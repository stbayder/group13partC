from flask import Blueprint, request, jsonify,render_template,redirect,url_for
from utilities.db_connector import mongo
from utilities.db_connector import hash_password, generate_password
from utilities.utils import check_if_admin

user_bp = Blueprint("users", __name__)


@user_bp.route('/<username>', methods=['GET'])
def getUserData(username):
    user = mongo.db.users.find_one({"UserName": username})
    if user:
        return {
            'UserName':user['UserName'],
            'Email':user["Email"],
            'Role':user["Role"],
            'FullName':user["FullName"]
        }
    else:
        return jsonify({"error": "Invalid credentials, username not found"}), 401  # User not found
@user_bp.route("/<user_id>", methods=["GET"])\

@user_bp.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user_id = int(user_id)
        
        user = mongo.db.users.find_one({"UserID": user_id})
        
        if user:
            user['_id'] = str(user['_id'])
            # Remove password hash from response
            if 'Password' in user:
                del user['Password']
                
            # If the user is a supplier, fetch and include supplier details
            if user['Role'] == 'Supplier':
                supplier = mongo.db.suppliers.find_one({"UserID": user_id})
                if supplier:
                    supplier['_id'] = str(supplier['_id'])
                    user['supplier_details'] = supplier
                    
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found"}), 404
            
    except ValueError:
        return jsonify({"error": "Invalid user ID format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/", methods=["POST"])
def create_user():
    try:
        data = request.json
        
        required_fields = ["UserName", "Email", "Role", "FullName"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        if mongo.db.users.find_one({"UserName": data["UserName"]}):
            return jsonify({"error": "Username already exists"}), 409
            
        if mongo.db.users.find_one({"Email": data["Email"]}):
            return jsonify({"error": "Email already exists"}), 409
            
        if data["Role"] == "Supplier":
            supplier_fields = ["SuppName", "Phone", "Address","SuppEmail"]
            for field in supplier_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required supplier field: {field}"}), 400
        
        # Get the next available UserID
        last_user = mongo.db.users.find_one(sort=[("UserID", -1)])
        new_user_id = last_user["UserID"] + 1 if last_user else 1
        
        # Create new user document
        new_user = {
            "UserID": new_user_id,
            "UserName": data["UserName"],
            "Email": data["Email"],
            "Role": data["Role"],
            "FullName": data["FullName"]
        }
        
        # Handle password - either use provided password or generate a random one
        password = data.get("Password")
        if not password:
            password = generate_password()
            generated_password = password  # Save for response
        
        new_user["Password"] = hash_password(password).decode('utf-8')
        
        result = mongo.db.users.insert_one(new_user)
        
        # If the user is a supplier, create a supplier record
        supplier_data = None
        if data["Role"] == "Supplier":
            # Get the next available SuppID
            last_supplier = mongo.db.suppliers.find_one(sort=[("SuppID", -1)])
            new_supp_id = last_supplier["SuppID"] + 1 if last_supplier else 1
            
            # Create supplier document
            new_supplier = {
                "SuppID": new_supp_id,
                "SuppName": data["SuppName"],
                "Email": data["SuppEmail"],
                "Phone": data["Phone"],
                "Address": data["Address"],
                "UserID": new_user_id
            }
            
            supplier_result = mongo.db.suppliers.insert_one(new_supplier)
            new_supplier["_id"] = str(supplier_result.inserted_id)
            supplier_data = new_supplier
        
        response_user = new_user.copy()
        del response_user["Password"]  # Don't return password hash
        response_user["_id"] = str(result.inserted_id)
        
        response = {
            "message": "User created successfully", 
            "user": response_user
        }
        
        # Add generated password to response if one was created
        if 'generated_password' in locals():
            response["generated_password"] = generated_password
            
        # Add supplier data if created
        if supplier_data:
            response["supplier_details"] = supplier_data
            
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/<user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user_id = int(user_id)
        data = request.json
        
        existing_user = mongo.db.users.find_one({"UserID": user_id})
        if not existing_user:
            return jsonify({"error": "User not found"}), 404
        
        # Prevent changing UserID
        if "UserID" in data:
            return jsonify({"error": "UserID cannot be modified"}), 400
            
        if "UserName" in data and data["UserName"] != existing_user["UserName"]:
            if mongo.db.users.find_one({"UserName": data["UserName"]}):
                return jsonify({"error": "Username already exists"}), 409
                
        if "Email" in data and data["Email"] != existing_user["Email"]:
            if mongo.db.users.find_one({"Email": data["Email"]}):
                return jsonify({"error": "Email already exists"}), 409
                
        if "Role" in data and data["Role"] != existing_user["Role"]:
            if existing_user["Role"] == "Supplier" or data["Role"] == "Supplier":
                return jsonify({"error": "Cannot change user role to or from Supplier"}), 400
        
        user_update_fields = {}
        supplier_update_fields = {}
        
        for key, value in data.items():
            if key not in ["UserID", "_id", "SuppName", "Phone", "Address", "SuppID"]:
                if key == "Password" and value:
                    # Hash new password if provided
                    user_update_fields[key] = hash_password(value).decode('utf-8')
                elif key == "Email":
                    user_update_fields[key] = value
                else:
                    user_update_fields[key] = value
        
        if existing_user["Role"] == "Supplier":
            existing_supplier = mongo.db.suppliers.find_one({"UserID": user_id})
            if existing_supplier:
                if "SuppName" in data:
                    supplier_update_fields["SuppName"] = data["SuppName"]
                if "Phone" in data:
                    supplier_update_fields["Phone"] = data["Phone"]
                if "Address" in data:
                    supplier_update_fields["Address"] = data["Address"]
                if "SuppEmail" in data:
                    supplier_update_fields["Email"] = data["SuppEmail"]
    
        # Update user document if there are fields to update
        user_updated = False
        if user_update_fields:
            user_result = mongo.db.users.update_one(
                {"UserID": user_id},
                {"$set": user_update_fields}
            )
            user_updated = user_result.modified_count > 0
        
        # Update supplier document if there are fields to update
        supplier_updated = False
        if supplier_update_fields and existing_user["Role"] == "Supplier":
            supplier_result = mongo.db.suppliers.update_one(
                {"UserID": user_id},
                {"$set": supplier_update_fields}
            )
            supplier_updated = supplier_result.modified_count > 0
        
        if user_updated or supplier_updated:
            # Get the updated records
            updated_user = mongo.db.users.find_one({"UserID": user_id})
            updated_user["_id"] = str(updated_user["_id"])
            # Remove password hash from response
            if 'Password' in updated_user:
                del updated_user['Password']
            
            response = {
                "message": f"User {user_id} updated successfully",
                "user": updated_user,
                "user_updated": user_updated
            }
            
            # Include supplier details if applicable
            if existing_user["Role"] == "Supplier":
                updated_supplier = mongo.db.suppliers.find_one({"UserID": user_id})
                if updated_supplier:
                    updated_supplier["_id"] = str(updated_supplier["_id"])
                    response["supplier_details"] = updated_supplier
                    response["supplier_updated"] = supplier_updated
                    
            return jsonify(response), 200
        else:
            return jsonify({"message": "No changes made"}), 200
            
    except ValueError:
        return jsonify({"error": "Invalid user ID format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user_id = int(user_id)
        
        existing_user = mongo.db.users.find_one({"UserID": user_id})
        if not existing_user:
            return jsonify({"error": "User not found"}), 404
            
        is_supplier = existing_user["Role"] == "Supplier"
        supplier_deleted = False
        
        if is_supplier:
            supplier_result = mongo.db.suppliers.delete_one({"UserID": user_id})
            supplier_deleted = supplier_result.deleted_count > 0
            
            # If supplier exists but couldn't be deleted, return error
            if not supplier_deleted and mongo.db.suppliers.find_one({"UserID": user_id}):
                return jsonify({"error": "Failed to delete associated supplier record"}), 500
        
        user_result = mongo.db.users.delete_one({"UserID": user_id})
        
        if user_result.deleted_count > 0:
            response = {
                "message": f"User {user_id} deleted successfully",
                "user_deleted": True
            }
            
            if is_supplier:
                response["supplier_deleted"] = supplier_deleted
                
            return jsonify(response), 200
        else:
            return jsonify({"error": "Failed to delete user"}), 500
            
    except ValueError:
        return jsonify({"error": "Invalid user ID format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/', methods=['GET'])
def admin_users():
    check = check_if_admin(request,mongo)
    if check == 'Not signed in':
        redirect(url_for('loginPage'))
    elif check == 'Not Admin':
        redirect(url_for('home'))
    
    try:
        users = list(mongo.db.users.find())

        for user in users:
            user['_id'] = str(user['_id'])
            # Remove password hash from response
            if 'Password' in user:
                del user['Password']
            # # If user is a supplier, include supplier details
            # if user['Role'] == 'Supplier':
            #     supplier = mongo.db.suppliers.find_one({"UserID": user['UserID']})
            #     if supplier:
            #         supplier['_id'] = str(supplier['_id'])
            #         user['supplier_details'] = supplier
            
        return render_template('admin-edit-users.html',users =users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
