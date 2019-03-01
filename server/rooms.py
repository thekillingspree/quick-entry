from flask import Blueprint, request, jsonify, g
from db import Admin, User, Room
from keys import SECRET
from middleware.login import *
import json
import jwt

room_routes = Blueprint('room_routes', __name__)


@room_routes.route('/api/rooms/new', methods=['POST'])
@admin_login_required
def create():
    try:
        name = request.json['name']
        roomnumber = request.json['roomnumber']
        capacity = request.json['capacity']
        room = Room(name=name, roomnumber=roomnumber, capacity=capacity)
        room.save()
        admin = Admin.objects(id=g.admin['id']).first()
        admin.rooms.append(room)
        admin.save()
        return room.to_json(), 200
    except KeyError:
        return jsonify({'error': 'Please provide all fields'}), 400
    except Exception as e:
        return jsonify({'error': str(e)})


