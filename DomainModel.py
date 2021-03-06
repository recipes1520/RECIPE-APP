from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images


# Creating datastorage for the user review submissions on review page
class ReviewSubmission(ndb.Model) :
	recipe_name = ndb.StringProperty(indexed=False)
	author = ndb.StringProperty(indexed=False)
	rating = ndb.IntegerProperty(indexed=False)
	comment = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=True)

class Recipe(ndb.Model) :
	title = ndb.StringProperty()
	user_author = ndb.StringProperty()
	ingredients = ndb.StringProperty(repeated=True)
	description = ndb.TextProperty()
	instructions = ndb.StringProperty(repeated=True)
	prep_time_est = ndb.StringProperty()
	cook_time_est = ndb.StringProperty()
	total_rating_points = ndb.IntegerProperty(default=0)
	avg_rating = ndb.FloatProperty(default=0)
	image = ndb.BlobKeyProperty()
	comment_section = ndb.StructuredProperty(ReviewSubmission, repeated=True)

class Search(ndb.Model) :
	keyWord = ndb.StringProperty()
	recipeKeys = ndb.KeyProperty(repeated=True)

class Account(ndb.Model) :
	user_email = ndb.StringProperty()
	user_id = ndb.StringProperty()
	user_nickname = ndb.StringProperty()
	user_recipes = ndb.KeyProperty(repeated=True, kind=Recipe)
	user_reviews = ndb.KeyProperty(repeated=True, kind=ReviewSubmission)

class Shoplist(ndb.Model) :
  item = ndb.StringProperty(indexed=True)
  user_id = ndb.StringProperty(indexed=True)
  bought = ndb.BooleanProperty(default=False)