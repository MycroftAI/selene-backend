from flask import Flask
from flask_restful import Api

from .authorize import AuthorizeAntisocialView
from .config import get_config_location
from .logout import LogoutView

BASE_URL = '/api/auth/'
login = Flask(__name__)
login.config.from_object(get_config_location())
login_api = Api(login, catch_all_404s=True)

antisocial_view_url = BASE_URL + 'antisocial'
login_api.add_resource(AuthorizeAntisocialView, antisocial_view_url)

logout_view_url = BASE_URL + 'logout'
login_api.add_resource(LogoutView, logout_view_url)
