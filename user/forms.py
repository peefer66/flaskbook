from flask_wtf import Form # documents => http://wtforms.readthedocs.io/en/latest/index.html
from wtforms import validators, StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import ValidationError
from wtforms.widgets import TextArea
import re

#  Seperate the application level packages from the python level packages
from user.models import User

#  Create a BaseUserForm class so that the same field can be inherited by other
#  form classes. The password will be handled in a seperate class to handle forgotten
# passwords and standard change oif password
class BaseUserForm(Form):
    first_name = StringField('First Name',[validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])
    email = EmailField('Email Address', [
        validators.DataRequired(),
        validators.Email()
        ])
    username = StringField('Username', [
        validators.DataRequired(),
        validators.length(min=4, max=25)
        ])
    bio = StringField('Bio',
    widget = TextArea(),
    validators = [validators.length(max=160)]
    )
 

class PasswordBaseForm(Form):  
    #  .EqualTo = The password and the confirm password fields must match
    #  if not then pass message
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.length(min=4, max=80)
        ])
    confirm = PasswordField('Repeat Password')

#  Register form that inherits the names username emai etc from the BaseUserForm 
#  and inherits fro the PasswordBaseForm
class RegisterForm(PasswordBaseForm, BaseUserForm):
    #  In order to provide custom validation for a single field without
    #  needing to write a one-time-use validator, validation can be defined
    #  inline by defining a method with the convention validate_fieldname:
    #  Then becomes part of the validators.required
    
    #  These are 
    #  Chck if the username already exists. If it does raise error and message
    #  The form passes the data from the fields. The data is then compared with
    #  the information already in the database, just finding the first record
    def validate_username(form, field):
        if User.objects.filter(username=field.data).first():
            raise ValidationError("Username already exists")
            # Use regular expressions to validate username
            # for acceptable characters and length
        if not re.match("^[a-zA-Z0-9_-]{4,25}$", field.data):
            raise ValidationError('Invalid username')
        
            
    def validate_email(form, field):
        if User.objects.filter(email=field.data).first():
            raise ValidationError("Email is already in use")

# User login.html
# Two fields username and password
class LoginForm(Form):
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=4, max=25)
        ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=4, max=80)
        ])
 
 #  The edit form will just be a replica of the registration form
 #  so can just put a pass in the code
class EditForm(BaseUserForm):
    pass
    

# If the user has forgotten their password
# does not inherit from BaseUserForm
class ForgotForm(Form):
    email = EmailField('email', [
        validators.DataRequired(),
        validators.Email()
        ])

# If the user is just changing their password as part of a profile edit
# Then confirmation is done using their current password. Inherited from
# PasswordBaseForm
class PasswordResetForm(PasswordBaseForm):
    current_password = PasswordField('Current password', [
        validators.DataRequired(),
        validators.Email(),
        validators.Length(min=4, max=80)
        ])
        