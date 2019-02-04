from os import path
from typing import List

from selene.device.entity.device import Device, WakeWord, TextToSpeech
from selene.util.db import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


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
    sql_results = fetch(db, query)
    device = {k: v for k, v in sql_results.items() if k in ('id', 'name', 'platform', 'enclosure_version', 'core_version')}

    wake_word = {k: v for k, v in sql_results.items() if k in ('wake_word_id', 'wake_word', 'engine')}
    wake_word['id'] = wake_word.pop('wake_word_id')
    device['wake_word'] = wake_word

    text_to_speech = {k: v for k, v in sql_results.items() if k in ('text_to_speech_id', 'setting_name', 'display_name', 'engine')}
    text_to_speech['id'] = text_to_speech.pop('text_to_speech_id')
    device['text_to_speech'] = text_to_speech
    return Device(**device)


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
