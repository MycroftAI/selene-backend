from collections import defaultdict

from flask import request
from flask_restful import Resource
import requests

UNDEFINED = 'Undefined'


class SkillSummaryView(Resource):
    def __init__(self):
        self.skills = defaultdict(list)
        self.skill_service_response = None
        self.search_term = None

    def get(self):
        self.skill_service_response = requests.get('http://service.mycroft.test/skill/all')
        if request.query_string:
            self.search_term = request.query_string.decode().lower().split('=')[1]
        self._reformat_skills()
        self._sort_skills()

        return self.skills

    def _reformat_skills(self):
        for skill in self.skill_service_response.json():
            skill_summary = dict(
                id=skill['id'],
                title=skill['title'],
                summary=skill['summary'],
                triggers=skill['triggers']
            )
            if self.search_term is None or self.search_term in skill['title'].lower():
                skill_category = skill.get('category', UNDEFINED)
                self.skills[skill_category].append(skill_summary)

    def _sort_skills(self):
        for skill_category, skills in self.skills.items():
            skills_sorted_by_title = sorted(skills, key=lambda skill: skill['title'])
            self.skills[skill_category] = skills_sorted_by_title


class SkillDetailView(Resource):
    def __init__(self):
        self.skill_service_response = None

    def get(self, skill_id):
        self.skill_service_response = requests.get(
            'http://service.mycroft.test/skill/id/' + skill_id
        )

        return self.skill_service_response.json()
