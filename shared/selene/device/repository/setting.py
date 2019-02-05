from os import path

from selene.util.db import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


def get_device_settings_by_device_id(db, device_id):
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_device_settings_by_device_id.sql'),
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
    response = get_device_settings_by_device_id(db, device_id)
    tts_setting = response['tts_settings']
    tts_setting = convert_text_to_speech_setting(tts_setting['setting_name'], tts_setting['engine'])
    tts_setting = {'@type': tts_setting[0], 'voice': tts_setting[1]}
    response['tts_settings'] = tts_setting
    return response
