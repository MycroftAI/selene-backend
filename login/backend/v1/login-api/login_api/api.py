from flask import Flask, request
from flask_restful import Api

from .endpoints import (
    AuthenticateAntisocialEndpoint,
    AuthenticateSocialEndpoint,
    AuthorizeFacebookEndpoint,
    AuthorizeGithubEndpoint,
    AuthorizeGoogleEndpoint,
    LogoutEndpoint
)
from .config import get_config_location
# Initialize the Flask application and the Flask Restful API
login = Flask(__name__)
login.config.from_object(get_config_location())
login_api = Api(login, catch_all_404s=True)

# Define the endpoints
login_api.add_resource(AuthenticateAntisocialEndpoint, '/api/antisocial')
login_api.add_resource(AuthorizeFacebookEndpoint, '/api/social/facebook')
login_api.add_resource(AuthorizeGithubEndpoint, '/api/social/github')
login_api.add_resource(AuthorizeGoogleEndpoint, '/api/social/google')
login_api.add_resource(AuthenticateSocialEndpoint, '/api/social')
login_api.add_resource(LogoutEndpoint, '/api/logout')


def add_cors_headers(response):
    """Allow any application to logout"""
    if 'logout' in request.url:
        response.headers['Access-Control-Allow-Origin'] = '*'
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = (
                'DELETE, GET, POST, PUT'
            )
            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                response.headers['Access-Control-Allow-Headers'] = headers
    return response


#login.after_request(add_cors_headers)
