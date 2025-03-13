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