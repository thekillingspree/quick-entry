from flask import Flask, request, jsonify
from flask_cors import CORS
from admin import admin_routes
from user import user_routes


app = Flask(__name__)

CORS(app)

app.register_blueprint(admin_routes)
app.register_blueprint(user_routes)

if __name__ == '__main__':
    app.run(debug=True)