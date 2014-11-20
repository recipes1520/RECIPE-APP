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


# This class is a request handler for the Main Page.
class MainPage(webapp2.RequestHandler) :
	def get(self) :
		featuredRecipes = self.getFeatured()
		template_values = {"featuredRecipes" : featuredRecipes}
		path = 'templates/index.html'
		render_template(self, template_values, path)
	def getFeatured(self) :
		return DomainModel.Recipe.query().fetch(5)



class SubmitPage(webapp2.RequestHandler) :
	def get(self) :
		if not users.get_current_user():
			render_template(self, {}, 'templates/login-required.html')
			return
		upload_url = blobstore.create_upload_url('/recipes/upload')
		template_values = {'uploadURL': upload_url}
		path = 'templates/recipe-submission.html'
		render_template(self, template_values, path)

class UserAuth(webapp2.RequestHandler):

	def get(self) :
		user = users.get_current_user()
		query = ndb.gql("SELECT * FROM Account WHERE user_id = :1", user.user_id())
		if query.count() == 0 :
			self.redirect('/recipe-submit')
			account = DomainModel.Account()
			account.user_id = user.user_id()
			account.user_email = user.email()
			account.put()
		self.redirect('/')

class SearchHandler(webapp2.RequestHandler) :
	def post(self) :

		search_query = self.request.get('searchInput')
		search_results = []
		search_words = search_query.split(" ")
		for word in search_words :
			query = DomainModel.Search.query(DomainModel.Search.keyWord == word.lower())
			search_results = search_results + query.fetch()

		recipes = []
		for thing in search_results :
			for key_num in thing.recipeKeys :
				recipes.append(key_num.get())

		recipe_titles = []
		image_urls = []
		for recipe in recipes :
			recipe_titles.append((recipe.title, recipe.title.replace(" ", "_")))
			if recipe.image == None :
				image_urls.append('../img/defaultImage.jpg')
			else :
				image_urls.append(images.get_serving_url(recipe.image, size=None, crop=False, secure_url=True))

		everythingZipped = zip(recipe_titles, image_urls)
		setZip = set(everythingZipped)
		zipped = []
		zipped = setZip

		template_values = {
		  'recipes' : recipe_titles,
		  'image_urls' : image_urls,
		  'zipped' : zipped,
		  'search_query': search_query
		}
		path = 'templates/search-results.html'
		render_template(self, template_values, path)
class RecipeLister(webapp2.RequestHandler):
	def get(self):
		query = DomainModel.Recipe.query(DomainModel.Recipe.user_author == str(users.get_current_user()))
		recipes = query.fetch()
		titles = []
		for thing in recipes :
			titles.append(thing.title)
		object = {}
		object['titles'] = titles

		self.response.write(json.dumps(object))


class ShoplistHandler(webapp2.RequestHandler):
  def get(self):
	list_objects = self.getShoppingList()
	json_return_object = {}
	items = []
	for item in list_objects :
		items.append(item.item)
	json_return_object['shoppingList'] = items

	self.response.write(json.dumps(json_return_object))

  def post(self):
	action = cgi.escape(self.request.get('action'))
	shoplist_item = cgi.escape(self.request.get('shopitem'))

	if action == 'add':
	  self.storeShoppingList(shoplist_item)
	  shopping_list_item_json = {'item' : shoplist_item, 'action': action }
	elif action == 'clear':
	  self.deleteShoppingList()
	  shopping_list_item_json = {'action': action }

	self.response.headers['Content-Type'] = 'application/json'
	self.response.write(json.dumps(shopping_list_item_json))

  def storeShoppingList(self, shopping_item):
	user = users.get_current_user()

	shoplist = DomainModel.Shoplist()
	shoplist.item = shopping_item
	shoplist.user_id = user.user_id()
	shoplist.put()
  
  def getShoppingList(self):
	user = users.get_current_user()

	query = DomainModel.Shoplist.query(DomainModel.Shoplist.user_id == user.user_id())

	return query.fetch()
  
  def deleteShoppingList(self):
	user = users.get_current_user()
	query = DomainModel.Shoplist.query(DomainModel.Shoplist.user_id == user.user_id())
	ndb.delete_multi(query.fetch(keys_only=True))

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
  ('/shoplist', ShoplistHandler),
  ('/recipelist', RecipeLister),
  ('/authorize', UserAuth)
], debug=True)
