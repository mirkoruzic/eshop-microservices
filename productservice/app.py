from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import json
import os


app = Flask(__name__)

# MongoDB connection configuration
# MongoDB connection configuration
mongo_host = os.getenv('MONGO_HOST', 'mongodb')
mongo_port = int(os.getenv('MONGO_PORT', 27017))
mongo_username = os.getenv('MONGO_USERNAME', 'admin')
mongo_password = os.getenv('MONGO_PASSWORD', 'admin123')
mongo_db = os.getenv('MONGO_DB', 'eshopdb')

# MongoDB client initialization
mongo_client = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/')
db = mongo_client[mongo_db]
products_collection = db['products']

# Custom JSON encoder class
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)
    
app.json_encoder = CustomJSONEncoder


@app.route("/products", methods=["GET"])
def get_all_users():
    products = list(products_collection.find())
    return jsonify(products)


@app.route("/products", methods=["POST"])
def create_or_update_product():
    data = request.get_json()
    product_name = data["product_name"]
    price = data["price"]
    quantity = data["quantity"]

    # Check if the product already exists in the database
    existing_product = products_collection.find_one({"product_name": product_name})

    if existing_product:
        # Update the quantity of the existing product by adding the quantity from the request
        product_id = existing_product["_id"]
        current_quantity = existing_product["quantity"]
        new_quantity = current_quantity + quantity

        update_result = products_collection.update_one(
            {"_id": product_id},
            {"$set": {"quantity": new_quantity, "price": price}}
        )

        if update_result.modified_count > 0:
            return jsonify({"message": "Product updated successfully"})
        else:
            return jsonify({"error": "Failed to update product"}), 500
    else:
        # Generate a new product ID
        product_id = str(ObjectId())

        # Insert the new product into the database
        product_data = {
            "_id": product_id,
            "product_name": product_name,
            "price": price,
            "quantity": quantity
        }
        result = products_collection.insert_one(product_data)

        if result.inserted_id:
            return jsonify({"message": "Product created successfully"})
        else:
            return jsonify({"error": "Failed to create product"}), 500


        
@app.route("/products/deduct", methods=["POST"])
def deduct_product_quantity():
    data = request.get_json()
    product_name = data["product_name"]
    quantity = data["quantity"]

    # Check if the product exists in the database
    product = products_collection.find_one({"product_name": product_name})

    if product:
        current_quantity = product["quantity"]
        if current_quantity >= quantity:
            new_quantity = current_quantity - quantity
            products_collection.update_one({"product_name": product_name}, {"$set": {"quantity": new_quantity}})
            return jsonify({"message": "Product quantity deducted successfully"})
        else:
            return jsonify({"error": "Insufficient product quantity"})
    else:
        return jsonify({"error": "Product not found"})

@app.route("/products/<product_name>", methods=["GET"])
def get_product(product_name):
    # Retrieve the product data from the MongoDB products collection
    product_data = products_collection.find_one({"product_name": product_name})

    if product_data:
        return jsonify(product_data)
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route("/health")
def health_check():
    return "It's working!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)