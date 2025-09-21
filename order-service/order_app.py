from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Order(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, nullable=False)
	quantity = db.Column(db.Integer, nullable=False)
	total_price = db.Column(db.String(50), nullable=False)
	customer_name = db.Column(db.String(100), nullable=False)


@app.route('/create-order', methods=['POST'])
def create_order():
	try:
		data = request.get_json()
		product_response = requests.get(f'http://127.0.0.1:5000/products')
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
