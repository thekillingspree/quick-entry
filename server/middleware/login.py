from functools import wraps
from flask import request, jsonify, g
import json
import jwt
from jwt.exceptions import *

from ..db import Admin, User
from ..keys import SECRET

def admin_login_required(f):
    '''
    Login Required View Decorator / Middleware.
    This is a middleware used to check if the token provided in the Authorization header(Bearer) belongs to a valid admin or not. 
    JWT Tokens are provided in Authorization header -> 'Bearer <token>'
    This middleware performs the above mentioned checks and returns the wrapped function if the tokens are validated.
    The flask application context, i.e g is then set to the found admin.
    '''
    @wraps(f)
    def dec_fn(*args, **kwargs):
        try:
            token = request.headers['Authorization'].split()[1]
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            if not payload:
                raise Exception('Admin privileges required. Please Login.')
            g.admin = payload
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
    '''
    Authorization View Decorator/ Middleware
    This middleware functions works just like the login required middleware. 
    It compares the id provided as url parameter with the id stored in the token payload, to see if the current admin is authorized to access the resource.
    '''
    @wraps(f)
    def dec_fn(*args, **kwargs):
        try:
            token = request.headers['Authorization'].split()[1]
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            if not request.args.get('id'):
                raise Exception('id query not provided')
            if (not payload) or payload['id'] != request.args.get('id'):
                raise Exception('You are not authorized')
            return f(*args, **kwargs)
        except InvalidSignatureError:
            return jsonify({'error': 'Signature verification failed.'}), 401
        except DecodeError:
            return jsonify({'error': 'Unauthorized'}), 401
        except InvalidTokenError:
            return jsonify({'error': 'Invalid Token. You are not logged in probably'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    return dec_fn

def user_login_required(f):
    '''
    Same as the admin_login_required middelware, except it deals with the user model.
    '''
    @wraps(f)
    def dec_fn(*args, **kwargs):
        try:
            token = request.headers['Authorization'].split()[1]
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            if not payload:
                raise Exception('Please Login to use this feature.')
            g.user = payload
            return f(*args, **kwargs)
        except InvalidSignatureError:
            return jsonify({'error': 'Signature verification failed.'}), 401
        except DecodeError:
            return jsonify({'error': 'User must be logged in.'}), 401
        except InvalidTokenError:
            return jsonify({'error': 'Invalid Token. You are probably not logged in.'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    return dec_fn

def user_is_authorized(f):
    '''
    Same as the admin_is_authorized middelware, except it deals with the user model.
    '''
    @wraps(f)
    def dec_fn(*args, **kwargs):
        try:
            token = request.headers['Authorization'].split()[1]
            payload = jwt.decode(token, SECRET, algorithms=['HS256'])
            if not request.args.get('uid'):
                raise Exception('uid query not provided')
            if not payload or payload['id'] != request.args.get('uid'):
                raise Exception('You are not authorized.')
            return f(*args, **kwargs)
        except InvalidSignatureError:
            return jsonify({'error': 'Signature verification failed.'}), 401
        except DecodeError:
            return jsonify({'error': 'Unauthorized'}), 401
        except InvalidTokenError:
            return jsonify({'error': 'Invalid Token. You are not logged in probably'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    return dec_fn