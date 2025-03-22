import os
import json
import bcrypt
import string
import random
import subprocess
import sys
from pathlib import Path
from flask import Flask
from flask_pymongo import PyMongo
from gridfs import GridFS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

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
    
    # Check if mock data file exists
    mock_data_path = os.path.join(BASE_DIR, "static", "data", "mock_data.json")
    
    if not os.path.exists(mock_data_path):
        print("⚠️ Mock data file not found. Generating mock data...")
        try:
            # Check if the generate_mock_data.py script exists in utilities folder
            mock_data_generator = os.path.join(BASE_DIR, "utilities", "generate_mock_data.py")
            if os.path.exists(mock_data_generator):
                # Use the correct path to the script and make sure directories exist
                os.makedirs(os.path.dirname(mock_data_path), exist_ok=True)
                subprocess.run([sys.executable, mock_data_generator], check=True)
                print("✅ Mock data generated successfully.")
            else:
                print(f"❌ generate_mock_data.py not found at {mock_data_generator}. Cannot generate mock data.")
                return
        except subprocess.CalledProcessError:
            print("❌ Error generating mock data.")
            return
    
    # Load mock data
    try:
        with open(mock_data_path, "r", encoding="utf-8") as file:
            mock_data = json.load(file)
    except FileNotFoundError:
        print(f"❌ Mock data file still not found at {mock_data_path} after generation attempt. Skipping data initialization.")
        return
    except json.JSONDecodeError:
        print("❌ Error parsing mock data file. The file may be corrupted.")
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

# Make sure to export the Flask app instance
__all__ = ['app', 'mongo', 'fs', 'initialize_db', 'hash_password', 'generate_password']