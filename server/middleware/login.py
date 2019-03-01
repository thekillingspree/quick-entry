from functools import wraps
from flask import request, jsonify, g
import json
import jwt
from jwt.exceptions import *

from db import Admin
from keys import SECRET

def admin_login_required(f):
    @wraps(f)
    def dec_fn(*args, **kwargs):
        try:
            token = request.headers['Authorization'].split()[1]
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            if not payload:
                raise Exception('Admin privileges required. Please Login.')
            return f(*args, **kwargs)
        except InvalidSignatureError:
            return jsonify({'error': 'Signature verification failed.'}), 401
        except DecodeError:
            return jsonify({'error': 'Admin must be logged in.'}), 401
        except InvalidTokenError:
            return jsonify({'error': 'Invalid Token. You are not logged in probably'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    return dec_fn

def admin_is_authorized(f):
    @wraps(f)
    def dec_fn(*args, **kwargs):
        try:
            token = request.headers['Authorization'].split()[1]
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            if not payload and json.loads(payload)['id'] == g.id:
                raise Exception('Admin privileges required. Please Login.')
            return f(*args, **kwargs)
        except InvalidSignatureError:
            return jsonify({'error': 'Signature verification failed.'}), 401
        except DecodeError:
            return jsonify({'error': 'Admin must be logged in.'}), 401
        except InvalidTokenError:
            return jsonify({'error': 'Invalid Token. You are not logged in probably'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    return dec_fn
