from flask import Flask, jsonify, render_template, request
import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import bcrypt

from utilities.db_connector import initialize_db,hash_password

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("DB_URI")
mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('userName')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Find user in the database
    user = mongo.db.users.find_one({"UserName": username})

    if not user:
        return jsonify({"error": "Invalid credentials, username not found"}), 401  # User not found

    # Extract stored hashed password
    stored_hashed_password = user.get("password_hash")  

    # Verify password
    if bcrypt.checkpw(password.encode("utf-8"), stored_hashed_password.encode("utf-8")):
        return jsonify({"message": "Login successful!", "username": username}), 200

    return jsonify({"error": "Invalid credentials"}), 401  # Incorrect password

@app.route('/contact-us/', methods=['GET', 'POST'])
def contact():
    return render_template('contact-us.html')

@app.route('/profile/', methods=['GET'])
def profile():
    return render_template('profile.html')

@app.route('/add-product', methods=['GET'])
def add_product():
    return render_template('add-product.html')

@app.route('/product-gallery', methods=['GET'])
def product_gallery():
    return render_template('product-gallery.html')

@app.route('/product-info', methods=['GET'])
def product_info():
    return render_template('product-info.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

if __name__ == '__main__':
    with app.app_context():
        initialize_db(mongo.db)
    print("MongoDB setup complete.")
    app.run(debug=True)

