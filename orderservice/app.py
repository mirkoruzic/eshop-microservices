from flask import Flask, jsonify, request, abort
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json
import os

app = Flask(__name__)

# MongoDB connection configuration
mongo_host = os.getenv('MONGO_HOST', 'mongodb')
mongo_port = int(os.getenv('MONGO_PORT', 27017))
mongo_username = os.getenv('MONGO_USERNAME', 'admin')
mongo_password = os.getenv('MONGO_PASSWORD', 'admin123')
mongo_db = os.getenv('MONGO_DB', 'eshopdb')

# MongoDB client initialization
mongo_client = MongoClient(f'mongodb://{mongo_username}:{mongo_password}@{mongo_host}:{mongo_port}/')
db = mongo_client[mongo_db]
orders_collection = db['orders']
users_collection = db['users']

# Custom JSON encoder class
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (ObjectId, datetime)):
            return str(o)
        return super().default(o)

app.json_encoder = CustomJSONEncoder

def verify_user(user_id, user_name):
    user = users_collection.find_one({"_id": ObjectId(user_id), "user_name": user_name})
    if user is None:
        abort(404, description="User not found")
    return user is not None


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    user_id = data["user_id"]
    user_name = data["user_name"]
    product_name = data["product_name"]
    quantity = data["quantity"]
    amount = data["amount"]
    date_time = data["datetime"]  # Handle the datetime field

    # Verify if the user exists
    if not verify_user(user_id, user_name):
        return jsonify({"error": "User not found"})

    # Create the order data
    order_data = {
        "user_id": user_id,
        "user_name": user_name,
        "product_name": product_name,
        "quantity": quantity,
        "amount": amount,
        "datetime": date_time
    }

    # Insert the order into the database
    result = orders_collection.insert_one(order_data)

    if result.inserted_id:
        return jsonify({"message": "Order created successfully"})
    else:
        return jsonify({"error": "Failed to create order"}), 500


@app.route("/orders/user/<user_id>", methods=["GET"])
def get_orders_by_user(user_id):
    # Retrieve the orders for the specified user
    orders = list(orders_collection.find({"user_id": user_id}))

    return jsonify(orders)


@app.route("/orders", methods=["GET"])
def get_all_orders():
    orders = list(orders_collection.find())
    for order in orders:
        order["_id"] = str(order["_id"])
        if "date_time" in order:
            order["date_time"] = order["date_time"].strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(orders)

@app.route("/health")
def health_check():
    return "It's working!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
