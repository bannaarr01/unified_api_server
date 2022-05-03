from flask import Flask, jsonify
import os
from src.shippingrate import shippingrate
from src.auth import auth
from src.database import db
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
         app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DB_URI=os.environ.get('SQLALCHEMY_DB_URI'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),
            SWAGGER={
                 'title': 'Unified API Server', 
                 'uiversion': 3
            }
         )
    else:
         app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)
    JWTManager(app)
    db.create_all()

    app.register_blueprint(auth)
    app.register_blueprint(shippingrate)   

    Swagger(app, config=swagger_config, template=template)

    #error handling
    @app.errorhandler(404)
    def handle_error_404(ex):
         return jsonify({'error':'Not found'}), 404

    @app.errorhandler(500) #Internal Server Error
    def handle_error_500(ex):
         return jsonify({'error':'Something went wrong, we are working on it'}), 500

    return app 