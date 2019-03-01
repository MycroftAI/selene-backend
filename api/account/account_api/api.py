"""Entry point for the API that supports the Mycroft Marketplace."""
from flask import Flask

from selene.api import get_base_config, selene_api, SeleneResponse
from selene.api.endpoints import AccountEndpoint, AgreementsEndpoint
from selene.util.log import configure_logger
from  .endpoints import SkillSettingsEndpoint

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
acct.add_url_rule(
    '/api/skill',
    view_func=SkillSettingsEndpoint.as_view('skill_api'),
    methods=['GET', 'POST']
)
