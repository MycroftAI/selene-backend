"""Entry point for the API that supports the Mycroft Marketplace."""
from flask import Flask

from selene.api import get_base_config, selene_api, SeleneResponse
from selene.api.endpoints import AccountEndpoint
from selene.util.log import configure_logger
from .endpoints import (
    AvailableSkillsEndpoint,
    SkillDetailEndpoint,
    SkillInstallEndpoint,
    SkillInstallStatusEndpoint
)

_log = configure_logger('market_api')

# Define the Flask application
market = Flask(__name__)
market.config.from_object(get_base_config())
market.response_class = SeleneResponse
market.register_blueprint(selene_api)

# Define the API and its endpoints.
account_endpoint = AccountEndpoint.as_view('account_endpoint')
market.add_url_rule(
    '/api/account',
    view_func=account_endpoint,
    methods=['GET']
)

available_endpoint = AvailableSkillsEndpoint.as_view('available_endpoint')
market.add_url_rule(
    '/api/skills/available',
    view_func=available_endpoint,
    methods=['GET']
)

status_endpoint = SkillInstallStatusEndpoint.as_view('status_endpoint')
market.add_url_rule(
    '/api/skills/status',
    view_func=status_endpoint,
    methods=['GET']
)

skill_detail_endpoint = SkillDetailEndpoint.as_view('skill_detail_endpoint')
market.add_url_rule(
    '/api/skills/<string:skill_display_id>',
    view_func=skill_detail_endpoint,
    methods=['GET']
)

install_endpoint = SkillInstallEndpoint.as_view('install_endpoint')
market.add_url_rule(
    '/api/skills/install',
    view_func=install_endpoint,
    methods=['PUT']
)
