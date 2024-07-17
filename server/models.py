from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from . import db  # Assuming db is your SQLAlchemy instance

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server/restaurants.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    reservations = db.relationship('Reservation', backref='user', lazy=True)


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    restaurant_name = db.Column(db.String(100), nullable=False)
    guest = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{
        'id': restaurant.id,
        'name': restaurant.name,
        'location': restaurant.location,
        'description': restaurant.description,
        'image': restaurant.image
    } for restaurant in restaurants])


@app.route('/restaurants', methods=['POST'])
def add_restaurant():
    data = request.json
    new_restaurant = Restaurant(
        name=data['name'],
        location=data['location'],
        description=data['description'],
        image=data['image']
    )
    db.session.add(new_restaurant)
    db.session.commit()
    return jsonify({
        'id': new_restaurant.id,
        'name': new_restaurant.name,
        'location': new_restaurant.location,
        'description': new_restaurant.description,
        'image': new_restaurant.image
    })


if __name__ == '__main__':
    app.run(debug=True)
