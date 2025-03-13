from flask import Blueprint, request, jsonify
from utilities.db_connector import mongo


user_bp = Blueprint("users", __name__)


@user_bp.route('/<username>', methods=['GET'])
def getUserData(username):
    user = mongo.db.users.find_one({"UserName": username})
    if user:
        return {
            'UserName':user['UserName'],
            'Email':user["Email"],
            'Role':user["Role"],
            'FullName':user["FullName"]
        }
    else:
        return jsonify({"error": "Invalid credentials, username not found"}), 401  # User not found

@user_bp.route("/", methods=["GET"])
def get_users():
    return jsonify({"message": "Fetching all users"}), 200

@user_bp.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    return jsonify({"message": f"Fetching user {user_id}"}), 200

@user_bp.route("/", methods=["POST"])
def create_user():
    data = request.json
    return jsonify({"message": "User created", "data": data}), 201

@user_bp.route("/<user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    return jsonify({"message": f"User {user_id} updated", "data": data}), 200

@user_bp.route("/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    return jsonify({"message": f"User {user_id} deleted"}), 200
