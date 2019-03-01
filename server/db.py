from mongoengine import *
connect(db='quick-entry', host='mongodb://admin:tu3f1718076@ds155825.mlab.com:55825/quick-entry')

class Room(Document):
    name = StringField(required=True)
    roomnumber = IntField(required=True, unique=True)
    capacity = IntField(required=True)
    entrylist = ListField(ReferenceField('User'))


class User(Document):
    username = StringField(required=True, unique=True)
    fullname = StringField(required=True)
    email = StringField(required=True)
    password = StringField(required=True)
    tecid = StringField(required=True, unique=True)
    history = ListField(ReferenceField(Room))


class Admin(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    fname = StringField(required=True)
    rooms = ListField(ReferenceField(Room, reverse_delete_rule=CASCADE))