from flask import Blueprint, request, jsonify,redirect,url_for
from utilities.db_connector import mongo
from utilities.utils import convert_objectid, check_if_admin

supplier_bp = Blueprint("suppliers", __name__)

@supplier_bp.route('/', methods=['GET'])
def get_all_suppliers():
    try:
        suppliers = list(mongo.db.suppliers.find({}))
        
        # Convert ObjectId to string
        for supplier in suppliers:
            supplier['_id'] = str(supplier['_id'])

        return jsonify({"message": "Success", "data": suppliers}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@supplier_bp.route('/by-username/<username>',methods=['GET'])
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
            "SuppID":supplier['SuppID'],
            "fullname": user['FullName'] if user else None,
            "email": supplier['Email'],
            "phone": supplier['Phone'],
            "address": supplier['Address'],
            "role": user['Role'] if user else "Unknown",
        }
    }), 200

@supplier_bp.route('/by-name/<supplier_name>', methods=['GET'])
def get_supplier_by_name(supplier_name):
    supplier = mongo.db.suppliers.find_one({"SuppName": supplier_name})
    if not supplier:
        return jsonify({"error": "Supplier not found"}), 404  # Supplier not found

    user = mongo.db.users.find_one({"UserID": supplier['UserID']})
    
    return jsonify({
        "message": "Success",
        "data": {
            "SuppName": supplier['SuppName'],
            "SuppID":supplier['SuppID'],
            "fullname": user['FullName'] if user else None,
            "email": supplier['Email'],
            "phone": supplier['Phone'],
            "address": supplier['Address'],
            "role": user['Role'] if user else "Unknown",
        }
    }), 200

@supplier_bp.route('/products/<supplierID>', methods=["GET"])
def get_supplier_products(supplierID):
    try:
        # Validate that supplierID is a number
        if not supplierID.isdigit():
            return jsonify({"error": "Invalid supplier ID format"}), 400

        supplierID = int(supplierID)  # Convert to int after validation
        
        # Fetch supplier products
        supplier_products = list(mongo.db.supplier_products.find({"SuppID": supplierID}))

        if not supplier_products:
            return jsonify({"message": "No products found for this supplier"}), 404

        # Convert ObjectId fields to strings
        supplier_products = convert_objectid(supplier_products)

        # Fetch product details for each supplier product
        for sp in supplier_products:
            product = mongo.db.products.find_one({"ProdID": sp["ProdID"]})
            sp["ProductDetails"] = convert_objectid(product) if product else None

        return jsonify({"message": "Success", "data": supplier_products}), 200

    except Exception as e:
        print("Error fetching supplier products:", e)
        return jsonify({"error": "Internal Server Error"}), 500

@supplier_bp.route('/products/not-linked/<supplierID>', methods=["GET"])
def get_products_not_linked_to_supplier(supplierID):
    try:
        if not supplierID.isdigit():
            return jsonify({"error": "Invalid supplier ID format"}), 400

        supplierID = int(supplierID)

        supplier_products = list(mongo.db.supplier_products.find({"SuppID":  supplierID}))

        if not supplier_products:
            return jsonify({"message": "No supplier products found that are not linked to this supplier"}), 404

        # Extract the ProdID values from supplier_products
        prod_ids = [sp["ProdID"] for sp in supplier_products]

        # Fetch the products using the ProdID list
        products_not_linked = list(mongo.db.products.find({"ProdID": {"$nin": prod_ids}}))

        if not products_not_linked:
            return jsonify({"message": "No products found matching the criteria"}), 404

        # Convert ObjectId fields to strings for JSON serializability
        products_not_linked = convert_objectid(products_not_linked)

        return jsonify({"message": "Success", "data": products_not_linked}), 200

    except Exception as e:
        print("Error fetching products not linked to supplier:", e)
        return jsonify({"error": "Internal Server Error"}), 500

@supplier_bp.route('/products/<supplier_id>/<SP_ID>', methods=["POST"])
def add_supplier_product(supplier_id, SP_ID):
    # Get the data from the request body
    data = request.get_json()
    
    price1 = data.get("price1")
    amount1 = data.get("amount1")
    price2 = data.get("price2")
    amount2 = data.get("amount2")
    units = data.get("units")

    # Validate input data
    if not all([price1, amount1, price2, amount2, units]):
        return jsonify({"error": "Missing required fields"}), 400

    # Create a new supplier product document
    supplier_product = {
        "SuppID": int(supplier_id),
        "ProdID": int(SP_ID),
        "Price1": price1,
        "Amount1": amount1,
        "Price2": price2,
        "Amount2": amount2,
        "StockQuantity": units
    }

    try:
        # Insert the document into the 'supplier_product' collection
        result = mongo.db.supplier_products.insert_one(supplier_product)
        
        # Return success response with inserted ID
        return jsonify({"message": "Success", "SupplierProductID": str(result.inserted_id)}), 201
    except Exception as e:
        # Handle any errors that occur during insertion
        return jsonify({"error": str(e)}), 500

@supplier_bp.route('/products/<SP_ID>', methods=['DELETE'])
def delete_SP(SP_ID):
    print(SP_ID)
    try:
        SP_ID = int(SP_ID)
        check = check_if_admin(request, mongo)
        if check == 'Not signed in':
            return redirect(url_for('loginPage'))
        elif check == 'Not Admin':
            return redirect(url_for('home'))

        SP = mongo.db.supplier_products.find_one({'SupplierProductID': SP_ID})
        if not SP:
            return jsonify({'success': False, 'message': 'מוצר לא נמצא'}), 404
        
        # Then delete the product itself
        SP_result = mongo.db.supplier_products.delete_one({'SupplierProductID': SP_ID})
        
        if SP_result.deleted_count > 0:
            return jsonify({
                'success': True, 
                'message': "מוצר ספק נמחק בהצלחה",
            }), 200
        else:
            return jsonify({'success': False, 'message': 'אירעה שגיאה במחיקת המוצר'}), 500
            
    except ValueError:
        return jsonify({'success': False, 'message': 'מזהה מוצר לא תקין'}), 400
    except Exception as e:
        print(f"Error deleting product: {str(e)}")
        return jsonify({'success': False, 'message': 'אירעה שגיאה במחיקת המוצר'}), 500