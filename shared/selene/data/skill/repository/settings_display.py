import json

from ...repository_base import RepositoryBase
from ..entity.skill_setting import SettingsDisplay


class SettingsDisplayRepository(RepositoryBase):

    def __init__(self, db):
        super(SettingsDisplayRepository, self).__init__(db, __file__)

    def add(self, settings_display: SettingsDisplay) -> str:
        """Add a new row to the skill.settings_display table."""
        db_request = self._build_db_request(
            sql_file_name='add_settings_display.sql',
            args=dict(
                skill_id=settings_display.skill_id,
                display_data=json.dumps(settings_display.display_data)
            )
        )
        result = self.cursor.insert_returning(db_request)

        return result['id']

    def get_settings_display_id(self, settings_display: SettingsDisplay):
        """Get the ID of a skill's settings definition."""
        db_request = self._build_db_request(
            sql_file_name='get_settings_display_id.sql',
            args=dict(
                skill_id=settings_display.skill_id,
                display_data=json.dumps(settings_display.display_data)
            )
        )
        result = self.cursor.select_one(db_request)

        return None if result is None else result['id']

    def get_settings_definitions_by_gid(self, global_id):
        """Get all matching settings definitions for a global skill ID.

        There can be more than one settings definition for a global skill ID.
        An example of when this could happen is if a skill author changed the
        settings definition and not all devices have updated to the latest.
        """
        return self._select_all_into_dataclass(
            SettingsDisplay,
            sql_file_name='get_settings_definition_by_gid.sql',
            args=dict(global_id=global_id)
        )

    def remove(self, settings_display_id: str):
        """Delete a settings definition that is no longer used by any device"""
        db_request = self._build_db_request(
            sql_file_name='delete_settings_display.sql',
            args=dict(settings_display_id=settings_display_id)
        )
        self.cursor.delete(db_request)
