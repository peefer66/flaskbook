from flask import Flask
from flask.ext.mongoengine import MongoEngine

#  Create a global variable db
db = MongoEngine()

def create_app(**config_overrides):
    #  Create the app using the configs settings.py
    # The over-tides allows for the testing
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    #  However if overides are present then use these instead
    #  eg if testing (see user/tests.py)
    app.config.update(config_overrides)
    
    #  initialize the database in the app
    db.init_app(app)
    
    # import the user_app blueprint
    from user.views import user_app
    #  register the blueprint so that flask knows that it has been created
    #  and usable throughout
    
    #  When you bind a function with the help of the @user_app.route
    #  decorator the blueprint will record the intention of registering the
    #  function show on the application when it’s later registered.
    #  Additionally it will prefix the endpoint of the function with the 
    #  name of the blueprint which was given to the Blueprint constructor
    #  (in this case also user_app).
    
    app.register_blueprint(user_app)
    return app

