from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database import User, db
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required, get_jwt_identity



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


@auth.post('/login')
def auth_user():
    # db.create_all()
    email=request.json.get('email', '') #default ''
    password=request.json.get('password', '')#cos pas is key

    user=User.query.filter_by(email=email).first()

    if user:
        is_pass_authorized = check_password_hash(user.password, password)

        if is_pass_authorized:
            refresh=create_refresh_token(identity=user.id)
            access=create_access_token(identity=user.id)

            return jsonify({
                'user':{
                    'refresh':refresh,
                    'access':access,
                    'email':email
                }
                }), 200

    return jsonify({'error': 'Invalid credentials'}), 401


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_auth_user_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({'access':access}), 200