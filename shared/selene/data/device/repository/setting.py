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

    def _format_date_v1(self, date: str):
        if date == 'DD/MM/YYYY':
            result = 'DMY'
        else:
            result = 'MDY'
        return result

    def _format_time_v1(self, time: str):
        if time == '24 Hour':
            result = 'full'
        else:
            result = 'half'
        return result

    def get_device_settings(self, device_id):
        """Return the device settings aggregating the tables account preference, text to speech, wake word and
        wake word settings
        :param device_id: device uuid
        :return setting entity using the legacy format from the API v1"""
        response = self.get_device_settings_by_device_id(device_id)
        if response:
            if response['listener_setting']['uuid'] is None:
                del response['listener_setting']
            tts_setting = response['tts_settings']
            tts_setting = self.convert_text_to_speech_setting(tts_setting['setting_name'], tts_setting['engine'])
            tts_setting = [{'@type': tts_setting[0], 'voice': tts_setting[1]}]
            response['tts_settings'] = tts_setting
            response['date_format'] = self._format_date_v1(response['date_format'])
            response['time_format'] = self._format_time_v1(response['time_format'])
            return response

    def add_account_preferences(self, preferences: dict):
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'add_account_preferences.sql')),
            args=dict(
                account_id=preferences['account_id'],
                date_format=preferences['date_format'],
                time_format=preferences['time_format'],
                measurement_system=preferences['measurement_system']
            )
        )
        self.cursor.insert(query)
