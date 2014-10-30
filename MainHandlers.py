import cgi
import webapp2
import os
import DomainModel
import json

from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images


# This class is a request handler for the Main Page.
class MainPage(webapp2.RequestHandler) :
	def get(self) :
		template_values = dict()
		path = 'templates/index.html'
		render_template(self, template_values, path)

class UserAuth(webapp2.RequestHandler):

	def get(self) :
		user = users.get_current_user()
		query = ndb.gql("SELECT * FROM Account WHERE user_id = :1", user.user_id())
		if query.count() == 0 :
			account = DomainModel.Account()
			account.user_id = user.user_id()
			account.user_email = user.email()
			account.put()
		self.redirect('/')

class GetProfile(webapp2.RequestHandler):

	def post(self) :
		user = users.get_current_user()
		query = ndb.gql("SELECT * FROM Account WHERE user_id = :1", user.user_id())
		account = query.get()
		json_account_object = {'email': user.email() }
		self.response.headers['Content-Type'] = 'application/json' 
		self.response.write(json.dumps(json_account_object))

class SubmitPage(webapp2.RequestHandler) :
	def get(self) :
		upload_url = blobstore.create_upload_url('/recipes/upload')
		template_values = {'uploadURL': upload_url}
		path = 'templates/recipe-submission.html'
		render_template(self, template_values, path)

class SearchHandler(webapp2.RequestHandler) :
	def post(self) :

		search_query = self.request.get('searchInput')
		search_results = []
		search_words = search_query.split(" ")
		for word in search_words :
			query = DomainModel.Search.query(DomainModel.Search.keyWord == word)
			search_results = search_results + query.fetch()

		recipes = []
		for thing in search_results :
			for key_num in thing.recipeKeys :
				recipes.append(key_num.get())

		recipe_titles = []
		image_urls = []
		for recipe in recipes :
			recipe_titles.append((recipe.title, recipe.title.replace(" ", "_")))
			if recipe.image is None :
				image_urls.append('../img/defaultImage.jpg')
			else :
				image_urls.append(images.get_serving_url(recipe.image, size=None, crop=False, secure_url=True))

		zipped = zip(recipe_titles, image_urls)

		template_values = {
		  'recipes' : recipe_titles,
		  'image_urls' : image_urls,
		  'zipped' : zipped,
		  'search_query': search_query
		}
		path = 'templates/search-results.html'
		render_template(self, template_values, path)

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
		login = users.create_login_url('/authorize')
	default_values = {
		'login_link': login,
		'logout_link': logout,
		'nav_bar' : getNavBar(),
		'user' : user_email
	}
	temp_values= dict(template_values.items() + default_values.items())

	self.response.out.write(template.render(os.path.join(os.path.dirname(__file__),path), temp_values))

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/recipe-submit', SubmitPage),
  ('/search', SearchHandler),
  ('/authorize', UserAuth),
  ('/profile', GetProfile)
], debug=True)
