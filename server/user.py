from flask import Blueprint, request, jsonify
from db import User
from keys import SECRET
import bcrypt
import jwt
import json

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/api/users/signup', methods=['POST'])
def signin():
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