from flask import Flask, jsonify, render_template, request
import os
from flask_pymongo import PyMongo
from gridfs import GridFS
from dotenv import load_dotenv
import bcrypt

from utilities.db_connector import initialize_db,hash_password

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("DB_URI")
mongo = PyMongo(app)
fs = GridFS(mongo.db)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def loginPage():
    return render_template('login.html')

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
    print("password:",password)
    print("stored passsword:",stored_hashed_password)

    if bcrypt.checkpw(password.encode("utf-8"), stored_hashed_password.encode("utf-8")):
        return jsonify({"message": "Login successful!", "username": username}), 200

    return jsonify({"error": "Invalid credentials"}), 401  # Incorrect password

@app.route('/contact-us/', methods=['GET', 'POST'])
def contact():
    return render_template('contact-us.html')

@app.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

@app.route('/supplier/<username>',methods=['GET'])
def get_supplier_data(username):
    user = mongo.db.users.find_one({"UserName": username})
    if not user :
        return jsonify({"error": "Invalid credentials, user not found"}), 401  # User not found
    supplier = mongo.db.suppliers.find_one({"UserID":user['UserID']})
    if not supplier :
        return jsonify({"error": "Invalid credentials, supplier not found"}), 401  # Supplier not found

    return jsonify(
    {
        "message": 'Success',
        "data": {
            "SuppName": supplier['SuppName'],
            "fullname": user['FullName'],
            "email": supplier['Email'],
            "phone": supplier['Phone'],
            "address": supplier['Address'],
            "role": user['Role']
        }
    }), 200

@app.route('/add-product', methods=['GET'])
def add_product():
    return render_template('add-product.html')

@app.route('/product-gallery', methods=['GET'])
def product_gallery():
    all_products = list(mongo.db.products.find())
    return render_template('product-gallery.html',products=all_products)

@app.route('/product-info/<product_id>', methods=['GET'])
def product_info(product_id):
    try:
        product_id = int(product_id)
    except ValueError:
        return "Invalid product ID", 400  
    
    # Query supplier_products to find all suppliers offering this product
    suppliers_of_product = list(mongo.db.supplier_products.find({"ProdID": product_id}))
    if not suppliers_of_product:
        return "Invalid product ID", 400  

    # Query product to get product info
    product = mongo.db.products.find_one({"ProdID": product_id})

    # Query discounts for this product
    discounts = list(mongo.db.discounts.find({"ProdID": product_id}))

    # Fetch supplier details for each entry, and combine data from supplier_product and supplier
    suppliers_info = []

    for entry in suppliers_of_product:
        supplier = mongo.db.suppliers.find_one({"SuppID": entry["SuppID"]})

        # Find a matching discount for this supplier and product
        supplier_discount = next((disc for disc in discounts if disc['SuppID'] == entry['SuppID']), None)

        if supplier:
            supplier_info = {
                "SuppName": supplier["SuppName"],
                "Address": supplier['Address'],
                "Price1": entry["Price1"],
                "Amount1": entry["Amount1"],
                "Price2": entry["Price2"],
                "Amount2": entry["Amount2"],
                "Email": supplier["Email"],
                "Phone": supplier["Phone"],
                "SuppID": supplier["SuppID"],
                "Stock": entry["StockQuantity"],
            }
            
            # Only attach the discount if it exists for this supplier
            if supplier_discount:
                supplier_info["Discount"] = supplier_discount

            suppliers_info.append(supplier_info)
    return render_template('product-info.html', suppliers=suppliers_info,product=product)


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

if __name__ == '__main__':
    with app.app_context():
        initialize_db(mongo.db)
    print("MongoDB setup complete.")
    app.run(debug=True)

