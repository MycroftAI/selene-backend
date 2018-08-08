from flask import Flask
from flask_restful import Api

from .authorize import AuthorizeView
from .config import get_config_location


login = Flask(__name__)
login.config.from_object(get_config_location())

login_api = Api(login)
login_api.add_resource(AuthorizeView, '/api/auth')
