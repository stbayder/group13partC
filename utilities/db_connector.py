import json
import bcrypt

# Function to hash a password
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

# Function to generate a random password
def generate_password(length=12):
    import string
    import random
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# Function to initialize collections
def initialize_db(db):
    print("stavpassword:",hash_password("stavisthebest").decode('utf-8'))
    # Ensure unique UserID index
    db.users.create_index("UserID", unique=True)
    
    # Collection names
    collections = ["users", "suppliers", "products", "discounts", "supplier_products"]
    
    # Load mock data
    with open("static/data/mock_data.json", "r", encoding="utf-8") as file:
        mock_data = json.load(file)
    
    for col in collections:
        if col not in db.list_collection_names():
            db.create_collection(col)
            
            if col == "users":
                # Process users to add password hashes
                for user in mock_data.get(col, []):
                    password = generate_password()
                    user["password_hash"] = hash_password(password).decode('utf-8')
                    
            db[col].insert_many(mock_data.get(col, []))
            print(f"Created and populated collection: {col}")
        elif db[col].count_documents({}) == 0:
            if col == "users":
                # Process users to add password hashes
                for user in mock_data.get(col, []):
                    password = generate_password()
                    user["password_hash"] = hash_password(password).decode('utf-8')
            
            db[col].insert_many(mock_data.get(col, []))
            print(f"Inserted data into empty collection: {col}")
        else:
            print(f"Collection {col} already exists and has data.")
