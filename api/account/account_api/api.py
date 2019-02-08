"""Entry point for the API that supports the Mycroft Marketplace."""
from flask import Flask
from flask_restful import Api

from selene.api import AccountEndpoint, get_base_config
from selene.api import JSON_MIMETYPE, output_json

# Define the Flask application
acct = Flask(__name__)
acct.config.from_object(get_base_config())

# Define the API and its endpoints.
acct_api = Api(acct)
acct_api.representations[JSON_MIMETYPE] = output_json
acct_api.add_resource(AccountEndpoint, '/api/account')
