from flask import Flask
from flask_restful import Api

from .all_skills import AllSkillsView
from .skill_detail import SkillDetailView
# from .config import get_config_location


skill = Flask(__name__)
# skill.config.from_object(get_config_location())

skill_api = Api(skill)
skill_api.add_resource(AllSkillsView, '/skill/all')
skill_api.add_resource(SkillDetailView, '/skill/id/<string:skill_id>')
