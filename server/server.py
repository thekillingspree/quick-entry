from flask import Flask, request, jsonify
from flask_cors import CORS
from .admin import admin_routes
from .user import user_routes
from .rooms import room_routes

app = Flask(__name__)
#CORS - Cross Origin Resource Sharing - This needs to be enabled to use our API/server with our app/website since the server the client will have different origins.
CORS(app)

app.register_blueprint(admin_routes)
app.register_blueprint(user_routes)
app.register_blueprint(room_routes)

if __name__ == '__main__':
    app.run(debug=True)