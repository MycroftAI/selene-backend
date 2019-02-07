from os import path

from selene.util.db import DatabaseRequest, get_sql_from_file, Cursor

SQL_DIR = path.join(path.dirname(__file__), 'sql')


class SkillRepository(object):
    def __init__(self, db):
        self.cursor = Cursor(db)

    def get_skill_settings_by_device_id(self, device_id):
        """Return all skill settings from a given device id
        :param device_id: device uuid
        :return list of skills using the format from the API v1"""
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'get_skill_setting_by_device_id.sql')),
            args=dict(device_id=device_id)
        )
        sql_results = self.cursor.select_all(query)
        if sql_results:
            return [result['skill'] for result in sql_results]

    def get_skill_settings_by_device_id_and_version_hash(self, device_id, version_hash):
        """Return a skill setting for a given device id and skill version hash
        :param device_id: device uuid
        :param version_hash: skill setting version hash
        :return skill setting using the format from the API v1
        """
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'get_skill_setting_by_device_id_and_version_hash.sql')),
            args=dict(device_id=device_id, version_hash=version_hash)
        )
        sql_results = self.cursor.select_all(query)
        if sql_results:
            return sql_results[0]['skill']

