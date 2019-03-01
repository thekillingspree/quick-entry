from flask import Blueprint, request, jsonify
from db import Admin
from keys import SECRET
import bcrypt
import json
import jwt

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route("/api/admin/signup", methods=['POST'])
def admsignup():
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