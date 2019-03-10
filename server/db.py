from mongoengine import *
connect(db='quick-entry', host='mongodb://admin:tu3f1718076@ds155825.mlab.com:55825/quick-entry')

class Room(Document):
    '''
    Room Model
    A basic model for storing rooms created by admins. 
    The entrylist property is a ListField containing a Reference to all the entries.
    '''
    name = StringField(required=True)
    roomnumber = IntField(required=True)
    capacity = IntField(required=True)
    current = IntField(default=0)
    entrylist = ListField(ReferenceField('Entry')) #String used, since Entry class is defined after Room


class User(Document):
    '''
    User Model
    Model for storing users/students and their information. 
    The tecid is used for identifying the user alongside the id that MongoDB provides.
    The history ListField holds references to all the rooms the user has entered into. 
    '''
    username = StringField(required=True, unique=True)
    fullname = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    tecid = StringField(required=True, unique=True)
    currentroom = ReferenceField(Room)
    history = ListField(ReferenceField('Entry'))


class Entry(Document):
    '''
    Entry Model
    Helps store entry specific data.
    '''
    user = ReferenceField(User)
    room = ReferenceField(Room)
    timestamp = LongField()
    exittime = LongField()

class Admin(Document):
    '''
    Admin Model
    Model for storing admin data.
    rooms is ListField which holds the references to all the rooms the admin has created so far.
    '''
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    fname = StringField(required=True)
    rooms = ListField(ReferenceField(Room, reverse_delete_rule=CASCADE))