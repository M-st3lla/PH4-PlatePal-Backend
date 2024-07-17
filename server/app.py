from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta 
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server/restaurants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)  # Optional: Set token expiration

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    reservations = db.relationship('Reservation', backref='user', lazy=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    restaurant_name = db.Column(db.String(100), nullable=False)
    guest = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class ReservationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        load_instance = True

user_schema = UserSchema()
reservation_schema = ReservationSchema()

@app.route('/create_reservation', methods=['POST'])
@jwt_required()
def create_reservation():
    try:
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        contact = data.get('contact')
        date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        restaurant_name = data.get('restaurant_name')
        guest = int(data.get('guest'))

        current_user = get_jwt_identity()
        user = User.query.filter_by(id=current_user['id']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        new_reservation = Reservation(
            name=name,
            email=email,
            contact=contact,
            date=date,
            restaurant_name=restaurant_name,
            guest=guest,
            user_id=user.id
        )

        db.session.add(new_reservation)
        db.session.commit()

        return jsonify({"message": "Reservation created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
