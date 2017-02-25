#  /flaskbook/user/tests.py
#  get the db that the system is using

from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest

from user.models import User

class UserTest(unittest.TestCase):
    # 1. flaskbook_test db created
    # 2. instance of the app created
    # 3. run tests
    # 4. destroy the database
    def create_app(self):
        # Create a sub instance of the application using the factory method that is
        # the creat_app
    
        #  create an instance of the database that will later be destroyed
        self.db_name = 'flaskbook_test'
        return create_app_base(
            MONGODB_SETTINGS={'DB': self.db_name},
            TESTING=True,
            WTF_CSRF_ENABLED=False
            )
        
    def setUp(self):
        #  create the app
        self.app_factory = self.create_app() #  calls the create_app method
        self.app = self.app_factory.test_client() #  Enable GET and POST requests

    def tearDown(self):
        db = _get_db()
        db.connection.drop_database(db)
        
     # TEST METHODS
     # For python each test has to begin with test_testname()
        
    def test_register_user(self):
        # basic registration
        rv = self.app.post('/register', data=dict(
            first_name="Jorge",
            last_name="Escobar",
            username="jorge",
            email="jorge@example.com",
            password="test123",
            confirm="test123"
            ), follow_redirects=True)  #    Good practice to allow redirects
        # Check the result of the test in this case that the database now contains
        # the record for 'Peter. There shoul be one ionstance of user
        assert User.objects.filter(username='jorge').count() == 1

