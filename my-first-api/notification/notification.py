from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
import jwt
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notification.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret-key'
db = SQLAlchemy(app)


class Notification(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	related_id = db.Column(db.Integer, nullable=False)
	event_type = db.Column(db.String(50), nullable=False)
	message = db.Column(db.String(200), nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

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

@app.route('/notify', methods=['POST'])
def create_notification():
	try:
		data = request.get_json()
		new_notification = Notification(related_id=data['related_id'], event_type=data['event_type'], message=data['message'])
		db.session.add(new_notification)	
		db.session.commit()

		response = { 
			"message": "Notification created successfully",
			"Notification": {"id": new_notification.id, "name": new_notification.related_id, "event": new_notification.event_type, "message": new_notification.message}
		}
		return jsonify(response), 201

	except Exception as e:
		return jsonify({"error": str(e)}), 400

@app.route('/notifications')
def get_notification():
	notifications = Notification.query.all()
	notification_list = []
	for notification in notifications:
		notification_list.append({
			"id": notification.id,
			"related_id": notification.related_id,
			"event": notification.event_type,
			"message": notification.message,
			"timestamp": notification.timestamp.isoformat()
			})
	return jsonify(notification_list)

if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug=True, port=5002)