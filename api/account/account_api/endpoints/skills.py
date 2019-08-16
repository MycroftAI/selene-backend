from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.skill import SkillRepository


class SkillsEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        response_data = self._build_response_data()

        return response_data, HTTPStatus.OK

    def _build_response_data(self):
        skill_repository = SkillRepository(self.db)
        skills = skill_repository.get_skills_for_account(self.account.id)

        response_data = {}
        for skill in skills:
            try:
                response_skill = response_data[skill.family_name]
            except KeyError:
                response_data[skill.family_name] = dict(
                    family_name=skill.family_name,
                    market_id=skill.market_id,
                    name=skill.display_name or skill.family_name,
                    has_settings=skill.has_settings,
                    skill_ids=skill.skill_ids
                )
            else:
                response_skill['skill_ids'].extend(skill.skill_ids)
                if response_skill['market_id'] is None:
                    response_skill['market_id'] = skill.market_id

        return sorted(response_data.values(), key=lambda x: x['name'])
