from flask import Blueprint, request, jsonify, g
from mongoengine.errors import ValidationError
import bcrypt
import jwt
import json
import time

from middleware.login import user_login_required, user_is_authorized
from db import User, Room, Entry
from keys import SECRET

user_routes = Blueprint('user_routes', __name__)

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
        unhashed = request.json['password']
        password = bcrypt.hashpw(unhashed.encode(), bcrypt.gensalt())
        user = User(username=username, fullname=fullname, email=email, tecid=tecid, password=password)
        user.save()
        token = jwt.encode({'id': str(user.id), 'username': user.username, 'fullname': user.fullname, 'tecid': user.tecid, 'email': user.email}, SECRET, algorithm='HS256')
        return jsonify({'result': json.loads(user.to_json()), 'token': token.decode()}), 200
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
            token = jwt.encode({'id': str(user.id), 'username': user.username, 'fullname': user.fullname, 'tecid': user.tecid, 'email': user.email}, SECRET, algorithm='HS256')
            return jsonify({'result': json.loads(user.to_json()), 'token': token.decode()}), 200
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
            ed['room'] = json.loads(entry.room.to_json())
            ed['user'] = json.loads(entry.user.to_json())
            del ed['user']['password']
            userdict['history'].append(ed)
        return jsonify(userdict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@user_routes.route('/api/users/enter', methods=['POST'])
def enter():
    try:
        rid = request.json['id']
        room = Room.objects(id=rid).first()
        #TODO: Instead of uid, we have to use regex and validate the tecid of student. This will reduce database fetches on the client side.
        user = User.objects(id=request.json['uid']).first() 
        entry = Entry()
        if not user:
            raise Exception("You have not signed up.")
        if user.currentroom and (user.currentroom.id == room.id):
            raise Exception('You have already entered inside the room.')
        user.currentroom = room
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