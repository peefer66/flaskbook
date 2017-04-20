from flask import Blueprint, render_template, redirect, request, session, url_for, abort
import bcrypt
# UUID values are 128 bits long and “can guarantee uniqueness across space
# and time”. They are useful for identifiers for documents, hosts, application
# clients, and other situations where a unique value is necessary. 
# The RFC is specifically geared toward creating a Uniform Resource Name namespace.
import uuid # universal unique identifier

from user.forms import RegisterForm, LoginForm, EditForm, ForgotForm, PasswordResetForm
from user.models import User
from utilities.common import email



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
   if form.validate_on_submit():#  ie passes validation
       # generate a salt (password generation key)
       salt = bcrypt.gensalt()
       # encrypt the password using the salt key
       hashed_password = bcrypt.hashpw(form.password.data, salt)
       # Create a unique identifier to store in the change_configuration field
       code = str(uuid.uuid4())
       # Create the user object
       user = User(
           username=form.username.data,
           password=hashed_password,
           email=form.email.data,
           first_name=form.first_name.data,
           last_name=form.last_name.data,
           bio=form.bio.data,
           change_configuration={"new_email": form.email.data.lower(),"confirmation_code": code})
        # Email verification to the user
       body_html = render_template('mail/user/register.html', user=user)
       body_text = render_template('mail/user/register.txt', user=user)
        
       email(user.email, 'Welcome to Flaskbook', body_html, body_text)
        
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
    
@user_app.route('/<username>', methods=('GET', 'POST'))
def profile(username):
    #  first set edit profile flag to false
    edit_profile = False
    # find the user and pass to the profile html
    user = User.objects.filter(username=username).first()
    
    # If the session of that username exists and the current user is that
    # username then they are looking at their own profile
    if session.get('username') and user.username==session.get('username'):
        # set the edit-profile to true
        edit_profile = True
    # if the user was found    
    if user:
        #  return the user/profile.html and pass the edit_profile flag
        # It will be false if looking at somebody elses profile
        # True if looking at own
        return render_template('user/profile.html', user=user, edit_profile=edit_profile)
    #  The user doesnt exist
    else:
        abort(404)
        
@user_app.route('/edit', methods=('GET', 'POST'))
def edit():
    error = None
    message = None 
    user = User.objects.filter(username=session.get('username')).first()
    
    #  If the user was found
    if user:
        #  obj=user is wtfform special usage thta prfills the form with user object
        form = EditForm(obj=user)
        if form.validate_on_submit():
            #  Check to see if username is changing
            # also the case may have changes so potetially give a false positive
            # therefore set username lower case.
            if user.username != form.username.data.lower():
            # Check to see if username already exists
                if User.objects.filter(username = form.username.data.lower()).first():
                    error = 'Username already exists'
                else:
                    # set the session to that of the username(lowercase)
                    session['username'] = form.username.data.lower()
                    #  set the username in the form to lowercase
                    form.username.data = form.username.data.lower()
            
            # Check if the email has chanmged
            if user.email != form.email.data:
                # The email has changed but check that it doesnt already exist
                if User.objects.filter(email=form.email.data.lower()).first():
                    error = 'email already exists'
                else:
                    # email has changed but does not already exist
                    # sent verification email
                    code = str(uuid.uuid4())
                    user.change_configuration = {
                        'new_email':form.email.data.lower(),
                        'confirmation_code':code
                    }
                    
                    #set the email confirmation to false
                    user.email_confirmed = False
                    # Change the form email to the old email otherwise the new email
                    # will be changed without the confirmation
                    form.email.data = user.email
                    message = 'You will need to confirm the new email to complete this change'
                    
                    # Email the user
                    body_html = render_template('mail/user/change_email.html', user=user)
                    body_text = render_template('mail/user/change_email.txt', user=user)
                    email(user.change_configuration['new_email'], 'Confirm your new email', body_html, body_text)
        
                    
                    
            #  If there are no errors Populate the user object with the new info
            if not error:
                # use a WTForm specuial usage to populate the user obj and
                # save (rather UPDATE) to DB
                form.populate_obj(user)
                user.save()
                # The new email has been confirmed
                if not message:
                    message = 'Profile updated'
        return render_template('user/edit.html', form=form, error=error, message=message)
    else:
        # No user found
        abort(404)
        
@user_app.route('/confirm/<username>/<code>', methods=('GET', 'POST'))
def confirm(username, code):
    #  See if user exists. Remember username is unique
    user = User.objects.filter(username=username).first()
    # if the user exists and the change cofiguration is true and has a change 
    # configuration code email return address to confirm user registration
    if user and user.change_configuration and user.change_configuration.get('confirmation_code'):
        if code == user.change_configuration.get('confirmation_code'):
            user.email =  user.change_configuration.get('new_email')
            user.change_configuration = {}
            user.email_confirmed = True
            user.save()
            return render_template('user/email_confirmed.html')
    else:
        # one or all criteria was faulse
        abort(404)


@user_app.route('/forgot', methods=('GET', 'POST'))
def forgot():
    error = None
    message = None
    form = ForgotForm()
    
    if form.validate_on_submit():
        user = User.objects.filter(email=form.email.data.lower()).first()
        if user:
            # create validation code
            code = str(uuid.uuid4())
            user.change_configuration={'password_reset_code':code}
            user.save()
    
            # email the user
            body_html = render_template('mail/user/password_reset.html', user=user)
            body_text = render_template('mail/user/password_reset.txt', user=user)
            email(user.email, 'Password reset request', body_html, body_text)
            message = 'You will recieve a password reset email if we find the email in our system'
            
    return render_template('user/forgot.html', form=form, error=error, message=message)
    
@user_app.route('/password_reset/<username>/<code>', methods=('GET', 'POST'))
def password_reset(username, code):
    form = PasswordResetForm()
    message = None
    require_current = None
    
    
    user = User.objects.filter(username=username).first()
    # if the user dont exist or the reset code is wrong
    if not user or code != user.change_configuration.get('password_reset_code'):
        abort(404)
    # Bipass the form validation to be able to delete the current password 
    # without throwing the form validation.datarequired wich would throw an error
    if request.method == 'POST':
        del form.current_password
        # Now we can validate
        if form.validate_on_submit():
            # create a salt
            salt = bcrypt.gensalt()
            # create hashed password passing the new password and the salt
            hashed_password = bcrypt.hashpw(form.password.data, salt)
            # Change the users password to the hashed password
            user.password = hashed_password
            # Change the change_configuration to a empty dict
            user.change_configuration = {}
            user.save()
            # Check to see if the user session exists and delete
            if session('username'):
                session.pop('username')
            return redirect(url_for('user_app.password_reset_complete'))
        
    # If not POST
    return render_template('user/password_reset.html',
        form=form,
        message=message,
        require_current=require_current,
        code=code
    )


@user_app.route('/password_reset_complete')
def password_reset_complete():
    return render_template('user/password_change_confirmed.html')            
            