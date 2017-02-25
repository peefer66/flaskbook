from flask_wtf import Form # documents => http://wtforms.readthedocs.io/en/latest/index.html
from wtforms import validators, StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import ValidationError

#  Seperate the application level packages from the python level packages
from user.models import User


class RegisterForm(Form):
    first_name = StringField('First Name',[validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])
    email = EmailField('Email Address', [
        validators.DataRequired(),
        validators.email()
        ])
        
    username = StringField('Username', [
        validators.DataRequired(),
        validators.length(min=4, max=25)
        ])
    
    #  .EqualTo = The password and the confirm password fields must match
    #  if not then pass message
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.length(min=4, max=80)
        ])
    confirm = PasswordField('Repeat Password')
    
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
            
    def validate_email(form, field):
        if User.objects.filter(email=field.data).first():
            raise ValidationError("Email is already in use")

# User login.html
# Two fields username and password
class LoginForm(Form):
    username = StringField('Username', [
        validators.DataRequired(),
        validators.length(min=4, max=25)
        ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.length(min=4, max=80)
        ])
    

    
        