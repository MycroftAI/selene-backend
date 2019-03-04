"""Entry point for the API that supports the Mycroft Marketplace."""
from flask import Flask
from flask_restful import Api

from .config import get_config_location
from market_api.endpoints import (
    AvailableSkillsEndpoint,
    SkillDetailEndpoint,
    SkillInstallEndpoint,
    SkillInstallationsEndpoint,
    UserEndpoint
)

# Define the Flask application
market = Flask(__name__)
market.config.from_object(get_config_location())

# Define the API and its endpoints.
market_api = Api(market)
market_api.add_resource(AvailableSkillsEndpoint, '/api/skill/available')
market_api.add_resource(
    SkillDetailEndpoint,
    '/api/skill/detail/<skill_name>'
)
market_api.add_resource(SkillInstallEndpoint, '/api/skill/install')
market_api.add_resource(
    SkillInstallationsEndpoint,
    '/api/skill/installations'
)
market_api.add_resource(UserEndpoint, '/api/user')
