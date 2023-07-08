from flask import Flask, jsonify, request
import psycopg2
import os
import random
import string
from bson import ObjectId
import json

app = Flask(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)
app.json_encoder = CustomJSONEncoder


# PostgreSQL connection configuration
postgres_host = os.getenv('POSTGRES_HOST', 'postgresql')
postgres_port = os.getenv('POSTGRES_PORT', '5432')
postgres_username = os.getenv('POSTGRES_USER', 'postgres')
postgres_password = os.getenv('POSTGRES_PASSWORD', 'password')
postgres_db = os.getenv('POSTGRES_DB', 'walletdb')

# PostgreSQL connection initialization
postgres_client = psycopg2.connect(
    host=postgres_host,
    port=postgres_port,
    user=postgres_username,
    password=postgres_password,
    database=postgres_db
)

# Create the wallet table if it doesn't exist
with postgres_client.cursor() as cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id VARCHAR(10) PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            card_number VARCHAR(255) NOT NULL,
            amount INTEGER NOT NULL
        )
    """)
    postgres_client.commit()

@app.route("/wallets", methods=["GET"])
def get_all_wallets():
    with postgres_client.cursor() as cursor:
        cursor.execute("SELECT * FROM wallets")
        wallets = cursor.fetchall()
        return jsonify(wallets)
    
@app.route('/wallets/add', methods=['POST'])
def create_or_update_wallet():
    data = request.get_json()
    user_name = data.get('user_name')
    card_number = data.get('card_number')
    amount = data.get('amount')

    with postgres_client.cursor() as cursor:
        cursor.execute("SELECT * FROM wallets WHERE user_name = %s AND card_number = %s", (user_name, card_number))
        wallet = cursor.fetchone()

        if wallet:
            current_amount = wallet[3]
            if amount > 0:
                new_amount = current_amount + int(amount)
                cursor.execute("UPDATE wallets SET amount = %s WHERE id = %s", (new_amount, wallet[0]))
                postgres_client.commit()
                return jsonify({"message": "Wallet updated"})
            else:
                return jsonify({"error": "Invalid amount"})
        else:
            if amount > 0:
                wallet_id = generate_random_id()
                cursor.execute("INSERT INTO wallets (id, user_name, card_number, amount) VALUES (%s, %s, %s, %s)",
                               (wallet_id, user_name, card_number, int(amount)))
                postgres_client.commit()
                return jsonify({"message": "Wallet created", "wallet_id": wallet_id}), 201
            else:
                return jsonify({"error": "Invalid amount"})

@app.route("/wallets/deduct", methods=["POST"])
def deduct_amount():
    data = request.get_json()
    user_name = data["user_name"]
    card_number = data["card_number"]
    amount = data["amount"]

    with postgres_client.cursor() as cursor:
        cursor.execute("SELECT * FROM wallets WHERE user_name = %s AND card_number = %s", (user_name, card_number))
        wallet = cursor.fetchone()

        if wallet:
            current_amount = wallet[3]

            if current_amount >= amount:
                updated_amount = current_amount - amount
                cursor.execute("UPDATE wallets SET amount = %s WHERE id = %s", (updated_amount, wallet[0]))
                postgres_client.commit()
                return jsonify({"message": "Amount deducted from the wallet"})
            else:
                return jsonify({"error": "Insufficient funds in the wallet"})
        else:
            return jsonify({"error": "User not found in wallet"})

@app.route("/health")
def health_check():
    return "It's working!"

def generate_random_id():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(10))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
