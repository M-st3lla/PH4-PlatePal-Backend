from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import os

# Initialize Flask app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable CORS
CORS(app)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'restaurants.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    restaurants = db.relationship('Restaurant', backref='user', lazy=True)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Schemas
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class RestaurantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Restaurant

user_schema = UserSchema()
restaurant_schema = RestaurantSchema()
restaurants_schema = RestaurantSchema(many=True)

# Routes
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(message="User registered successfully. Please log in.")

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity={'username': user.username, 'id': user.id})
        return jsonify(access_token=access_token, username=user.username, id=user.id)
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/restaurants', methods=['POST'])
@jwt_required()
def add_restaurant():
    name = request.json['name']
    location = request.json['location']
    description = request.json['description']
    image = request.json['image']
    
    current_user = get_jwt_identity()  # Get current user from JWT token
    user = User.query.filter_by(username=current_user['username']).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    new_restaurant = Restaurant(name=name, location=location, description=description, image=image, user_id=user.id)
    
    db.session.add(new_restaurant)
    db.session.commit()
    
    return restaurant_schema.jsonify(new_restaurant)

@app.route('/restaurants', methods=['GET'])
@jwt_required()
def get_restaurants():
    current_user = get_jwt_identity()  # Get current user from JWT token
    user = User.query.filter_by(username=current_user['username']).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user_restaurants = Restaurant.query.filter_by(user_id=user.id).all()
    result = restaurants_schema.dump(user_restaurants)
    
    return jsonify(result)

# Run the server
if __name__ == '__main__':
    app.run(debug=True, port=5555)
