from flask import Blueprint

#  Flask uses a concept of blueprints for making application components
#  and supporting common patterns within an application or across applications.
#  Blueprints can greatly simplify how large applications work and provide
#  a central means for Flask extensions to register operations on applications.
#  A Blueprint object works similarly to a Flask application object,
#  but it is not actually an application. Rather it is a blueprint of how
#  to construct or extend an application.

user_app = Blueprint('user_app', __name__)

#  Access the routes via the blueprint using a decorator
@user_app.route('/login')
def login():
    return 'User login'
    
    
