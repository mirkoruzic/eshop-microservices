from flask import Flask, request, jsonify
import requests
import datetime
import os


app = Flask(__name__)

# MongoDB connection configuration
product_service_host = os.getenv('PRODUCT_SERVICE_HOST', 'productservice')
product_service_port = int(os.getenv('PRODUCT_SERVICE_PORT', 5000))

wallet_service_host = os.getenv('WALLET_SERVICE_HOST', 'walletservice')
wallet_service_port = int(os.getenv('WALLET_SERVICE_PORT', 5000))

order_service_host = os.getenv('ORDER_SERVICE_HOST', 'orderservice')
order_service_port = int(os.getenv('ORDER_SERVICE_PORT', 5000))

@app.route("/payments", methods=["POST"])
def process_payment():
    data = request.get_json()
    user_id = data["user_id"]
    user_name = data["user_name"]
    user_card = data["card_number"]
    product_name = data["product_name"]
    product_quantity = data["quantity"]

    # Check if the product exists and get its price and quantity
    product_service_url = "http://{}:{}/products/{}".format(product_service_host, product_service_port, product_name)

    product_response = requests.get(product_service_url)

    if product_response.status_code != 200:
        return jsonify({"error": "Product not found"})

    product_data = product_response.json()
    product_price = product_data["price"]
    product_available_quantity = product_data["quantity"]

    # Calculate the total amount for the product quantity
    total_amount = product_price * product_quantity

    order_service_url = "http://{}:{}/orders".format(order_service_host, order_service_port)
    order_payload = {
        "user_id": user_id,
        "user_name": user_name,
        "product_name": product_name,
        "quantity": product_quantity,
        "amount": total_amount,
        "datetime": datetime.datetime.now().isoformat()  # Add the datetime field
    }
    order_response = requests.post(order_service_url, json=order_payload, headers={"Content-Type": "application/json"})
        
    if order_response.status_code == 200:
    
        # Check if the user's wallet has enough funds
        wallet_service_url = "http://{}:{}/wallets/deduct".format(wallet_service_host, wallet_service_port)
        wallet_payload = {
            "user_name": user_name,
            "card_number": user_card,
            "amount": total_amount  # Pass the total_amount to the wallet service
        }

        print("current_amount:", wallet_payload, flush=True)


        wallet_response = requests.post(wallet_service_url, json=wallet_payload)


        if wallet_response.status_code == 200:
            # Deduct the product quantity from the inventory
            product_service_deduct_url = "http://{}:{}/products/deduct".format(product_service_host, product_service_port)
            product_deduct_payload = {
                "product_name": product_name,
                "quantity": product_quantity
            }
            product_deduct_response = requests.post(product_service_deduct_url, json=product_deduct_payload)
            
            # if product_deduct_response.status_code != 200:
            #     # Revert the wallet deduction if product quantity deduction fails
            #     rollback_payload = {
            #         "user": user_name,
            #         "card_number": user_card,
            #         "amount": total_amount  # Pass the total_amount to the wallet service
            #     }
            #     requests.post(wallet_service_url, json=rollback_payload)
            #     return jsonify({"error": "Failed to deduct product quantity"})

        elif wallet_response.status_code == 404:
            return jsonify({"error": "User not found in wallet"})
        else:
            return jsonify({"error": "Failed to deduct amount from the wallet"})

        return jsonify({"message": "Order created successfully"})

    else:
        # Inform that something is wrong with the Order Service
        return jsonify({"error": "Failed to create order. Please check Order Service for more details."})

@app.route("/health")
def health_check():
    return "It's working!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
