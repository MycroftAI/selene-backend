from flask import Flask
from flask_restful import Api

from .config import get_config_location
from market_api.endpoints import (
    SkillSummaryView,
    SkillDetailView,
    SkillInstallView,
    UserView
)


marketplace = Flask(__name__)
marketplace.config.from_object(get_config_location())

marketplace_api = Api(marketplace)
marketplace_api.add_resource(SkillSummaryView, '/api/skills')
marketplace_api.add_resource(SkillDetailView, '/api/skill/<skill_id>')
marketplace_api.add_resource(SkillInstallView, '/api/install-skill')
marketplace_api.add_resource(UserView, '/api/user')
