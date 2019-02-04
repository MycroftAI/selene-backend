from os import path

from selene.util.db import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


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


def get_wake_word_by_device_id(db, device_id):
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_wake_word_by_device_id.sql'),
        args=dict(device_id=device_id),
        singleton=True
    )
    return fetch(db, query)


def convert_text_to_speech_setting(setting_name, engine) -> (str, str):
    if engine == 'mimic':
        if setting_name == 'amy':
            return 'mimic', 'amy'
        elif setting_name == 'kusal':
            return 'mimic2', 'kusal'
        else:
            return 'mimic', 'ap'
    else:
        return 'google', ''


def get_device_settings(db, device_id):
    response = {}
    sql_results = get_account_preferences_by_device_id(db, device_id)
    response['uuid'] = sql_results['id']
    response['systemUnit'] = sql_results['measurement_system']
    response['dateFormat'] = sql_results['date_format']
    response['timeFormat'] = sql_results['time_format']

    sql_results = get_text_to_speech_by_device_id(db, device_id)
    type, voice = convert_text_to_speech_setting(sql_results['setting_name'], sql_results['engine'])
    response['ttsSettings'] = [{
        '@type': type,
        'voice': voice
    }]

    sql_results = get_wake_word_settings_by_device_id(db, device_id)
    sql_results_wake_word = get_wake_word_by_device_id(db, device_id)
    response['listenerSetting'] = {
        'uuid': sql_results['id'],
        'sampleRate': sql_results['sample_rate'],
        'channels': sql_results['channels'],
        'wakeWord': sql_results_wake_word['wake_word'],
        'phonemes': sql_results['pronunciation'],
        'threshold': sql_results['threshold'],
        'multiplier': float(sql_results['threshold_multiplier']),
        'energyRatio': float(sql_results['dynamic_energy_ratio'])
    }
    return response
