from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database import User, db

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.post('/signup')
def register():
    db.create_all()
    email=request.json["email"]
    password=request.json["password"]

    if len(password)<6:
        return jsonify({'error': 'Password is too short'}), 400
    
    if not validators.email(email):
        return jsonify({'error': 'Email is not valid'}), 400

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': 'Email is taken'}), 409      
    
    pwd_hash=generate_password_hash(password) #store hashed pass in db
    user=User(email=email, password=pwd_hash) #create a user
    db.session.add(user) #add the user to db
    db.session.commit()

    return jsonify({'message': 'User created', 
    'user':{'email': email}}), 201
  