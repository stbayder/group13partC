from bson import ObjectId
from flask import jsonify

def convert_objectid(data):
    """Recursively converts ObjectId fields to strings in a dictionary or list."""
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: str(value) if isinstance(value, ObjectId) else value for key, value in data.items()}
    return data

def check_if_admin(request,mongo):
    username = request.cookies.get('username')
    if not username:
        return 'Not signed in'
    
    user = mongo.db.users.find_one({'UserName': username})
    if not user or user.get('Role') != 'Admin':
        return 'Not Admin'
    