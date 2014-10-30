import cgi
import webapp2
import os
import json
import DomainModel
import ShoplistModel

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

class SubmitPage(webapp2.RequestHandler) :
	def get(self) :
		upload_url = blobstore.create_upload_url('/recipes/upload')
		template_values = {'uploadURL': upload_url}
		path = 'templates/recipe-submission.html'
		render_template(self, template_values, path)



class SearchHandler(webapp2.RequestHandler) :
	def post(self) :

		search_query = self.request.get('searchInput')
		query = DomainModel.Recipe.query(ancestor=get_key()).order(
				-DomainModel.Recipe.title)
		recipes = query.fetch()

		recipe_titles = []
		image_urls = []
		for recipe in recipes :
			recipe_titles.append((recipe.title, recipe.title.replace(" ", "_")))
			if recipe.image == None :
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
                
class ShoplistHandler(webapp2.RequestHandler):
  def get(self):
    
    template_values = {
      'shopping_list': self.getShoppingList()
    }
    path = 'templates/shoplist.html'
    
    render_template(self, template_values, path)
    
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
    
    shoplist = ShoplistModel.Shoplist()
    shoplist.item = shopping_item
    shoplist.user_id = user.user_id()
    shoplist.put()
  
  def getShoppingList(self):
    user = users.get_current_user()
    
    query = ShoplistModel.Shoplist.query(ShoplistModel.Shoplist.user_id == user.user_id())
    
    return query.fetch()
  
  def deleteShoppingList(self):
    user = users.get_current_user()
    query = ShoplistModel.Shoplist.query(ShoplistModel.Shoplist.user_id == user.user_id())
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
  ('/', MainPage),
  ('/recipe-submit', SubmitPage),
  ('/search', SearchHandler),
  ('/shoplist', ShoplistHandler)
], debug=True)
