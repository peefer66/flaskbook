from application import db
from utilities.common import utc_now_ts as now

#  Creaet an instance of User using mongodb documents (like a table)
class User(db.Document):
    
    #  db_field='u' the first character of the field name => saves space in large
    #  databases
    username = db.StringField(db_field='u', required=True)
    password = db.StringField(db_field='p', required=True)
    email = db.StringField(db_field='e', required=True)
    first_name = db.StringField(db_field='fn', max_length=50)
    last_name = db.StringField(db_field='ln', max_length=50)
    
    #  create a time stamp(NB NOT a date because a time stampe cn give more 
    #  information). Use a helper function 
    created = db.IntField(db_field='c', default=now())
    
    
    