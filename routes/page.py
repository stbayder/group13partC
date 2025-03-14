from flask import Blueprint, render_template
from utilities.db_connector import mongo
from utilities.utils import convert_objectid

page_bp = Blueprint("pages", __name__)

@page_bp.route("/")
def home():
    return render_template("index.html")

@page_bp.route("/about")
def about():
    return render_template("about.html")

@page_bp.route("/contact-us")
def contact():
    return render_template("contact-us.html")

@page_bp.route('/add-product', methods=['GET'])
def get_add_product():
    return render_template('create-supplier-product.html')

@page_bp.route('/product-gallery', methods=['GET'])
def product_gallery():
    all_products = list(mongo.db.products.find())
    return render_template('product-gallery.html',products=convert_objectid(all_products))

@page_bp.route('/login', methods=['GET'])
def loginPage():
    return render_template('login.html')

@page_bp.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html')

@page_bp.route('/admin/products', methods=['GET'])
def adminProductsPage():
    # Get all products
    all_products = list(mongo.db.products.find())
    
    for product in all_products:
        product_id = product['ProdID']
        # Count supplier_products documents where ProdID matches this product's ID
        supplier_count = mongo.db.supplier_products.count_documents({"ProdID": product_id})
        product['numberOfSupps'] = supplier_count
    
    products_json = convert_objectid(all_products)
    
    return render_template('admin-products.html', products=products_json)

@page_bp.route('/admin/edit-product/<product_id>', methods=['GET'])
def admin_edit_product(product_id):
    # Convert product_id to integer since ProdID is stored as an integer
    product_id = int(product_id)
    product = mongo.db.products.find_one({'ProdID': product_id})
    # Convert ObjectId to string for JSON serialization
    if product and '_id' in product:
        product['_id'] = str(product['_id'])
    return render_template('admin-edit-product.html', product=product)
