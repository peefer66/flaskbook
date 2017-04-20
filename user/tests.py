#  /flaskbook/user/tests.py
#  get the db that the system is using

from application import create_app as create_app_base
from mongoengine.connection import _get_db
from flask import session
import unittest

from user.models import User

class UserTest(unittest.TestCase):
    # 1. flaskbook_test db created ==> create a seperate db from the real one
    # 2. instance of the app created
    # 3. run tests
    # 4. destroy the database => tearDown
    def create_app(self):
        # Create a sub instance of the application using the factory method that is
        # the creat_app
    
        #  create an instance of the database that will later be destroyed
        self.db_name = 'flaskbook_test'
        return create_app_base(
            MONGODB_SETTINGS={'DB': self.db_name},
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY='my_secret_key'
            )
        
    def setUp(self):
        #  create the app
        self.app_factory = self.create_app() #  calls the create_app method
        self.app = self.app_factory.test_client() #  Enable GET and POST requests

    def tearDown(self):
        db = _get_db()
        db.connection.drop_database(db)
     
     # This returns a dictionary of the user fields and will be called from 
     # a number of test. No code repartion
    def user_dict(self):
        return dict(
            first_name="Peter",
            last_name="Fieldhouse",
            username="peefer",
            email="peefer66@hotmail.com",
            password="test123",
            confirm="test123"
            )
        
     # TEST METHODS
     # For python each test has to begin with test_testname()
        
    def test_register_user(self):
        # basic registration
        rv = self.app.post('/register', data=self.user_dict(), follow_redirects=True)  #    Good practice to allow redirects
        # Check the result of the test in this case that the database now contains
        # the record for 'Peter. There shoul be one ionstance of user
        assert User.objects.filter(username=self.user_dict()['username']).count() == 1
       
        # Test for invalid username characters
        #  Create a second user with different credentials
        user2 = self.user_dict()
        user2['username'] = 'Test Test'
        user2['email'] = 'test@example.com'
        rv = self.app.post('/register', data=user2, follow_redirects=True)
        assert 'Invalid username' in str(rv.data)
        
        # Test for lower case
        user3 = self.user_dict()
        user3['username'] = 'test'
        user3['email'] = 'TEST@example.com'
        rv = self.app.post('/register', data=user3, follow_redirects=True)
        # test the database to find the lowercase username should find 1 instance
        #assert User.objects.filter(username=user3['username'].lower()).count() == 1
        assert User.objects.filter(email=user3['email'].lower()).count() == 1
        
        # Test for confirmation email
        user = User.objects.get(username=self.user_dict()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert 'Your email has been confirmed' in str(rv.data)
        
        # Try agsin to confirm
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert rv.status_code == 404
        
        # Check change configuration is empty
        user = User.objects.get(username=self.user_dict()['username'])
        assert user.change_configuration == {}
        

        
    def test_login(self):
        # Create the user - remember the database will be blank at thi point
        self.app.post('/register', data=self.user_dict())
        # login
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password']
            ))
        # Test for the session is set
        # not too sure what this with statement is for
        with self.app as c:
            rv = c.get('/')
            assert session.get('username')== self.user_dict()['username']
            
    def test_edit_profile(self):
        #  Craete a user
        self.app.post('/register', data=self.user_dict())
        
        # Confirm the user
        user = User.objects.get(username=self.user_dict()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        
        
        
        # login the user
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password']
            ))
        # Check that the user has a edit button on his profile page
        rv = self.app.get('/' + self.user_dict()['username'])
        assert 'Edit profile' in str(rv.data)
        
        #  Edit the fields
        user = self.user_dict()
        user['first_name'] = 'Firstname'
        user['last_name'] = 'Lastname'
        user['username'] = 'Testusername'
        
        # check new email is in change configuration
        user['email'] = "test@example.com"
        rv = self.app.post('/edit', data=user)
        assert "You will need to confirm the new email to complete this change" in str(rv.data)
        db_user = User.objects.first()
        code = db_user.change_configuration.get('confirmation_code')
        new_email = db_user.change_configuration.get('new_email')
        assert new_email == user['email']
        
        # Now confirm
        rv = self.app.get('/confirm/' + db_user.username + '/' + code)
        db_user = User.objects.first()
        assert db_user.email == user['email']
        assert db_user.change_configuration == {}
        
        
        # Edit the user -- post
        rv = self.app.post('/edit', data=user)
        assert 'Profile updated' in str(rv.data)
        
        # grab the data from the database since there will only be one result
        # grab that info
        edited_user = User.objects.first()
        assert edited_user.first_name == 'Firstname'
        assert edited_user.last_name == 'Lastname'
        assert edited_user.username == 'testusername'  # lower case so also test for change to LC
        assert edited_user.email == 'test@example.com' # lower case
        
         # create a second user
        self.app.post('/register', data=self.user_dict())
        # login the user
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password']
            ))
        
        
        # try to save same email
        user = self.user_dict()
        user['email'] = "test@example.com"
        rv = self.app.post('/edit', data=user)
        assert "email already exists" in str(rv.data)

        # try to save same username
        user = self.user_dict()
        user['username'] = "TestUsername"
        rv = self.app.post('/edit', data=user)
        assert "Username already exists" in str(rv.data) 
        
    def test_get_profile(self):
        # create a user
        self.app.post('/register', data=self.user_dict())
        
        # get the user's profile
        rv = self.app.get('/' + self.user_dict()['username'])
        assert self.user_dict()['username'] in str(rv.data)
        
        # get a 404
        rv = self.app.get('/noexist')
        assert rv.status_code == 404
        
    def test_forgot_password(self):
        # Create a user
        self.app.post('/register', data=self.user_dict())
        # Confirm the user
        user = User.objects.get(username=self.user_dict()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        
        # Entert user forgot email
        rv = self.app.post('/forgot', data=dict(email=self.user_dict().get('email')))
        user = User.objects.first()
        password_reset_code = user.change_configuration.get('password_reset_code')
        assert password_reset_code is not None
        
        # try wrong username
        rv = self.app.get('/password_reset/not_there/' + password_reset_code)
        assert rv.status_code == 404
        
        # try wrong password reset code
        rv = self.app.get('/password_reset/' + self.user_dict().get('username') + '/bad-code')
        assert rv.status_code == 404
        
        # do right password reset code
        rv = self.app.post('/password_reset/' +self.user_dict().get('username') + '/' + password_reset_code, 
        data=dict(password='newpassword', confirm='newpassword'), follow_redirects=True)
        assert "Your password has been updated" in str(rv.data)
        user = User.objects.first()
        assert user.change_configuration == {}
        
        # try logging in with new password
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password='newpassword'
            ))
        # check the session is set
        with self.app as c:
            rv = c.get('/')
            assert session.get('username') == self.user_dict()['username']