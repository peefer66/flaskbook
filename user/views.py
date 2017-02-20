from flask import Blueprint, render_template
import bcrypt

from user.forms import RegisterForm
from user.models import User



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

@user_app.route('/register', methods=('GET', 'POST'))
def register():
   form = RegisterForm()
   if form.validate_on_submit(): #  ie passes validation
       # generate a salt (password generation key)
       salt = bcrypt.gensalt()
       # encrypt the password using the salt key
       hashed_password = bcrypt.hashpw(form.password.data, salt)
       # Create the user object
       user = User(
           username=form.username.data,
           password=hashed_password,
           email=form.email.data,
           first_name=form.first_name.data,
           last_name=form.last_name.data
           )
          
       # save the user to the database
       user.save()
       return 'User registered'
       
   return render_template('user/register.html', form=form)
   
    
