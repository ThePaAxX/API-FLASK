import os
import secrets

from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask import jsonify
from flask_cors import CORS
from datetime import timedelta

from db import db
from blocklist import BLOCKLIST
import models

from resources.item  import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag   import blp as TagBlueprint
from resources.user  import blp as UserBlueprint

def create_app(db_url=None):
    app = Flask(__name__)

    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['API_TITLE'] = 'Stores REST API'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.0.3'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'http://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv('DATABASE_URL', 'sqlite:///data.db')
    app.config['SQLALCHEMY_TRACK_MOFIFICATION'] = False
    db.init_app(app)

    api = Api(app)

    app.config['JWT_SECRET_KEY'] = '122980922952672538296416966144101176097'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=60)
    # Activa JWT en cookies
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  
    app.config["JWT_COOKIE_SECURE"] = False  # True en producción con HTTPS
    app.config["JWT_COOKIE_SAMESITE"] = "None"  # Necesario si frontend y backend están en diferentes dominios
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Actívalo en prod si quieres CSRF tokens extra

    jwt = JWTManager(app)

    CORS(app, resources={r"/*": {
        "origins": ['http://localhost:3000'],
        "supports_credentials": "True",
        "allow_methods": ["GET", "POST", "PUT", "DELETE"],
        }})

    # Esta seccion es para manejar el bloqueo y el logout de la sesion de los usuarios
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({'message': 'The token has been revoked.', 'error': 'token_revoked'}),
            401
        )

    # En este trozo de codigo podremos agregar un valor personalizado al token
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # Aca puede ir una logica para la bd
        if identity == '1':
            user = models.UserModel.query.filter(models.UserModel.id == identity).first()
            if user:
                return {
                    'is_admin': True,
                    'username': user.username
                    }
        
        return {'is_admin': False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({'message': 'The token has expired.', 'error': 'token_expired'}),
            401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({'message': 'Signature verification failed.', 'error': 'invalid_token'}),
            401
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    'description': 'Request does not contain an access token.',
                    'error': 'authorization_required'
                }
            ),
            401
        )

    with app.app_context():
        db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app