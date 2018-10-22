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


marketplace = Flask(__name__)
marketplace.config.from_object(get_config_location())

marketplace_api = Api(marketplace)
marketplace_api.add_resource(AvailableSkillsEndpoint, '/api/skill/available')
marketplace_api.add_resource(
    SkillDetailEndpoint,
    '/api/skill/detail/<skill_name>'
)
marketplace_api.add_resource(SkillInstallEndpoint, '/api/skill/install')
marketplace_api.add_resource(
    SkillInstallationsEndpoint,
    '/api/skill/installations'
)
marketplace_api.add_resource(UserEndpoint, '/api/user')
