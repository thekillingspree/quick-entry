from flask import Blueprint, request, jsonify, g
from .db import Admin, User, Room
from .keys import SECRET
from .middleware.login import *
import json
import jwt

room_routes = Blueprint('room_routes', __name__)


@room_routes.route('/api/rooms/new', methods=['POST'])
@admin_login_required
def create():
    try:
        admin = Admin.objects(id=g.admin['id']).first()
        name = request.json['name']
        roomnumber = request.json['roomnumber']
        capacity = request.json['capacity']
        for r in admin.rooms:
            if r.name == name:
                raise Exception('You have already created a room with name as \'{}\''.format(name))
            if r.roomnumber == roomnumber:
                raise Exception('You already have a room with the same room number. ({})'.format(r.name))
        room = Room(name=name, roomnumber=roomnumber, capacity=capacity)
        room.save()
        admin.rooms.append(room)
        admin.save()
        return room.to_json(), 200
    except KeyError:
        return jsonify({'error': 'Please provide all fields'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@room_routes.route('/api/rooms/view', methods=['GET'])
@admin_login_required
@admin_is_authorized
def viewroom():
    try:
        admin = Admin.objects(id=g.admin['id']).first()
        rid = request.args.get('rid')
        if not rid:
            raise Exception('Please provide room id.')
        room = Room.objects(id=rid).first()
        res = json.loads(room.to_json())
        res['entrylist'] = []
        for entry in room.entrylist:
            u = entry.user
            d = json.loads(entry.to_json())
            d['user'] = {'fullname': u.fullname, 'tecid': u.tecid}
            res['entrylist'].append(d)
        return jsonify(res), 200
    except KeyError:
        return jsonify({'error': 'Please provide all fields'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400
