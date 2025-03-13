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

        # Find a matching discount for this supplier and product
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
            
            # Only attach the discount if it exists for this supplier
            if supplier_discount:
                supplier_info["Discount"] = supplier_discount

            suppliers_info.append(supplier_info)
    return render_template('product-info.html', suppliers=suppliers_info,product=product)
  
@product_bp.route("/<product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    return jsonify({"message": f"Product {product_id} updated", "data": data}), 200

# @product_bp.route("/<product_id>", methods=["DELETE"])
# def delete_product(product_id):
#     return jsonify({"message": f"Product {product_id} deleted"}), 200
