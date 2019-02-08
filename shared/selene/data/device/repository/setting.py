from os import path

from selene.util.db import get_sql_from_file, Cursor, DatabaseRequest

SQL_DIR = path.join(path.dirname(__file__), 'sql')


class SettingRepository(object):
    def __init__(self, db):
        self.cursor = Cursor(db)

    def get_device_settings_by_device_id(self, device_id):
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'get_device_settings_by_device_id.sql')),
            args=dict(device_id=device_id)
        )
        return self.cursor.select_one(query)

    def convert_text_to_speech_setting(self, setting_name, engine) -> (str, str):
        """Convert the selene representation of TTS into the tartarus representation, for backward compatibility
        with the API v1"""
        if engine == 'mimic':
            if setting_name == 'amy':
                return 'mimic', 'amy'
            elif setting_name == 'kusal':
                return 'mimic2', 'kusal'
            else:
                return 'mimic', 'ap'
        else:
            return 'google', ''

    def get_device_settings(self, device_id):
        """Return the device settings aggregating the tables account preference, text to speech, wake word and
        wake word settings
        :param device_id: device uuid
        :return setting entity using the legacy format from the API v1"""
        response = self.get_device_settings_by_device_id(device_id)
        tts_setting = response['tts_settings']
        tts_setting = self.convert_text_to_speech_setting(tts_setting['setting_name'], tts_setting['engine'])
        tts_setting = [{'@type': tts_setting[0], 'voice': tts_setting[1]}]
        response['tts_settings'] = tts_setting
        return response