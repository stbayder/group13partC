from flask import Blueprint, request, jsonify, render_template
from utilities.db_connector import mongo
from utilities.utils import convert_objectid


product_bp = Blueprint("products", __name__)

@product_bp.route('/', methods=['POST'])
def create_product():
    try:
        data = request.json
        print(data)

        # Fetch the last inserted product to determine new ProdID
        last_product = mongo.db.products.find_one(sort=[("ProdID", -1)])
        new_prod_id = last_product["ProdID"] + 1 if last_product else 1

        # Fetch supplier details
        supplier = mongo.db.suppliers.find_one({"SuppName": data["SupplierName"]})
        if not supplier:
            return jsonify({"error": "Supplier not found"}), 400

        new_product = {
            "ProdID": new_prod_id,
            "ProdName": data["ProdName"],
            "Currency": "ILS",
            "Category": data["Category"],
            "Specifications": data["Specifications"],
            "Img": data["Img"]
        }

        mongo.db.products.insert_one(new_product)

        # Create supplier product entry
        new_supplier_product = {
            "SupplierProductID": mongo.db.supplier_products.count_documents({}) + 1,
            "SuppID": supplier["SuppID"],
            "ProdID": new_prod_id,
            "Price1": data["Price1"],
            "Amount1": data["Amount1"],
            "Price2": data["Price2"],
            "Amount2": data["Amount2"],
            "StockQuantity": data["StockQuantity"]
        }

        mongo.db.supplier_products.insert_one(new_supplier_product)

        return jsonify({"message": "Product added successfully!", "ProdID": new_prod_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_bp.route('/<product_id>', methods=['GET'])
def product_info(product_id):
    try:
        product_id = int(product_id)
    except ValueError:
        return "Invalid product ID", 400  

    # Query supplier_products to find all suppliers offering this product
    suppliers_of_product = convert_objectid(list(mongo.db.supplier_products.find({"ProdID": product_id})))
    if not suppliers_of_product:
        return "Invalid product ID", 400  

    # Query product to get product info
    product = convert_objectid(mongo.db.products.find_one({"ProdID": product_id}))

    # Query discounts for this product
    discounts = convert_objectid(list(mongo.db.discounts.find({"ProdID": product_id})))

    # Fetch supplier details for each entry, and combine data from supplier_product and supplier
    suppliers_info = []
    for entry in suppliers_of_product:
        supplier = mongo.db.suppliers.find_one({"SuppID": entry["SuppID"]})

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

            if supplier_discount:
                supplier_info["Discount"] = supplier_discount

            suppliers_info.append(supplier_info)

    # Check if request expects JSON response
    if request.headers.get("Accept") == "application/json" or request.args.get("json") == "true":
        return jsonify({"product": product, "suppliers": suppliers_info})

    return render_template('product-info.html', suppliers=suppliers_info, product=product)

@product_bp.route('/<product_id>', methods=["PUT"])
def edit_product(product_id):
    # Convert product_id to integer
    product_id = int(product_id)
    
    # Get the JSON data from the request
    product_data = request.get_json()
    
    try:
        # Ensure the product exists before updating
        existing_product = mongo.db.products.find_one({'ProdID': product_id})
        if not existing_product:
            return jsonify({'success': False, 'message': 'מוצר לא נמצא'}), 404
        
        # Make sure ProdID is not changed
        product_data['ProdID'] = product_id
        
        print(f"Updating product with ProdID: {product_id}")
        print(f"Update data: {product_data}")
        
        result = mongo.db.products.update_one(
            {'ProdID': product_id},  
            {'$set': product_data}   
        )
        
        print(f"Update result: {result.raw_result}")
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'המוצר עודכן בהצלחה'}), 200
        elif result.matched_count > 0:
            return jsonify({'success': True, 'message': 'לא בוצעו שינויים במוצר'}), 200
        else:
            return jsonify({'success': False, 'message': 'מוצר לא נמצא'}), 404
    
    except Exception as e:
        print(f"Error updating product: {str(e)}")
        return jsonify({'success': False, 'message': 'אירעה שגיאה בעדכון המוצר'}), 500

@product_bp.route('/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        # Convert product_id to integer since ProdID is stored as an integer
        product_id = int(product_id)
        
        # Authentication check using the username from cookie
        username = request.cookies.get('username')
        print(username)
        if not username:
            return jsonify({'success': False, 'message': 'אינך מחובר למערכת'}), 401
        
        # Verify user is an admin
        user = mongo.db.users.find_one({'UserName': username})
        if not user or user.get('Role') != 'Admin':
            return jsonify({'success': False, 'message': 'אין לך הרשאות למחוק מוצרים'}), 403
        
        # Check if product exists
        product = mongo.db.products.find_one({'ProdID': product_id})
        if not product:
            return jsonify({'success': False, 'message': 'מוצר לא נמצא'}), 404
            
        # First, delete all supplier products related to this product
        supplier_products_result = mongo.db.supplier_products.delete_many({'ProdID': product_id})
        
        # Then delete the product itself
        product_result = mongo.db.products.delete_one({'ProdID': product_id})
        
        if product_result.deleted_count > 0:
            return jsonify({
                'success': True, 
                'message': f'המוצר נמחק בהצלחה יחד עם {supplier_products_result.deleted_count} הצעות מספקים',
                'deleted_supplier_products': supplier_products_result.deleted_count
            }), 200
        else:
            return jsonify({'success': False, 'message': 'אירעה שגיאה במחיקת המוצר'}), 500
            
    except ValueError:
        return jsonify({'success': False, 'message': 'מזהה מוצר לא תקין'}), 400
    except Exception as e:
        print(f"Error deleting product: {str(e)}")
        return jsonify({'success': False, 'message': 'אירעה שגיאה במחיקת המוצר'}), 500