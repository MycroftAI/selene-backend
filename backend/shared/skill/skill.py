from dataclasses import dataclass
from os import path

from selene_util.db import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


@dataclass
class Setting(object):
    """Representation of a Skill setting"""
    id: str
    setting_section_id: str
    setting: str
    setting_type: str
    hidden: bool
    display_order: int
    hint: str = None
    label: str = None
    placeholder: str = None
    options: str = None
    default_value: str = None
    value: str = None


@dataclass
class SettingSection(object):
    """Representation of a section from a Skill Setting"""
    id: str
    skill_version_id: str
    section: str
    display_order: int
    description: str = None
    settings: list = None


@dataclass
class SkillSetting(object):
    """Representation of the link between a device and a skill setting """
    id: str
    device_skill_id: str
    setting_id: str
    value: str = None


def get_setting_sections_by_device_id_and_setting_version(db, device_id, setting_version_hash):
    """ Fetch all sections of a skill for a given device and setting version

    :param db: psycopg2 connection to the mycroft database
    :param device_id: uuid
    :param setting_version_hash: version_hash for a given skill setting
    :return:
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_setting_sections_by_device_id_and_setting_version.sql'),
        args=dict(device_id=device_id, setting_version_hash=setting_version_hash),
        singleton=False
    )
    sql_results = fetch(db, query)
    return list(map(lambda result: SettingSection(**result), sql_results))


def get_setting_by_section_id(db, setting_section_ids):
    """ Fetch all settings for a given list of section ids

    :param db: psycopg2 connection to the mycroft database
    :param setting_section_ids: list of section ids
    :return:
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_setting_by_section_ids.sql'),
        args=dict(setting_section_ids=setting_section_ids),
        singleton=False
    )
    sql_results = fetch(db, query)
    return list(map(lambda result: Setting(**result), sql_results))


def get_skill_settings_by_device_id_and_version_hash(db, device_id, setting_version_hash):
    """Fetch the skill settings for a given device and setting version hash

    :param db: psycopg2 connection to the mycroft database
    :param device_id: uuid
    :param setting_version_hash:
    :return:
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_skill_setting_by_device_id_and_version_hash.sql'),
        args=dict(device_id=device_id, setting_version_hash=setting_version_hash),
        singleton=False
    )
    sql_results = fetch(db, query)
    return list(map(lambda result: SkillSetting(**result), sql_results))


def get_setting_by_device_id_and_setting_version_hash(db, device_id, setting_version_hash):
    """Fetch the skill settings filling the setting using the value from the table skill setting
    :param db: psycopg2 connection to the mycroft database
    :param device_id: uuid
    :param setting_version_hash:
    :return:
    """
    sections = get_setting_sections_by_device_id_and_setting_version(db, device_id, setting_version_hash)
    setting_sections_ids = tuple(map(lambda s: s.id, sections))
    settings = get_setting_by_section_id(db, setting_sections_ids)
    skill_settings = get_skill_settings_by_device_id_and_version_hash(db, device_id, setting_version_hash)

    # Fills each setting with the correspondent value from the skill setting
    for skill_setting in skill_settings:
        s = next(filter(lambda setting: setting.id == skill_setting.setting_id, settings), None)
        if s:
            s.value = skill_setting.value

    # Fills each setting with its list of settings
    for section in sections:
        section.settings = list(filter(lambda setting: setting.setting_section_id == section.id, settings))

    return sections
