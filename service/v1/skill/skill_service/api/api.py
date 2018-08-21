"""Define the API Flask application and its endpoints"""

from flask import Flask
from flask_restful import Api

from skill_service.api.endpoints import AllSkillsEndpoint, SkillDetailEndpoint
# from .config import get_config_location


skill = Flask(__name__)
# skill.config.from_object(get_config_location())

skill_api = Api(skill)
skill_api.add_resource(AllSkillsEndpoint, '/skill/all')
skill_api.add_resource(SkillDetailEndpoint, '/skill/id/<string:skill_id>')
