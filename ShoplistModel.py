from google.appengine.ext import ndb

class Shoplist(ndb.Model) :
  item = ndb.StringProperty(indexed=False)
  user_id = ndb.StringProperty(indexed=True)