"""Entry point for the API that supports the Mycroft Marketplace."""
from flask import Flask

from selene.api import get_base_config, selene_api, SeleneResponse
from selene.api.endpoints import AccountEndpoint, AgreementsEndpoint
from selene.util.log import configure_logger
from .endpoints.device_count import DeviceCountEndpoint
from .endpoints.skills import SkillsEndpoint
from .endpoints.skill_settings import SkillSettingsEndpoint

_log = configure_logger('account_api')


# Define the Flask application
acct = Flask(__name__)
acct.config.from_object(get_base_config())
acct.response_class = SeleneResponse
acct.register_blueprint(selene_api)

acct.add_url_rule(
    '/api/account',
    view_func=AccountEndpoint.as_view('account_api'),
    methods=['GET', 'POST']
)
acct.add_url_rule(
    '/api/agreement/<string:agreement_type>',
    view_func=AgreementsEndpoint.as_view('agreements_api'),
    methods=['GET']
)

skill_endpoint = SkillsEndpoint.as_view('skill_endpoint')
acct.add_url_rule(
    '/api/skills',
    view_func=skill_endpoint,
    methods=['GET']
)

setting_endpoint = SkillSettingsEndpoint.as_view('setting_endpoint')
acct.add_url_rule(
    '/api/skills/<string:skill_id>/settings',
    view_func=setting_endpoint,
    methods=['GET', 'PUT']
)

device_count_endpoint = DeviceCountEndpoint.as_view('device_count_endpoint')
acct.add_url_rule(
    '/api/device-count',
    view_func=device_count_endpoint,
    methods=['GET']
)
