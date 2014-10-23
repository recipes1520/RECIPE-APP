import cgi
import webapp2
import os

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import users

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
        template_values = {
            'review_submit' : user_reviews,
        }
        path = 'templates/review-form.html'
        render_template(self, template_values, path)

class CommentSection(webapp2.RequestHandler) :
    def post(self) :
        try :
            input_recipe = str(cgi.escape(self.request.get('recipe')))
            input_author = str(users.get_current_user())
            input_rating = int(cgi.escape(self.request.get('rating')))
            input_comments = str(cgi.escape(self.request.get('comments')))
            self.store_comment(input_recipe, input_author, input_rating,
                           input_comments)
            self.redirect('/review')
        except(TypeError, ValueError):
            self.response.out.write('<html><body>Invalid input</html></body')

    def store_comment(self, input_recipe, input_author, input_rating,
                      input_comments) :
        comment = ReviewSubmission(parent=get_key())
        comment.recipe_name = input_recipe
        comment.author = input_author
        comment.rating = input_rating
        comment.comment = input_comments
        comment.put()

class SubmitPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
	def get(self) :

		template_values = {}
		path = 'templates/recipe-submission.html'
		render_template(self, template_values, path)
	
	def post(self):
		recipe = Recipe(parent=get_key())
		
		recipe.title = str(cgi.escape(self.request.get('recipe_title')))
		recipe.user_author= str(users.get_current_user())		
		recipe.ingredients = self.getIngredients()	
		recipe.instruction = self.getInstructions()
		recipe.description = str(cgi.escape(self.request.get('description')))
		recipe.prep_time_est = str(cgi.escape(self.request.get('prep_time'))) #PREP TIME ONLY.  WILL UPDATE WITH + COOK
		recipe.cook_time_est = str(cgi.escape(self.request.get('cook_time')))
		recipe.genre = str(cgi.escape(self.request.get('category')))
		recipe.put()
		
		self.redirect('/recipe-submit')
		
	def getIngredients(self) :
		ingredients = self.request.get_all('ingredients')
		quantities = self.request.get_all('quantities')
		units = self.request.get_all('units')
		
		list = []
		for ing in zip(ingredients, quantities, units) :
			list.append( ing[1] + " " + ing[2] + " " + ing[0] )
		
		return list

	def getIngredients(self) :
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
		for recipe in recipes :
			recipe_titles.append((recipe.title, recipe.title.replace(" ", "_")))

		template_values = {
		  'recipes' : recipe_titles,
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
		template_values = {
		  'recipe' : recipe
		}
		path = "templates/recipe-display.html"
		render_template(self, template_values, path)

		
def getNavBar():
	navBarTitles = ['Home', 'Submit Recipe', 'Featured', 'About']
	navBarLinks = ['/', 'recipe-submit', '/review', '#']
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

	self.response.out.write(template.render(path, temp_values))

# we use this to set up the AppEngine app - each of the mappings identifies a
# URL and the webapp2.RequestHandler class that handles requests to that URL
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/review', ReviewPage),
  ('/recipe-submit', SubmitPage),
  ('/submit_comment', CommentSection),
  ('/search', SearchHandler),
  ('/recipes/(.*)', RecipeDisplay),
], debug=True)
