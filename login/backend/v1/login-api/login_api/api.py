from flask import Flask
from flask_restful import Api

from .endpoints import AuthenticateAntisocialEndpoint, LogoutEndpoint
from .facebook import AuthorizeFacebookView
from .config import get_config_location

BASE_URL = '/api/auth/'
login = Flask(__name__)
login.config.from_object(get_config_location())
login_api = Api(login, catch_all_404s=True)

antisocial_view_url = BASE_URL + 'antisocial'
facebook_view_url = BASE_URL + 'social/facebook'

login_api.add_resource(AuthenticateAntisocialEndpoint, antisocial_view_url)
login_api.add_resource(AuthorizeFacebookView, facebook_view_url)

logout_view_url = BASE_URL + 'logout'
login_api.add_resource(LogoutEndpoint, logout_view_url)
