from flask import Flask, request
from flask_restful import Api

from .endpoints import (
    AuthenticateAntisocialEndpoint,
    SocialLoginTokensEndpoint,
    AuthorizeFacebookEndpoint,
    AuthorizeGithubEndpoint,
    AuthorizeGoogleEndpoint,
    LogoutEndpoint
)
from .config import get_config_location
# Initialize the Flask application and the Flask Restful API
sso = Flask(__name__)
sso.config.from_object(get_config_location())
sso_api = Api(sso, catch_all_404s=True)

# Define the endpoints
sso_api.add_resource(AuthenticateAntisocialEndpoint, '/api/antisocial')
sso_api.add_resource(AuthorizeFacebookEndpoint, '/api/social/facebook')
sso_api.add_resource(AuthorizeGithubEndpoint, '/api/social/github')
sso_api.add_resource(AuthorizeGoogleEndpoint, '/api/social/google')
sso_api.add_resource(SocialLoginTokensEndpoint, '/api/social/tokens')
sso_api.add_resource(LogoutEndpoint, '/api/logout')


def add_cors_headers(response):
    """Allow any application to logout"""
    # if 'logout' in request.url:
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = (
            'DELETE, GET, POST, PUT'
        )
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response


sso.after_request(add_cors_headers)
