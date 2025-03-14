from flask import Flask
from flask_cors import CORS 
from utilities.db_connector import app, initialize_db  # Import from db_connector

app = Flask(__name__, template_folder="templates")
CORS(app)

# Import routes after MongoDB initialization
from routes.auth import auth_bp
from routes.user import user_bp
from routes.supplier import supplier_bp
from routes.product import product_bp
from routes.page import page_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/users")
app.register_blueprint(supplier_bp, url_prefix="/suppliers")
app.register_blueprint(product_bp, url_prefix="/products")
app.register_blueprint(page_bp, url_prefix="/")

if __name__ == "__main__":
    initialize_db()  # Call function without passing `mongo.db`
    app.run(debug=True)
