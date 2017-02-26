from flask import Blueprint, render_template, redirect, request, session, url_for
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
    # Require a method that if the login page is accwssed from anoher page
    # say the profile, then a re-direct back to the page of origin will be necessary
    # this is handled by the 'next' method
    
    # first check that the method accesing the login page was a GET and that
    # the GET request contains a next
    if request.method=='GET' and request.args.get('next'):
        # store that next in a session so that it can redirect back
        session['next'] = request.args.get('next')
        
        
    if form.validate_on_submit(): # Valid entry in the form
        #  Examine database to see if the user exists
        #  Find the first occurance because only unique usernames should be
        #  present
        user = User.objects.filter(username=form.username.data).first()
        #  If found
        if user:
            #  Check password is correct by comparing the hashed passwords
            if bcrypt.hashpw(form.password.data, user.password)==user.password:
                #  if a next session exists. A next session is created when 
                # the login is accessed from another page
                if 'next' in session:
                    # get that session url and store as next
                    next = session.get('next')
                    # delete the session[next] so that further redirects will not happen
                    session.pop('next')
                    # rediect back to the page of origin
                    return redirect(next)
                else:   
                    #  if there was no next 
                    #  set the session to the username and return to user logged in/user
                    session['username']=form.username.data
                    return 'User logged in'
            else:
                user = None
        #  Use 'if not user' here rather than else bc the user may be correct but the password not
        #  so with the user set to None the if statemment is correct
        if not user:
            error =  'Incorrect username / password'
        
    return render_template('user/login.html', form=form, error=error)
    
@user_app.route('/logout', methods=('GET', 'POST'))
def logout():
    # first delete session
    session.pop('username')
    # Redirect using the Blueprint
    return redirect(url_for('user_app.login'))
    
@user_app.route('/profile', methods=('GET', 'POST'))
def profile():
    return render_template(url_for('user/profile.html'))
   
    
