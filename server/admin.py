from flask import Blueprint, request, jsonify, g
from db import Admin
from keys import SECRET
from middleware.login import admin_login_required, admin_is_authorized
import bcrypt
import json
import jwt

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route("/api/admin/signup", methods=['POST'])
def admsignup():
    ''' 
    Route for signing up a new admin. 
    Uses bcrypt to hash passwords. These hashes are then stored in the collection, thus improving the security.
    Returns a json response with the created admin document and a JWT Authorization token with status code 200 on successful requests.
    Returns an error message as json response with status code 400 on unsuccessful request.
    '''
    try:
        username = request.json['username']
        fname = request.json['fname']
        unhashed = request.json['password'].encode()
        password = bcrypt.hashpw(unhashed, bcrypt.gensalt())
        admin = Admin(username=username, fname=fname, password=password)
        admin.save()
        token = jwt.encode({"id": str(admin.id), "username": admin.username, "fname": admin.fname}, SECRET, algorithm='HS256')
        return jsonify({"result": json.loads(admin.to_json()), "token": token.decode()}), 200
    except KeyError:
        return jsonify({"error": "Need all values"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@admin_routes.route('/api/admin/login', methods=['POST'])
def login():
    '''
    Route for logging in an admin.
    Bcrypt is used for checking the provided password with the hash stored in the database.
    Returns a json response with the found admin document and a JWT Authorization token with status code 200 on successful requests.
    Returns an error message as json response with status code 400 on unsuccessful request.
    '''
    try:
        username = request.json['username']
        password = request.json['password']
        admin = Admin.objects(username=username).first()
        if not admin:
            raise Exception("Username or password incorrect")
        if bcrypt.checkpw(password.encode(), admin.password.encode()):
            token = jwt.encode({"id": str(admin.id), "username": admin.username, "fname": admin.fname}, SECRET, algorithm='HS256')
            return jsonify({"status": "SUCCESS", "code": 200, "token": token.decode()}), 200
        raise Exception("Username or password incorrect")
    except KeyError:
        return jsonify({"error": "Need all values"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@admin_routes.route('/api/admin/rooms', methods=['GET'])
@admin_login_required
@admin_is_authorized
def getallrooms():
    try:
        admin = Admin.objects(id=g.admin['id']).first()
        allrooms = []
        for room in admin.rooms:
            roomdict = json.loads(room.to_json())
            allrooms.append(roomdict)
        return jsonify(allrooms), 200
    except Exception as e:
        return {'error': str(e)}, 400