from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
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
users_collection = db['users']

# Custom JSON encoder class
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

app.json_encoder = CustomJSONEncoder

@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    user_name = data["user_name"]
    email = data["email"]
    card_number = data.get("card_number", "")

    # Insert the user data into the MongoDB users collection
    user_data = {
        "user_name": user_name,
        "email": email,
        "card_number": card_number
    }
    result = users_collection.insert_one(user_data)

    if result.inserted_id:
        return jsonify({"message": "User created successfully"})
    else:
        return jsonify({"error": "Failed to create user"}), 500
    
@app.route("/users", methods=["GET"])
def get_all_users():
    users = list(users_collection.find())
    return jsonify(users)

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    # Retrieve the user data from the MongoDB users collection
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})

    if user_data:
        return jsonify(user_data)
    else:
        return jsonify({"error": "User not found"}), 404

@app.route("/health")
def health_check():
    return "It's working!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)