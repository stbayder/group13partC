from flask import Blueprint, request, jsonify,redirect,url_for,render_template
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
        if not supplierID.isdigit():
            return jsonify({"error": "Invalid supplier ID format"}), 400

        supplierID = int(supplierID)  # Convert to int after validation
        
        # Fetch supplier products
        supplier_products = list(mongo.db.supplier_products.find({"SuppID": supplierID}))

        if not supplier_products:
            return jsonify({"message": "No products found for this supplier"}), 404

        # Convert ObjectId fields to strings
        supplier_products = convert_objectid(supplier_products)

        # Fetch product details and applicable discounts for each supplier product
        for sp in supplier_products:
            # Get product details
            product = mongo.db.products.find_one({"ProdID": sp["ProdID"]})
            sp["ProductDetails"] = convert_objectid(product) if product else None
            
            # Get discounts that match both the supplier ID and the product ID
            discounts = list(mongo.db.discounts.find({
                "SuppID": supplierID,
                "ProdID": sp["ProdID"]
            }))
            sp["Discounts"] = convert_objectid(discounts) if discounts else []
            
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
        if len(supplier_products) == 0:
            products_not_linked = list(mongo.db.products.find())
            products_not_linked = convert_objectid(products_not_linked)
            return jsonify({"message": "Success", "data": products_not_linked}), 200

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
    data = request.get_json()
    
    price1 = data.get("price1")
    amount1 = data.get("amount1")
    price2 = data.get("price2")
    amount2 = data.get("amount2")
    units = data.get("units")

    if not all([price1, amount1, price2, amount2, units]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        try:
            supplier_id = int(supplier_id)
            prod_id = int(SP_ID)
            price1 = float(price1)
            amount1 = int(amount1)
            price2 = float(price2)
            amount2 = int(amount2)
            units = int(units)
            
            # Additional validation
            if price1 <= 0 or price2 <= 0:
                return jsonify({"error": "Prices must be positive"}), 400
            if amount1 <= 0 or amount2 <= 0:
                return jsonify({"error": "Amounts must be positive"}), 400
            if amount2 <= amount1:
                return jsonify({"error": "Amount2 must be greater than Amount1"}), 400
            if units < 0:
                return jsonify({"error": "Units cannot be negative"}), 400
        except ValueError:
            return jsonify({"error": "Invalid numeric values provided"}), 400
        
        highest_sp = mongo.db.supplier_products.find_one(
            sort=[("SupplierProductID", -1)]  # Sort by SupplierProductID in descending order
        )
        
        new_sp_id = 1  # Default if no records exist
        if highest_sp and "SupplierProductID" in highest_sp:
            new_sp_id = highest_sp["SupplierProductID"] + 1
        
        supplier_product = {
            "SupplierProductID": new_sp_id,
            "SuppID": supplier_id,
            "ProdID": prod_id,
            "Price1": price1,
            "Amount1": amount1,
            "Price2": price2,
            "Amount2": amount2,
            "StockQuantity": units
        }

        result = mongo.db.supplier_products.insert_one(supplier_product)
        
        return jsonify({
            "message": "Success", 
            "SupplierProductID": new_sp_id,
            "insertedId": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        print(f"Error adding supplier product: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@supplier_bp.route('/products/<SP_ID>', methods=['DELETE'])
def delete_SP(SP_ID):
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
    
@supplier_bp.route("/products/edit/<SP_ID>", methods=["GET"])
def get_supplier_product_edit_page(SP_ID):
    try:
        check = check_if_admin(request, mongo)
        if check == 'Not signed in':
            return redirect(url_for('loginPage'))
        
        if not SP_ID.isdigit():
            # fix this shit

            return redirect(url_for('supplier_bp.supplier_products'))
            
        SP_ID = int(SP_ID)  

        SP = mongo.db.supplier_products.find_one({'SupplierProductID': SP_ID})
        SP_Supplier = mongo.db.suppliers.find_one({'SuppID':SP['SuppID']})

        if not SP:
            # fix this shit

            return redirect(url_for('supplier_bp.supplier_products'))
        
        product = mongo.db.products.find_one({"ProdID": SP["ProdID"]})
        
        if check == 'Not Admin':
            # For suppliers, verify they own this product
            username = request.cookies.get('username')
            user = mongo.db.users.find_one({"UserName": username})
            
            if not user:
                return redirect(url_for('loginPage'))
                
            supplier = mongo.db.suppliers.find_one({"UserID": user['UserID']})
            if not supplier:
            # fix this shit

                return redirect(url_for('supplier_bp.supplier_products'))
                
            if SP['SuppID'] != supplier['SuppID']:
            # fix this shit
                return redirect(url_for('supplier_bp.supplier_products'))
        
        SP['_id'] = str(SP['_id'])
        if product:
            product['_id'] = str(product['_id'])
        if SP_Supplier:
            SP_Supplier['_id'] = str(SP_Supplier['_id'])
        
        # Pass the data to the template
        return render_template(
            'edit-sp.html',
            SP=SP,
            product=product,
            SP_Supplier = SP_Supplier
        )
    
    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_supplier_product_edit_page: {str(e)}")
        # fix this shit
        return redirect(url_for('supplier_bp.supplier_products'))
    
@supplier_bp.route('/products/<SP_ID>',methods=["PUT"])
def update_SP(SP_ID):
    check = check_if_admin(request, mongo)
    username = request.cookies.get('username')
    
    try:
        if check == 'Not signed in':
            return jsonify({'success': False, 'message': 'אנא התחבר למערכת'}), 401
        
        if not SP_ID.isdigit():
            return jsonify({'success': False, 'message': 'מזהה מוצר לא תקין'}), 400
            
        SP_ID = int(SP_ID)  

        # Find the supplier product
        SP = mongo.db.supplier_products.find_one({'SupplierProductID': SP_ID})
        
        if not SP:
            return jsonify({'success': False, 'message': 'מוצר ספק לא נמצא'}), 404
        
        # Authorization check
        if check == 'Not Admin':
            # For suppliers, verify they own this product
            user = mongo.db.users.find_one({"UserName": username})
            
            if not user:
                return jsonify({'success': False, 'message': 'אנא התחבר למערכת'}), 401
                
            UserSupplier = mongo.db.suppliers.find_one({"UserID": user['UserID']})
            if not UserSupplier:
                return jsonify({'success': False, 'message': 'גישה נדחתה - משתמש אינו ספק'}), 403
                
            if SP['SuppID'] != UserSupplier['SuppID']:
                return jsonify({'success': False, 'message': 'גישה נדחתה - אין הרשאה לעדכן מוצר זה'}), 403
    
        # Get JSON data
        SP_data = request.get_json()
        
        # Validate the incoming data
        if not SP_data:
            return jsonify({'success': False, 'message': 'לא התקבלו נתונים לעדכון'}), 400
            
        # Validate data types and values
        validation_errors = []
        
        try:
            price1 = float(SP_data.get('Price1', 0))
            price2 = float(SP_data.get('Price2', 0))
            amount1 = int(SP_data.get('Amount1', 0))
            amount2 = int(SP_data.get('Amount2', 0))
            stock_quantity = int(SP_data.get('StockQuantity', 0))
            
            if price1 <= 0:
                validation_errors.append("מחיר לכמות ראשונה חייב להיות חיובי")
            if price2 <= 0:
                validation_errors.append("מחיר לכמות שניה חייב להיות חיובי")
            if amount1 <= 0:
                validation_errors.append("כמות ראשונה חייבת להיות חיובית")
            if amount2 <= 0:
                validation_errors.append("כמות שניה חייבת להיות חיובית")
            if amount2 <= amount1:
                validation_errors.append("כמות שניה חייבת להיות גדולה מכמות ראשונה")
            if stock_quantity < 0:
                validation_errors.append("כמות מלאי חייבת להיות חיובית או אפס")
        except (ValueError, TypeError):
            validation_errors.append("ערכים לא תקינים התקבלו")
            
        if validation_errors:
            return jsonify({
                'success': False, 
                'message': 'שגיאת תיקוף נתונים', 
                'errors': validation_errors
            }), 400
                
        # Prepare update data
        dataToUpdate = {
            "Price1": price1,
            "Price2": price2,
            "Amount1": amount1,
            "Amount2": amount2,
            "StockQuantity": stock_quantity
        }

        # Update the document in the correct collection
        result = mongo.db.supplier_products.update_one(
            {'SupplierProductID': SP_ID},  
            {'$set': dataToUpdate}   
        )
        
        if result.modified_count > 0:
            return jsonify({'success': True, 'message': 'המוצר עודכן בהצלחה'}), 200
        elif result.matched_count > 0:
            return jsonify({'success': True, 'message': 'לא בוצעו שינויים במוצר'}), 200
        else:
            return jsonify({'success': False, 'message': 'מוצר לא נמצא'}), 404
    
    except Exception as e:
        print(f"Error updating product: {str(e)}")
        return jsonify({'success': False, 'message': 'אירעה שגיאה בעדכון המוצר'}), 500