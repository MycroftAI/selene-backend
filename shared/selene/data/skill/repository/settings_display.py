from selene.data.repository_base import RepositoryBase


class SettingsDisplayRepository(RepositoryBase):

    def __init__(self, db):
        super(SettingsDisplayRepository, self).__init__(db, __file__)

    def add(self, skill_id: str, settings_display: str) -> str:
        db_request = self._build_db_request(
            sql_file_name='add_settings_display.sql',
            args=dict(skill_id=skill_id, settings_display=settings_display)
        )
        result = self.cursor.insert_returning(db_request)
        return result['id']
