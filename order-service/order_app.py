from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret-key'
db = SQLAlchemy(app)

class Order(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, nullable=False)
	quantity = db.Column(db.Integer, nullable=False)
	total_price = db.Column(db.String(50), nullable=False)
	customer_name = db.Column(db.String(100), nullable=False)

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.headers.get('Authorization')

		if not token:
			return jsonify({'error': 'Token is missing'}), 401

		try:
			if token.startswith('Bearer '):
				token = token[7:]

			data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
		except jwt.ExpiredSignatureError:
			return jsonify({'error': 'Token has expired'}), 401
		except jwt.InvalidTokenError:
			return jsonify({'error': "Token is invalid"}), 401

		return f(*args, **kwargs)
	return decorated

@app.route('/get-token', methods=['POST'])
def get_token():
	data = request.get_json()
	service_name = data.get('service_name', 'unknown')

	payload = {
		'service_name': service_name,
		'exp': datetime.utcnow() + timedelta(hours=1)
	}

	token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

	return jsonify({
		'token': token,
		'expires_in': 3600
		})


def get_auth_token():
	try:
		response = requests.post('http://127.0.0.1:5000/get-token', json={'service_name': 'order_service'})

		if response.status_code == 200:
			return response.json()['token']
		return None

	except Exception as e:
		print(f"Error getting token: {e}")
		return None

def send_notification(event_type, related_id, message):
 	try:
 		notification_data = {
 			 "event_type": event_type,
 			 "related_id": related_id,
 			 "message": message
 		}

 		response = requests.post('http://127.0.0.1:5002/notify', json=notification_data, headers={'Content-Type': 'application/json'})

 		if response.status_code == 201:
 			print("Notification sent successfully")
 		else:
 			print("Failed to send Notification: {response.status_code}")

 	except Exception as e:
 		print(f"Error sending notification: {e}")

@app.route('/create-order', methods=['POST'])
def create_order():
	try:
		token = get_auth_token()
		if not token:
			return jsonify({"error": "Unable to authenticate"}), 500
		data = request.get_json()
		headers = {'Authorization': f'Bearer {token}'}
		product_response = requests.get(f'http://127.0.0.1:5000/products', headers=headers)
		products = product_response.json()


		product = None

		for p in products:
			if p['id'] == data['product_id']:
				product = p
				break

		if not product:
			return jsonify({"error": "Product not found"}), 404


		total_price = int(product['price']) * data['quantity']

		new_order = Order(
			product_id=data['product_id'],
			quantity=data['quantity'],
			total_price=str(total_price),
			customer_name=data['customer_name']
		)

		db.session.add(new_order)
		db.session.commit()
		print(f"Order Saved with ID: {new_order.id}")

		notification_message = f"Order created for {new_order.customer_name} - Product: {product['name']}, Quantity: {new_order.quantity}"

		send_notification("order_created", new_order.id, notification_message)

		response = {
			"message": "Order created successfully",
			"order": {
				"id": new_order.id,
				"product": product['name'],
				"quantity": new_order.quantity,
				"total_price": new_order.total_price,	
				"customer": new_order.customer_name				
			}
		}
		return jsonify(response)

	except Exception as e:
		return jsonify({"error": str(e)}), 400

@app.route('/orders')
def get_orders():
	orders = Order.query.all()
	print(f"Found {len(orders)} orders")
	order_list = []
	for order in orders:
		order_list.append({
			"id": order.id,
			"product_id": order.product_id,
			"quantity": order.quantity,
			"total_price": order.total_price,
			"customer_name": order.customer_name
			})
	return jsonify(order_list)

if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug=True, port=5001)
