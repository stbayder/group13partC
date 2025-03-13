from flask import Blueprint, request, jsonify
from utilities.db_connector import mongo
import bcrypt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('userName')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = mongo.db.users.find_one({"UserName": username})

    if not user:
        return jsonify({"error": "Invalid credentials, username not found"}), 401  # User not found

    # decode and check stored hashed password
    stored_hashed_password = user.get("password_hash")  
    if bcrypt.checkpw(password.encode("utf-8"), stored_hashed_password.encode("utf-8")):
        return jsonify({"message": "Login successful!", "username": username}), 200

    return jsonify({"error": "Invalid credentials"}), 401  # Incorrect password

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "User logged out"}), 200
