from bson import ObjectId

def convert_objectid(data):
    """Recursively converts ObjectId fields to strings in a dictionary or list."""
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: str(value) if isinstance(value, ObjectId) else value for key, value in data.items()}
    return data