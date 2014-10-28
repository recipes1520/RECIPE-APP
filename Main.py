import cgi
import webapp2
import os
import urllib

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from google.appengine.api import search

# Creating datastorage for the user review submissions on review page
class ReviewSubmission(ndb.Model) :
	recipe_name = ndb.StringProperty(indexed=False)
	author = ndb.StringProperty(indexed=False)
	rating = ndb.IntegerProperty(indexed=False)
	comment = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=True)

def get_key() :
	return ndb.Key('recipe_name', 'author')

class Recipe(ndb.Model) :
	title = ndb.StringProperty()
	user_author = ndb.StringProperty()
	ingredients = ndb.StringProperty(repeated=True)
	description = ndb.TextProperty()
	instructions = ndb.StringProperty(repeated=True)
	prep_time_est = ndb.StringProperty()
	cook_time_est = ndb.StringProperty()
	image = ndb.BlobKeyProperty()
	comment_section = ndb.StructuredProperty(ReviewSubmission, repeated=True)

# This class is a request handler for the Main Page.
class MainPage(webapp2.RequestHandler) :
	def get(self) :
		template_values = dict()
		path = 'templates/index.html'
		render_template(self, template_values, path)

class ReviewPage(webapp2.RequestHandler) :
	def get(self) :
		self.render_reviews()

	def render_reviews(self) :
		query = ReviewSubmission.query(ancestor=get_key()).order(
				-ReviewSubmission.date)
		user_reviews = query.fetch()
		#unique to your template
		template_values = {
			'review_submit' : user_reviews,
		}
		path = 'templates/review-form.html'
		render_template(self, template_values, path)

class CommentSection(webapp2.RequestHandler) :
	def post(self) :
		try :
			input_recipe = str(cgi.escape(self.request.get('recipeTitle')))
			input_author = str(users.get_current_user())
			input_rating = int(cgi.escape(self.request.get('rating')))
			input_comments = str(cgi.escape(self.request.get('comments')))
			self.store_comment(input_recipe, input_author, input_rating,
						   input_comments)
			self.redirect("/recipes/" + input_recipe.replace(' ', '_'))
		except(TypeError, ValueError):
			self.response.out.write('<html><body>Invalid input</html></body')

	def store_comment(self, input_recipe, input_author, input_rating,
					  input_comments) :
		comment = ReviewSubmission(parent=get_key())
		comment.recipe_name = "Pickles"
		comment.author = input_author
		comment.rating = input_rating
		comment.comment = input_comments
		query = Recipe.query(Recipe.title == input_recipe )
		recipe = query.fetch()[0]
		recipe.comment_section.append(comment)
		recipe.put()
		comment.put()


class SubmitPage(webapp2.RequestHandler) :
	# implementing the get method here allows this class to handle GET requests.
	def get(self) :
		upload_url = blobstore.create_upload_url('/upload')
		template_values = {'uploadURL': upload_url}
		path = 'templates/recipe-submission.html'
		render_template(self, template_values, path)

class UploadRecipe(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		#this is for image storing
		pic = self.get_uploads('file')
		recipe = Recipe(parent=get_key())
		if len(pic) == 0 :
			recipe.image = None
		else :
			recipe.image = pic[0].key()
		#all this is for ndb store of recipe text
		recipe.title = str(cgi.escape(self.request.get('recipe_title')))
		recipe.user_author= str(users.get_current_user())
		recipe.ingredients = self.getIngredients()
		recipe.instructions = self.getInstructions()
		recipe.description = str(cgi.escape(self.request.get('description')))
		recipe.prep_time_est = str(cgi.escape(self.request.get('prep_time'))) #PREP TIME ONLY.  WILL UPDATE WITH + COOK
		recipe.cook_time_est = str(cgi.escape(self.request.get('cook_time')))
		recipe.put()

		self.redirect('/recipe-submit')

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

class SearchHandler(webapp2.RequestHandler) :
	def post(self) :

		search_query = self.request.get('searchInput')
		query = Recipe.query(ancestor=get_key()).order(
				-Recipe.title)
		recipes = query.fetch()

		recipe_titles = []
		image_urls = []
		for recipe in recipes :
			recipe_titles.append((recipe.title, recipe.title.replace(" ", "_")))
			if recipe.image == None :
				image_urls.append('../img/defaultImage.jpg')
			else :
				image_urls.append(images.get_serving_url(recipe.image, size=None, crop=False, secure_url=True))

		template_values = {
		  'recipes' : recipe_titles,
		  'image_urls' : image_urls,
		  'search_query': search_query
		}
		path = 'templates/search-results.html'
		render_template(self, template_values, path)

class RecipeDisplay(webapp2.RequestHandler) :
	def get(self, recipe_name) :

		recipe_name = recipe_name.replace("_"," ")
		query = Recipe.query(Recipe.title == recipe_name)
		q = query.fetch()

		recipe = q[0]
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

# we use this to set up the AppEngine app - each of the mappings identifies a
# URL and the webapp2.RequestHandler class that handles requests to that URL
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/review', ReviewPage),
  ('/recipe-submit', SubmitPage),
  ('/submit_comment', CommentSection),
  ('/search', SearchHandler),
  ('/recipes/(.*)', RecipeDisplay),
  ('/upload', UploadRecipe),
], debug=True)
