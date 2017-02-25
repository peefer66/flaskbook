from flask import Blueprint, render_template, redirect, request, session
import bcrypt

from user.forms import RegisterForm, LoginForm
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

@user_app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit(): # Valid entry in the form
        #  Examine database to see if the user exists
        #  Find the first occurance because only unique usernames should be
        #  present
        user = User.objects.filter(username=form.username.data).first()
        #  If found
        if user:
            #  Check password is correct by comparing the hashed passwords
            if bcrypt.hashpw(form.password.data, user.password)==user.password:
                #  set the session to the username
                session['username']=form.username.data
                return 'User logged in'
            else:
                user = None
        #  Use 'if not user' here rather than else bc the user may be correct but the password not
        #  so with the user set to None the if statemment is correct
        if not user:
            error =  'Incorrect username / password'
        
    return render_template('user/login.html', form=form, error=error)
   
    
