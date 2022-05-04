from flask import Flask, jsonify
import os
from src.shippingrate import shippingrate, cache
from src.auth import auth
from src.database import db
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
         app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', default=False),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI', default=False),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', default=False),
            SWAGGER={
                 'title': 'Unified API Server', 
                 'uiversion': 3
            },
            CACHE_TYPE=os.environ.get('CACHE_TYPE', default=False),
            CACHE_REDIS_HOST=os.environ.get('CACHE_REDIS_HOST', default=False),
            CACHE_REDIS_PORT=os.environ.get('CACHE_REDIS_PORT', default=False),
            CACHE_REDIS_DB=os.environ.get('CACHE_REDIS_DB', default=False),
            CACHE_REDIS_URL=os.environ.get('CACHE_REDIS_URL', default=False),
            CACHE_DEFAULT_TIMEOUT=os.environ.get('CACHE_DEFAULT_TIMEOUT', default=False)
         )
    else:
         app.config.from_object(test_config)

    db.app = app
    db.init_app(app)
    cache.init_app(app)
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