from selene.data.repository_base import RepositoryBase


class DeviceSkillRepository(RepositoryBase):

    def __init__(self, db):
        super(DeviceSkillRepository, self).__init__(db, __file__)

    def add(self, device_id: str, skill_id: str, skill_settings_display_id: str, settings_value: str):
        db_request = self._build_db_request(
            sql_file_name='add_device_skill.sql',
            args=dict(
                device_id=device_id,
                skill_id=skill_id,
                skill_settings_display_id=skill_settings_display_id,
                settings_value=settings_value
            )
        )
        self.cursor.insert(db_request)
