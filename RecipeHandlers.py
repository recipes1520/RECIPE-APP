import cgi
import webapp2
import os
import json
import DomainModel

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images

class CommentSection(webapp2.RequestHandler) :
	def get(self):
		render_template(self, {}, 'templates/permission-denied.html')

	def post(self) :
		user = users.get_current_user()
		if user == None :
			self.response.out.write(json.dumps({"userStatus": "false"}))
		else :
			try :
				input_recipe = str(cgi.escape(self.request.get('recipeTitle')))
				input_author = str(user)
				input_rating = int(cgi.escape(self.request.get('rating')))
				input_comments = str(cgi.escape(self.request.get('comments')))
				tup = self.store_comment(input_recipe, input_author, input_rating,
							   input_comments)
				
				self.response.headers['Content-Type'] = 'application/json' 
				self.update_user_info(tup[0])
				json_comment_object = {'author': input_author, 'rating': input_rating, 'commentText': input_comments, 'avgRating': round(tup[1],1), "userStatus": "true"}

				self.response.write(json.dumps(json_comment_object))
			except(TypeError, ValueError):
				self.response.out.write('<html><body>Invalid input</body></html>')

	def store_comment(self, input_recipe, input_author, input_rating,
					  input_comments) :
		comment = DomainModel.ReviewSubmission(parent=get_key())
		comment.recipe_name = input_recipe
		comment.author = input_author
		comment.rating = input_rating
		comment.comment = input_comments
		avg_rating = self.update_recipe_comment_section(input_recipe, comment)
		comment_key = comment.put()
		return (comment_key, avg_rating)

	def update_recipe_comment_section(self, recipe_name, comment) :	
		query = DomainModel.Recipe.query(DomainModel.Recipe.title == recipe_name )	
		recipe = query.fetch()[0]
		recipe.comment_section.append(comment)
		recipe.total_rating_points += comment.rating
		recipe.avg_rating = float(recipe.total_rating_points)/len(recipe.comment_section)
		recipe.put()
		return recipe.avg_rating

	def update_user_info(self, comment_key) :	
		user = users.get_current_user()
		query = ndb.gql("SELECT * FROM Account WHERE user_id = :1", user.user_id())
		account = query.get()
		if account :
			account.user_reviews.append(comment_key)
			account.put()

class UploadRecipe(blobstore_handlers.BlobstoreUploadHandler):
	def get(self):
		render_template(self, {}, 'templates/permission-denied.html')
		
	def post(self):
		#this is for image storing
		img = self.get_uploads('file')
		recipe = DomainModel.Recipe(parent=get_key())
		if len(img) == 0 :
			recipe.image = None
		else :
			recipe.image = img[0].key()
		
		#all this is for ndb store of recipe text
		recipeTitle = str(cgi.escape(self.request.get('recipe_title')))
		recipe.title = recipeTitle
		recipe.user_author= str(users.get_current_user())
		#this is a list of ingredients
		ingredientList = self.getIngredients()
		recipe.ingredients = ingredientList
		recipe.instructions = self.getInstructions()
		recipe.description = str(cgi.escape(self.request.get('description')))
		recipe.prep_time_est = str(cgi.escape(self.request.get('prep_time'))) #PREP TIME ONLY.  WILL UPDATE WITH + COOK
		recipe.cook_time_est = str(cgi.escape(self.request.get('cook_time')))

		#this will store our recipe as a recipe Model and returns its specific key for search
		key = recipe.put()

		#we need to tokenize recipe name
		name_list = recipeTitle.split(" ")
		self.create_search(name_list, key)

		#making ingredients searchable
		ingredient_list = self.request.get_all('ingredients')
		split_ingredients = []
		for item in ingredient_list :
			split_ingredients = split_ingredients + item.split(" ")
		self.create_search(split_ingredients, key)

		self.redirect('/recipe-submit')

	def create_search(self, names, key) :
		for item in names :
			word = item.lower()
			query = DomainModel.Search.query(DomainModel.Search.keyWord == word)
			searchEntry = query.fetch()
			if len(searchEntry) > 0 :
				keyList = searchEntry[0].recipeKeys
				keyList.append(key)
				searchEntry[0].recipeKeys = keyList
				searchEntry[0].put()
			else :
				searchEntry = DomainModel.Search()
				searchEntry.keyWord = word
				keyList = []
				keyList.append(key)
				searchEntry.recipeKeys = keyList
				searchEntry.put()

	def getIngredients(self) :
		ingredients = self.request.get_all('ingredients')
		quantities = self.request.get_all('quantities')
		units = self.request.get_all('units')

		list = []
		for ing in zip(ingredients, quantities, units) :
			list.append( ing[1] + " " + ing[2] + "_" + ing[0] )

		return list

	def getInstructions(self) :
		instructions = self.request.get_all('instructions')

		list = []
		for instruction in instructions :
			list.append(instruction)
		return list

class RecipeDisplay(webapp2.RequestHandler) :
	def get(self, recipe_name) :

		recipe_name = recipe_name.replace("_"," ")
		query = DomainModel.Recipe.query(DomainModel.Recipe.title == recipe_name)
		
		if query.count() == 0:
			render_template(self, {}, 'templates/404-error-page.html')
			return
		recipe = query.fetch()[0]

		#will load a default image if none provided.
		if recipe.image == None :
			imgURL = '../img/defaultImage.jpg'
		else :
			imgURL = images.get_serving_url(recipe.image, size=None, crop=False, secure_url=True)
		template_values = {
		  'recipe' : recipe,
		  'imgURL' : imgURL,
		  'reviews' : recipe.comment_section
		}
		path = "templates/recipe-display.html"
		render_template(self, template_values, path)
	def post(self, args):
		self.redirect('/')

def get_key() :
	return ndb.Key('recipe_name', 'author')

def getNavBar():
	navBarTitles = ['Submit Recipe', 'Featured', 'About']
	navBarLinks = ['/recipe-submit', '/recipes/Godly_Pumpkin_Mash', '#']
	return zip(navBarLinks, navBarTitles)

def render_template(self, template_values, path):
	user = users.get_current_user()
	login = ''
	logout = ''
	user_email = ''
	if user :
		logout = users.create_logout_url('/')
		user_email = user.email()
	else :
		login = users.create_login_url('/')
	default_values = {
		'login_link': login,
		'logout_link': logout,
		'nav_bar' : getNavBar(),
		'user' : user_email
	}
	temp_values= dict(template_values.items() + default_values.items())

	self.response.out.write(template.render(os.path.join(os.path.dirname(__file__),path), temp_values))


app = webapp2.WSGIApplication([
  ('/recipes/submit_comment', CommentSection),
  ('/recipes/upload', UploadRecipe),
  ('/recipes/(.*)', RecipeDisplay),
], debug=True)