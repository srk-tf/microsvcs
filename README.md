# Microservices Project with JWT Authentication

A distributed microservices system built with Python/Flask demonstrating service-to-service communication, JWT authentication, and database integration.

## Architecture

```
┌─────────────────┐    HTTP + JWT    ┌─────────────────┐
│  Order Service  │ ────────────────▶ │ Product Service │
│   Port: 5001    │                  │   Port: 5000    │
│   Database:     │                  │   Database:     │
│   orders.db     │                  │   products.db   │
└─────────────────┘                  └─────────────────┘
```

## Services

### Product Service (Port 5000)
- **Database**: SQLite (`products.db`)
- **Authentication**: JWT token-based
- **Endpoints**:
  - `POST /get-token` - Generate JWT token
  - `GET /products` - List all products (requires auth)
  - `GET /products/category/<category>` - Filter by category (requires auth)
  - `POST /create-product` - Create new product
  - `PUT /update-product/<id>` - Update product price

### Order Service (Port 5001)
- **Database**: SQLite (`orders.db`)
- **Dependencies**: Calls Product Service for validation
- **Endpoints**:
  - `POST /create-order` - Create new order (auto-authenticates with Product Service)
  - `GET /orders` - List all orders

## Setup and Installation

### Prerequisites
```bash
pip3 install flask flask-sqlalchemy pyjwt requests
```

### Running the Services

1. **Start Product Service:**
```bash
cd my-first-api
python3 app.py
# Runs on http://127.0.0.1:5000
```

2. **Start Order Service (in new terminal):**
```bash
cd order-service
python3 order_app.py
# Runs on http://127.0.0.1:5001
```

## API Usage Examples

### Create a Product
```bash
curl -X POST http://127.0.0.1:5000/create-product \
  -H "Content-Type: application/json" \
  -d '{"name":"iPhone", "price":"50000", "category":"Electronics"}'
```

### Get Authentication Token
```bash
curl -X POST http://127.0.0.1:5000/get-token \
  -H "Content-Type: application/json" \
  -d '{"service_name": "order-service"}'
```

### List Products (with authentication)
```bash
curl -X GET http://127.0.0.1:5000/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Create an Order
```bash
curl -X POST http://127.0.0.1:5001/create-order \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2, "customer_name": "John Doe"}'
```

## Key Features Implemented

- ✅ **REST API Design** - Standard HTTP methods and JSON responses
- ✅ **Database Integration** - SQLAlchemy ORM with SQLite
- ✅ **Microservices Architecture** - Independent services with separate databases
- ✅ **Service-to-Service Communication** - HTTP-based inter-service calls
- ✅ **JWT Authentication** - Token-based security between services
- ✅ **CRUD Operations** - Complete Create, Read, Update operations
- ✅ **Data Validation** - Cross-service product validation
- ✅ **Error Handling** - Proper HTTP status codes and error responses

## Technical Stack

- **Language**: Python 3.x
- **Framework**: Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (PyJWT)
- **HTTP Client**: Requests library
- **Architecture**: Microservices

## Project Learning Outcomes

This project demonstrates practical experience with:
- Building distributed systems
- Implementing authentication between services
- Database design and ORM usage
- RESTful API development
- Service integration and communication
- Error handling and debugging
- Real-world development patterns

## Future Enhancements

- [ ] Add HTTPS/TLS encryption
- [ ] Implement service discovery
- [ ] Add logging and monitoring
- [ ] Deploy to cloud platform (AWS/Docker)
- [ ] Add automated testing
- [ ] Implement circuit breakers for resilience
