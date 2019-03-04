"""Define the API that will support Mycroft single sign on (SSO)."""

from flask import Flask, request

from selene.api import get_base_config, selene_api, SeleneResponse
from selene.util.log import configure_logger

from .endpoints import (
    AuthenticateInternalEndpoint,
    LogoutEndpoint,
    ValidateFederatedEndpoint
)

_log = configure_logger('sso_api')

# Define the Flask application
sso = Flask(__name__)
sso.config.from_object(get_base_config())
sso.response_class = SeleneResponse
sso.register_blueprint(selene_api)

# Define the endpoints
sso.add_url_rule(
    '/api/internal-login',
    view_func=AuthenticateInternalEndpoint.as_view('internal_login'),
    methods=['GET']
)
sso.add_url_rule(
    '/api/validate-federated',
    view_func=ValidateFederatedEndpoint.as_view('federated_login'),
    methods=['POST']
)
sso.add_url_rule(
    '/api/logout',
    view_func=LogoutEndpoint.as_view('logout'),
    methods=['GET']
)


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
