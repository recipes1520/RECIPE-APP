# import the webapp2 module so we can get access to the framework
import webapp2
import os


# import the db module from appengine
from google.appengine.ext import db
from google.appengine.ext.webapp import template

# we'll create a simple Model class here.
class PostName(db.Model) :  
  # this model class has just one property - myname
  myname = db.StringProperty()

# This class is a request handler.
class MainPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
  def get(self) :
   
    template_values = {}
    path = 'templates/index.html'
    self.response.out.write(template.render(path, template_values))


class LoginPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
  def get(self) :
    
    template_values = {}
    path = 'templates/sign-in.html'
    self.response.out.write(template.render(path, template_values))
    
class ReviewPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
  def get(self) :
   
 
    template_values = {}
    path = 'templates/review-form.html'
    self.response.out.write(template.render(path, template_values))
    
class SubmitPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
  def get(self) :
   
    template_values = {}
    path = 'templates/recipe-submission.html'
    self.response.out.write(template.render(path, template_values))
    
    # This class is a request handler.
class RegisterPage(webapp2.RequestHandler) :
  # implementing the get method here allows this class to handle GET requests.
  def get(self) :
   
    template_values = {}
    path = 'templates/sign-up.html'
    self.response.out.write(template.render(path, template_values))

    

# we use this to set up the AppEngine app - each of the mappings identifies a 
# URL and the webapp2.RequestHandler class that handles requests to that URL
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/review', ReviewPage),
  ('/login', LoginPage),
  ('/register', RegisterPage),
  ('/recipe-submit', SubmitPage)

], debug=True)