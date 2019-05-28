from ..entity.display import SkillDisplay
from ...repository_base import RepositoryBase


class SkillDisplayRepository(RepositoryBase):
    def __init__(self, db):
        super(SkillDisplayRepository, self).__init__(db, __file__)

        # TODO: Change this to a value that can be passed in
        self.core_version = '19.02'

    def get_display_data_for_skills(self):
        return self._select_all_into_dataclass(
            dataclass=SkillDisplay,
            sql_file_name='get_display_data_for_skills.sql',
            args=dict(core_version=self.core_version)
        )

    def get_display_data_for_skill(self, skill_display_id) -> SkillDisplay:
        return self._select_one_into_dataclass(
            dataclass=SkillDisplay,
            sql_file_name='get_display_data_for_skill.sql',
            args=dict(skill_display_id=skill_display_id)
        )

    def upsert(self, skill_display: SkillDisplay):
        db_request = self._build_db_request(
            sql_file_name='upsert_skill_display_data.sql',
            args=dict(
                skill_id=skill_display.skill_id,
                core_version=skill_display.core_version,
                display_data=skill_display.display_data,
            )
        )

        self.cursor.insert(db_request)
