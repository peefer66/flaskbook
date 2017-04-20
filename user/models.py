from mongoengine import signals

from application import db
from utilities.common import utc_now_ts as now

#  Creaet an instance of User using mongodb documents (like a table)
class User(db.Document):
    
    #  db_field='u' the first character of the field name => saves space in large
    #  databases
    username = db.StringField(db_field='u', required=True, unique=True)
    password = db.StringField(db_field='p', required=True)
    email = db.StringField(db_field='e', required=True, unique=True)
    first_name = db.StringField(db_field='fn', max_length=50)
    last_name = db.StringField(db_field='ln', max_length=50)
    
    #  create a time stamp(NB NOT a date because a time stampe cn give more 
    #  information). Use a helper function 
    created = db.IntField(db_field='c', default=now())
    bio = db.StringField(db_field='b', max_length=160)
    
    #  Confirm email. Usually after registration the email of the account is verified
    email_confirmed = db.BooleanField(db_field='ecf', default=False)
    
    # A dictionary object in json format that will store the old and new email
    # when the email is changing. In a transition phase
    change_configuration = db.DictField(db_field='cc')
    #  Add the indexes by using the meta properties of the class. Give a string
    #  of the indexes. The minus created means that the sort order is reversed
    meta = {
        'indexes':['username', 'email', '-created']
    }
    
    # The @classmethod will be called prior to the save to the database
    # so can make any adjustments here ie change fields to lower case
    #  pre_save is a mongo method
    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.username = document.username.lower()
        document.email = document.email.lower()
    
signals.pre_save.connect(User.pre_save, sender=User)