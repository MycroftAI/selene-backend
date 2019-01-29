from dataclasses import dataclass
from os import path

from selene.util.db import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


@dataclass
class AccountPreferences(object):
    id: str
    date_format: str
    time_format: str
    measurement_system: str


@dataclass
class WakeWord(object):
    id: str
    wake_word: str
    engine: str


@dataclass
class WakeWordSettings(object):
    id: str
    sample_rate: int
    channels: int
    pronunciation: str
    threshold: str
    threshold_multiplier: float
    dynamic_energy_ratio: float


@dataclass
class TextToSpeech(object):
    id: str
    setting_name: str
    display_name: str
    engine: str


def get_account_preferences_by_device_id(db, device_id):
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_account_preferences_by_device_id.sql'),
        args=dict(device_id=device_id),
        singleton=True
    )
    return fetch(db, query)


def get_wake_word_settings_by_device_id(db, device_id):
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_wake_word_settings_by_device_id.sql'),
        args=dict(device_id=device_id),
        singleton=True
    )
    return fetch(db, query)


def get_text_to_speech_by_device_id(db, device_id):
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_text_to_speech_by_device_id.sql'),
        args=dict(device_id=device_id),
        singleton=True
    )
    return fetch(db, query)


def get_device_settings(db, device_id):
    sql_results = get_account_preferences_by_device_id(db, device_id)
    del sql_results['account_id']
    del sql_results['wake_word_id']
    del sql_results['text_to_speech_id']
    del sql_results['location_id']

    account_preferences = AccountPreferences(**sql_results)

    sql_results = get_wake_word_settings_by_device_id(db, device_id)
    del sql_results['wake_word_id']
    print(sql_results)
    wake_word = WakeWordSettings(**sql_results)

    sql_results = get_text_to_speech_by_device_id(db, device_id)
    text_to_speech = TextToSpeech(*sql_results)
