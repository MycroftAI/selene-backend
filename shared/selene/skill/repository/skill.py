from os import path

from selene.util.db import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


def get_skill_settings_by_device_id(db, device_id):
    """Return all skill settings from a given device id
    :param db: psycopg2 connection to mycroft database
    :param device_id: device uuid
    :return list of skills using the format from the API v1"""
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_skill_setting_by_device_id.sql'),
        args=dict(device_id=device_id),
        singleton=False
    )
    sql_results = fetch(db, query)
    if sql_results:
        return [result['skill'] for result in sql_results]


def get_skill_settings_by_device_id_and_version_hash(db, device_id, version_hash):
    """Return a skill setting for a given device id and skill version hash
    :param db: psycopg2 connection to the mycroft database
    :param device_id: device uuid
    :param version_hash: skill setting version hash
    :return skill setting using the format from the API v1
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_skill_setting_by_device_id_and_version_hash.sql'),
        args=dict(device_id=device_id, version_hash=version_hash),
        singleton=False
    )
    sql_results = fetch(db, query)
    if sql_results:
        return sql_results[0]['skill']

