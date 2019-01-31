import os

from flask import Flask, request
from flask_restful import Api

from selene.api.base_config import get_base_config

from .endpoints import (
    AuthenticateInternalEndpoint,
    SocialLoginTokensEndpoint,
    AuthorizeFacebookEndpoint,
    AuthorizeGithubEndpoint,
    AuthorizeGoogleEndpoint,
    LogoutEndpoint
)

# Initialize the Flask application and the Flask Restful API
sso = Flask(__name__)
sso.config.from_object(get_base_config())
sso.config['SSO_BASE_URL'] = os.environ['SSO_BASE_URL']

# Initialize the REST API and define the endpoints
sso_api = Api(sso, catch_all_404s=True)
sso_api.add_resource(AuthenticateInternalEndpoint, '/api/antisocial')
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


@sso.teardown_appcontext
def close_db_connections():
    sso.config['DB_CONNECTION_POOL'].close_all()
