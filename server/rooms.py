from flask import Blueprint, request, jsonify
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
        return jsonify({'success': True}), 200
    except KeyError:
        return jsonify({'error': 'Please provide all fields'}), 400
    except Exception as e:
        return jsonify({'error': str(e)})


