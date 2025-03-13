import os
import json
import bcrypt
import string
import random
from flask import Flask
from flask_pymongo import PyMongo
from gridfs import GridFS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app and MongoDB
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("DB_URI")
mongo = PyMongo(app)
fs = GridFS(mongo.db)

# Function to hash a password
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

# Function to generate a random password
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# Function to initialize collections
def initialize_db():
    db = mongo.db  # Get the MongoDB instance

    # Ensure unique UserID index
    db.users.create_index("UserID", unique=True)
    
    collections = ["users", "suppliers", "products", "discounts", "supplier_products"]
    
    # Load mock data
    try:
        with open("static/data/mock_data.json", "r", encoding="utf-8") as file:
            mock_data = json.load(file)
    except FileNotFoundError:
        print("⚠️ Mock data file not found. Skipping data initialization.")
        return

    for col in collections:
        if col not in db.list_collection_names():
            db.create_collection(col)
            
            if col == "users":
                for user in mock_data.get(col, []):
                    password = generate_password()
                    user["password_hash"] = hash_password(password).decode('utf-8')
                    
            db[col].insert_many(mock_data.get(col, []))
            print(f"✅ Created and populated collection: {col}")
        elif db[col].count_documents({}) == 0:
            if col == "users":
                for user in mock_data.get(col, []):
                    password = generate_password()
                    user["password_hash"] = hash_password(password).decode('utf-8')
            
            db[col].insert_many(mock_data.get(col, []))
            print(f"✅ Inserted data into empty collection: {col}")
        else:
            print(f"ℹ️ Collection {col} already exists and has data.")
