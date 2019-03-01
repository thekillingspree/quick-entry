from flask import Flask, request, jsonify
from admin import admin_routes



app = Flask(__name__)
app.register_blueprint(admin_routes)


if __name__ == '__main__':
    app.run(debug=True)