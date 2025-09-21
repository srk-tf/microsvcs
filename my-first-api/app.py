from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import jwt
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret-key'
db = SQLAlchemy(app)

class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	price = db.Column(db.String(100), nullable=True)
	category = db.Column(db.String(100), nullable=False)

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

@app.route('/create-product', methods=['POST'])
def create_product():
	try:
		data = request.get_json()
		new_product = Product(name=data['name'], price=data.get('price'), category=data.get('category'))
		db.session.add(new_product)	
		db.session.commit()

		response = { 
			"message": "Product created successfully",
			"product": {"id": new_product.id, "name": new_product.name, "price": new_product.price, "category": new_product.category}
		}
		return jsonify(response)

	except Exception as e:
		return jsonify({"error": str(e)}), 400

@app.route('/products')
@token_required
def get_all_products():
	products = Product.query.all()
	product_list = [{"id": product.id, "name": product.name, "price": product.price, "category": product.category} for product in products]
	return jsonify(product_list)

@app.route('/products/category/<category_name>')
def get_all_category(category_name):
	products = Product.query.filter_by(category=category_name).all()
	product_list = [{"id": product.id, "name": product.name, "price": product.price, "category": product.category} for product in products]
	return jsonify(product_list)

@app.route('/update-product/<int:product_id>', methods=['PUT'])
def update_product_price(product_id):
	try:
		data = request.get_json()
		product = Product.query.get(product_id)

		if not product:
			return jsonify({"error": "Product not found"}), 404

		product.price = data['price']
		db.session.commit()

		response = {
			"message": "Product updated successfully",
			"product": {"id": product.id, "name": product.name, "price": product.price, "category": product.category}
			}

		return jsonify(response)

	except Exception as e:
		return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug=True)