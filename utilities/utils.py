from bson import ObjectId
from flask import jsonify,redirect, url_for

def convert_objectid(data):
    """Recursively converts ObjectId fields to strings in a dictionary or list."""
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: str(value) if isinstance(value, ObjectId) else value for key, value in data.items()}
    return data

def check_if_admin(request, mongo):
    username = request.cookies.get('username')
    if not username:
        return False, 'Not signed in'
    
    user = mongo.db.users.find_one({'UserName': username})
    if not user:
        return False, 'User not found'
    
    if user.get('Role') != 'Admin':
        return False, 'Not Admin'
    
    return True, 'Admin'
