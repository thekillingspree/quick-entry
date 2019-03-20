from flask import Blueprint, request, jsonify, g
from mongoengine.errors import ValidationError, NotUniqueError
import bcrypt
import jwt
import json
import time
import re

from .middleware.login import user_login_required, user_is_authorized
from .db import User, Room, Entry
from .keys import SECRET

user_routes = Blueprint('user_routes', __name__)

def checkID(id):
    '''
    This function uses regex to check if the provided Terna ID No is valid.
    '''
    regex = r'^TU[A-Z]*[0-9]+[A-Z]+.{7}$'
    m = re.search(regex, id)
    return not not m


@user_routes.route('/api/users/signup', methods=['POST'])
def signin():
    '''
    Route for signing up a new user (eg: student). 
    Uses bcrypt to hash passwords. These hashes are then stored in the collection, thus improving the security.
    Returns a json response with the created user document and a JWT Authorization token with status code 200 on successful requests.
    Returns an error message as json response with status code 400 on unsuccessful request.
    '''
    try:
        username = request.json['username']
        fullname = request.json['fullname']
        email = request.json['email']
        tecid = request.json['tecid'].upper()
        if User.objects(username=username).first():
            raise Exception('Username already taken.')
        if User.objects(email=email).first():
            raise Exception('Email has been already registered.')
        if User.objects(tecid=tecid).first():
            #TODO: SHOW Email for discrepancies
            raise Exception('Account with the provided TEC ID already exists.')
        if not checkID(tecid):
            raise Exception('Please provide a valid TEC-ID')
        unhashed = request.json['password']
        password = bcrypt.hashpw(unhashed.encode(), bcrypt.gensalt())
        user = User(username=username, fullname=fullname, email=email, tecid=tecid, password=password)
        user.save()
        token = jwt.encode({'id': str(user.id), 'username': user.username, 'fullname': user.fullname, 'tecid': user.tecid, 'email': user.email}, SECRET, algorithm='HS256')
        userdict = json.loads(user.to_json())
        del userdict['password']
        return jsonify({'result': userdict , 'token': token.decode()}), 200
    except KeyError:
        return jsonify({'errors': 'Please provide all the required fields'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@user_routes.route('/api/users/login', methods=['POST'])
def login():
    ''' 
    Route for logging in a user. 
    Bcrypt is used for checking the provided password with the hash stored in the database.
    Returns a json response with the created admin document and a JWT Authorization token with status code 200 on successful requests.
    Returns an error message as json response with status code 400 on unsuccessful request.
    '''
    try:
        username = request.json['username']
        password = request.json['password']
        user = User.objects(username=username).first()
        if user and bcrypt.checkpw(password.encode(), user.password.encode()):
            userdict = json.loads(user.to_json())
            del userdict['password']        
            token = jwt.encode({'id': str(user.id), 'username': user.username, 'fullname': user.fullname, 'tecid': user.tecid, 'email': user.email}, SECRET, algorithm='HS256')
            return jsonify({'result': userdict, 'token': token.decode()}), 200
        else:
            raise Exception('Username or password Incorrect') 

    except KeyError:
        return jsonify({'error': 'Please provide all the required fields'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@user_routes.route('/api/users/profile', methods=['GET'])
@user_login_required
@user_is_authorized
def profile():
    '''
    Returns a detailed profile of user in json format with status code 200.
    User needs to authenticated and authorized to access this route, else returns error with status 401
    '''
    try:
        user = User.objects(id=g.user['id']).first()
        if not user:
            raise Exception('User not found.')
        userdict = json.loads(user.to_json())
        del userdict['password']
        userdict['history'] = []
        if user.currentroom:
            cd = json.loads(user.currentroom.to_json())
            del cd['entrylist']
            userdict['currentroom'] = cd
        for entry in user.history:
            ed = json.loads(entry.to_json())
            ed['room_name'] = json.loads(entry.room.to_json())['name']
            userdict['history'].append(ed)
        return jsonify(userdict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@user_routes.route('/api/users/enter', methods=['POST'])
def enter():
    '''
    Route to create entries.
    This POST request requires two fields, id -> the id of room and uid -> the id of user. Future implementations may switch uid with the tecid.
    This POST request also needs a valid user.
    Also checks if the room is full. If the room is full, returns a message with status code 400.
    If user has already entered into the room, returns an error message with status code 400.
    '''
    try:
        rid = request.json['id']
        room = Room.objects(id=rid).first()
        #TODO: Instead of uid, we have to use regex and validate the tecid of student. This will reduce database fetches on the client side.
        user = User.objects(tecid=request.json['uid']).first() 
        entry = Entry()
        if not user:
            raise Exception("You have either provided an unsupported QR/Barcode or you have not signed up with Quick Entry.")
        if not room:
            raise Exception('Invalid Room id')
        if user.currentroom and (user.currentroom.id == room.id):
            raise Exception('You have already entered inside the room.')
        if room.current == room.capacity:
            raise Exception('Room full. You cannot enter now. Please come again after sometime.')
        user.currentroom = room
        room.current = room.current + 1
        #TODO: Decide whether to add room to history on entering or after entring
        entry.user = user
        entry.room = room
        entry.timestamp = int(round(time.time() * 1000))
        entry.save()
        user.history.append(entry)
        room.entrylist.append(entry)
        user.save()
        room.save()
        return jsonify({'result': 'SUCCESS'}), 200
    except KeyError:
        return jsonify({'error': 'id and uid is required.'}), 400
    except ValidationError:
        return jsonify({'error': 'Please provide a valid id'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@user_routes.route('/api/users/exit', methods=['POST'])
def uexit():
    '''
    Route to record exits. This helps in storing the exit time of a user.
    Also helps in providing insights on how much time an user spends inside the room on average.
    Requires two fields, id and uid, which have the same meaning as the above /entry route.
    '''
    try:
        rid = request.json['id']
        uid = request.json['uid']
        room = Room.objects(id=rid).first()
        user = User.objects(tecid=uid).first()
        if not user:
            raise Exception('User not found. Please signup first.')
        elif not room:
            raise Exception('Room id is invalid.')
        elif not user.currentroom:
            raise Exception('Please enter a room first to exit.')
        elif user.currentroom.id != room.id or not room:
            raise Exception('You are not inside this room to exit.')
        for entry in room.entrylist:
            if entry.user.id == user.id and not entry.exittime:
                entry.exittime = int(round(time.time() * 1000))
                room.current = room.current - 1
                user.currentroom = None
                entry.save()
                room.save()
                user.save()
                return jsonify({'message': 'Thank you for visitng {}.'.format(room.name)}), 200
        return jsonify({'message': 'Exit was not recorded due to some error.'}), 400
    except KeyError:
        return jsonify({'error': 'Please provide all the required data.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400