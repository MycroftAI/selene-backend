from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.skill import SkillRepository
from selene.util.db import get_db_connection


class SkillsEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        response_data = self._build_response_data()

        return response_data, HTTPStatus.OK

    def _build_response_data(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            skill_repository = SkillRepository(db)
            skills = skill_repository.get_skills_for_account(self.account.id)

        response_data = []
        for skill in skills:
            response_data.append(dict(
                id=skill.id,
                name=skill.display_name or skill.family_name,
                has_settings=skill.has_settings
            ))

        return sorted(response_data, key=lambda x: x['name'])
