from flask import Flask
from flask_restful import Api

from .config import get_config_location
from market_api.endpoints import (
    SkillSummaryEndpoint,
    SkillDetailEndpoint,
    SkillInstallEndpoint,
    UserEndpoint
)


marketplace = Flask(__name__)
marketplace.config.from_object(get_config_location())

marketplace_api = Api(marketplace)
marketplace_api.add_resource(SkillSummaryEndpoint, '/api/skills')
marketplace_api.add_resource(SkillDetailEndpoint, '/api/skill/<skill_id>')
marketplace_api.add_resource(SkillInstallEndpoint, '/api/install')
marketplace_api.add_resource(UserEndpoint, '/api/user')
