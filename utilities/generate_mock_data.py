import json
import random
from faker import Faker
import string
import bcrypt

# Initialize Faker with Hebrew locale
fake = Faker('he_IL')
# Also use English for certain fields
fake_en = Faker('en_US')

# Function to hash a password
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode('utf-8')

# Function to generate a random password
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def generate_mock_data():
    # Lists to store our generated data
    users = []
    suppliers = []
    products = []
    supplier_products = []
    discounts = []
    
    # ------- Generate Users -------
    user_roles = ["Admin", "Supplier"]
    user_ids = list(range(1, 31))  # Generate 30 users to choose from
    
    # Create 10 users (mix of Admin and Supplier)
    for i in range(1, 11):
        role = random.choice(user_roles)
        hebrew_name = fake.name()
        username = fake_en.user_name() + str(random.randint(1, 999))
        
        user = {
            "UserID": i,
            "UserName": username,
            "Email": f"{username}@{fake_en.domain_name()}",
            "Role": role,
            "FullName": hebrew_name,
            "password_hash": hash_password(generate_password())
        }
        users.append(user)
    
    # ------- Generate Suppliers -------
    # Only for users who are suppliers
    supplier_user_ids = [user["UserID"] for user in users if user["Role"] == "Supplier"]
    
    for i, user_id in enumerate(supplier_user_ids, 1):
        supplier = {
            "SuppID": i,
            "SuppName": fake.company(),
            "Email": f"business_{user_id}@{fake_en.domain_name()}",
            "Phone": f"05{random.randint(0, 9)}-{random.randint(1000000, 9999999)}",
            "Address": f"{fake.street_name()} {random.randint(1, 200)}, {fake.city()}",
            "UserID": user_id
        }
        suppliers.append(supplier)
    
    # ------- Generate Products -------
    # Create 20 products
    categories = ["מזון", "אלקטרוניקה", "ביגוד", "מוצרי חשמל", "משקאות", "טיפוח", "ציוד משרדי", "אביזרי בית"]
    currencies = ["ILS", "USD", "EUR"]
    
    product_images = [
        "https://orchardfruit.com/cdn/shop/files/Navel-Oranges-1-Pcs-The-Orchard-Fruit-72137770.jpg?crop=center&height=1200&v=1722937866&width=1200",
        "https://assets.epicurious.com/photos/5947f7257c8b416bb8639aee/16:9/w_2560%2Cc_limit/banana-almond-smoothie.jpg",
        "https://img.freepik.com/free-psd/laptop-psd-mockup-with-gradient-led-light_53876-115623.jpg",
        "https://t4.ftcdn.net/jpg/02/30/60/07/360_F_230600764_Uh5yc9Lg4pfO8tvuhS7iw7kkUWcgLUHx.jpg",
        "https://img.freepik.com/free-photo/blue-office-shirt_1203-2841.jpg",
        "https://static.vecteezy.com/system/resources/previews/011/012/237/non_2x/3d-render-illustration-black-headphones-png.png",
        "https://img.freepik.com/free-photo/arrangement-black-friday-shopping-carts-with-copy-space_23-2148667047.jpg",
        "https://img.freepik.com/free-photo/bottle-wine-isolated-white_93675-131610.jpg"
    ]
    
    for i in range(1, 21):
        category = random.choice(categories)
        
        # Generate specifications based on category
        if category == "מזון":
            specs = f"מוצר טרי, {random.choice(['עשיר בויטמינים', 'אורגני', 'מקומי'])}, תוקף: {fake.date_this_year()}"
        elif category == "אלקטרוניקה":
            specs = f"{random.choice(['מעבד חזק', 'זיכרון גדול', 'סוללה איכותית'])}, אחריות לשנה"
        else:
            specs = f"{random.choice(['איכות גבוהה', 'מבצע מיוחד', 'מוצר פרימיום'])}, {fake.sentence(nb_words=5)}"
        
        product = {
            "ProdID": i,
            "ProdName": fake.word().capitalize() + " " + fake.word(),
            "Currency": random.choice(currencies),
            "Category": category,
            "Specifications": specs,
            "Img": random.choice(product_images)
        }
        products.append(product)
    
    # ------- Generate Supplier Products -------
    # Each supplier should have multiple products
    supplier_product_id = 1
    
    # Base prices for products (to ensure similar products have similar prices)
    base_prices = {product["ProdID"]: random.randint(50, 1000) for product in products}
    
    for supplier in suppliers:
        # Each supplier offers 3-5 products
        num_products = random.randint(3, 5)
        selected_products = random.sample([p["ProdID"] for p in products], num_products)
        
        for prod_id in selected_products:
            # Get base price and add some variation
            base_price = base_prices[prod_id]
            price_variation = random.uniform(0.9, 1.1)  # 10% variation
            
            price1 = round(base_price * price_variation, 2)
            price2 = round(price1 * 0.9, 2)  # 10% discount for bulk
            
            supplier_product = {
                "SupplierProductID": supplier_product_id,
                "SuppID": supplier["SuppID"],
                "ProdID": prod_id,
                "Price1": price1,
                "Amount1": random.randint(1, 10),
                "Price2": price2,
                "Amount2": random.randint(15, 30),
                "StockQuantity": random.randint(100, 500)
            }
            supplier_products.append(supplier_product)
            supplier_product_id += 1
    
    # ------- Generate Discounts -------
    # Create discounts for some supplier products
    discount_types = ["Percentage", "Fixed"]
    conditions = [
        "לרכישות מעל 200 ש\"ח",
        "למזמינים אונליין",
        "ללקוחות חדשים",
        "בהצגת כרטיס חבר",
        "בקניית 2 יחידות ומעלה",
        "משלוח חינם"
    ]
    
    for i in range(1, 11):
        # Select random supplier product
        sp = random.choice(supplier_products)
        
        discount_type = random.choice(discount_types)
        if discount_type == "Percentage":
            value = round(random.uniform(5, 30), 2)  # 5% to 30% discount
        else:
            value = random.randint(10, 100)  # 10 to 100 units of currency off
        
        discount = {
            "DiscountID": i,
            "SuppID": sp["SuppID"],
            "ProdID": sp["ProdID"],
            "DiscountType": discount_type,
            "DiscountValue": value,
            "Conditions": random.choice(conditions)
        }
        discounts.append(discount)
    
    # Compile all data into a dictionary
    mock_data = {
        "users": users,
        "suppliers": suppliers,
        "products": products,
        "supplier_products": supplier_products,
        "discounts": discounts
    }
    
    return mock_data

def save_mock_data(data, filename="static/data/mock_data.json"):
    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Write data to file
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    print(f"Mock data saved to {filename}")
    print(f"Generated {len(data['users'])} users")
    print(f"Generated {len(data['suppliers'])} suppliers")
    print(f"Generated {len(data['products'])} products")
    print(f"Generated {len(data['supplier_products'])} supplier products")
    print(f"Generated {len(data['discounts'])} discounts")

if __name__ == "__main__":
    mock_data = generate_mock_data()
    save_mock_data(mock_data)