from dataclasses import dataclass
from datetime import datetime
from os import path
from typing import List

from selene.util.db import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


@dataclass
class WakeWord(object):
    id: str
    wake_word: str
    engine: str


@dataclass
class TextToSpeech(object):
    id: str
    setting_name: str
    display_name: str
    engine: str


@dataclass
class Device(object):
    """Representation of a Device"""
    id: str
    name: str
    platform: str
    enclosure_version: str
    core_version: str
    wake_word: WakeWord
    text_to_speech: TextToSpeech
    placement: str = None
    last_contact_ts: datetime = None


def get_device_by_id(db, device_id: str) -> Device:
    """Fetch a device using a given device id

    :param db: psycopg2 connection to mycroft database
    :param device_id: uuid
    :return: Device entity
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_device_by_id.sql'),
        args=dict(device_id=device_id),
        singleton=True
    )
    sql_result = fetch(db, query)
    sql_result = load_device_relations(db, sql_result)
    return Device(**sql_result)


def get_devices_by_account_id(db, account_id: str) -> List[Device]:
    """Fetch all devices associated to a user from a given account id

    :param db: psycopg2 connection to mycroft database
    :param account_id: uuid
    :return: List of User's devices
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_devices_by_account_id.sql'),
        args=dict(account_id=account_id),
        singleton=False
    )
    sql_results = fetch(db, query)
    return [Device(**result) for result in sql_results]


def load_device_relations(db, device: dict):
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_wake_word_by_id.sql'),
        args=dict(wake_word_id=device['wake_word_id']),
        singleton=True
    )
    sql_result = fetch(db, query)
    del sql_result['account_id']
    device['wake_word'] = WakeWord(**sql_result)
    del device['wake_word_id']

    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_text_to_speech_by_id.sql'),
        args=dict(text_to_speech_id=device['text_to_speech_id']),
        singleton=True
    )
    sql_result = fetch(db, query)
    device['text_to_speech'] = TextToSpeech(**sql_result)
    del device['text_to_speech_id']

    del device['account_id']
    del device['category_id']
    del device['location_id']
    return device

