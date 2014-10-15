# import the webapp2 module so we can get access to the framework
import cgi
import webapp2
import os

# import the db module from appengine
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

# import the users module from appengine
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


# we'll create a simple Model class here.
class PostName(ndb.Model) :
  # this model class has just one property - myname
  myname = ndb.StringProperty()

# This class is a request handler.
class MainPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
  def get(self) :

    template_values = {
      'login_btn': getLoginLink(),
      'logout_btn': getLogoutLink()
    }
    path = 'templates/index.html'
    self.response.out.write(template.render(path, template_values))

class ReviewPage(webapp2.RequestHandler) :
    def get(self) :
        self.render_reviews()
 #       self.print_reviews()

    def render_reviews(self) :
        query = ReviewSubmission.query(ancestor=get_key()).order(
                ReviewSubmission.date)
        user_reviews = query.fetch()
        template_values = {
            'review_submit' : user_reviews
        }
        path = 'templates/review-form.html'
        self.response.out.write(template.render(path, template_values))

class CommentSection(webapp2.RequestHandler) :
    def post(self) :
        try :
            input_recipe = str(cgi.escape(self.request.get('recipe')))
            input_author = str(cgi.escape(self.request.get('author')))
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


class LoginPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
  def get(self) :

    user = users.get_current_user()

    login = ''
    logout = ''

    if user:
      logout = users.create_logout_url('/')
    else:
      login = users.create_login_url('/')
   
    template_values = {
      'login': login,
      'logout': logout
    }
    path = 'templates/sign-in.html'
    self.response.out.write(template.render(path, template_values))

class ReviewPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
  def get(self) :
   
 
    template_values = {
      'login_btn': getLoginLink(),
      'logout_btn': getLogoutLink()
    }
    path = 'templates/review-form.html'
    self.response.out.write(template.render(path, template_values))

class SubmitPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
  def get(self) :

    template_values = {
      'login_btn': getLoginLink(),
      'logout_btn': getLogoutLink()
    }
    path = 'templates/recipe-submission.html'
    self.response.out.write(template.render(path, template_values))

    # This class is a request handler.
class RegisterPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
  def get(self) :
   
    template_values = {}
    path = 'templates/sign-up.html'
    self.response.out.write(template.render(path, template_values))

def getLoginLink():
  user = users.get_current_user()
  if not user:
    return users.create_login_url('/')
  else:
    return ''

def getLogoutLink():
  user = users.get_current_user()
  if user:
    return users.create_logout_url('/')
  else:
    return ''

# we use this to set up the AppEngine app - each of the mappings identifies a
# URL and the webapp2.RequestHandler class that handles requests to that URL
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/review', ReviewPage),
  ('/login', LoginPage),
  ('/register', RegisterPage),
  ('/recipe-submit', SubmitPage),
  ('/submit_comment', CommentSection)
], debug=True)
