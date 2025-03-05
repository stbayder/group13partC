from flask import Flask, render_template, request
import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv

from utilities.db_connector import initialize_db

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("DB_URI")
mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']
    #     # הוספת קוד לבדוק את שם המשתמש והסיסמה
    #     return "ברוך הבא, {}".format(username)  # או מעבר לעמוד אחר
    return render_template('login.html')

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

