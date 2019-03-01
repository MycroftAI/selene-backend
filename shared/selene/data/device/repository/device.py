from os import path
from typing import List

from ..entity.text_to_speech import TextToSpeech
from ..entity.wake_word import WakeWord
from ..entity.device import Device
from selene.util.db import DatabaseRequest, get_sql_from_file, Cursor

SQL_DIR = path.join(path.dirname(__file__), 'sql')


class DeviceRepository(object):
    def __init__(self, db):
        self.cursor = Cursor(db)

    def get_device_by_id(self, device_id: str) -> Device:
        """Fetch a device using a given device id

        :param device_id: uuid
        :return: Device entity
        """
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'get_device_by_id.sql')),
            args=dict(device_id=device_id)
        )

        sql_results = self.cursor.select_one(query)
        if sql_results:
            return Device(**sql_results)

    def get_devices_by_account_id(self, account_id: str) -> List[Device]:
        """Fetch all devices associated to a user from a given account id

        :param account_id: uuid
        :return: List of User's devices
        """
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'get_devices_by_account_id.sql')),
            args=dict(account_id=account_id)
        )
        sql_results = self.cursor.select_all(query)
        return [Device(**result) for result in sql_results]

    def get_account_device_count(self, account_id):
        query = DatabaseRequest(
            sql=get_sql_from_file(
                path.join(SQL_DIR, 'get_account_device_count.sql')
            ),
            args=dict(account_id=account_id)

        )
        sql_results = self.cursor.select_one(query)

        return sql_results['device_count']

    def get_subscription_type_by_device_id(self, device_id):
        """Return the type of subscription of device's owner
        :param device_id: device uuid
        """
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'get_subscription_type_by_device_id.sql')),
            args=dict(device_id=device_id)
        )
        sql_result = self.cursor.select_one(query)
        if sql_result:
            rate_period = sql_result['rate_period']
            # TODO: Remove the @ in the API v2
            return {'@type': rate_period} if rate_period is not None else {'@type': 'free'}

    def add_device(self, account_id: str, name: str, wake_word_id: str, text_to_speech_id: str):
        """ Creates a new device with a given name and associate it to an account"""
        # TODO: validate foreign keys
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'add_device.sql')),
            args=dict(
                account_id=account_id,
                name=name,
                wake_word_id=wake_word_id,
                text_to_speech_id=text_to_speech_id
            )
        )
        return self.cursor.insert_returning(query)

    def update_device(self, device_id: str, platform: str, enclosure_version: str, core_version: str):
        """Updates a device in the database"""
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'update_device.sql')),
            args=dict(
                device_id=device_id,
                platform=platform,
                enclosure_version=enclosure_version,
                core_version=core_version
            )
        )
        return self.cursor.insert(query)

    def add_wake_word(self, account_id: str, wake_word: WakeWord) -> str:
        """Adds a row to the wake word table
        :param account_id: the account that we are linking to the wake word
        :param wake_word: wake_word entity
        :return wake word id
        """
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'add_wake_word.sql')),
            args=dict(
                wake_word=wake_word.wake_word,
                account_id=account_id,
                engine=wake_word.engine
            )
        )
        result = self.cursor.insert_returning(query)
        return result['id']

    def add_text_to_speech(self, text_to_speech: TextToSpeech) -> str:
        """Add a row to the text to speech table
        :param text_to_speech: text to speech entity
        :return text to speech id"""
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'add_text_to_speech.sql')),
            args=dict(
                setting_name=text_to_speech.setting_name,
                display_name=text_to_speech.display_name,
                engine=text_to_speech.engine
            )
        )
        result = self.cursor.insert_returning(query)
        return result['id']

    def remove_wake_word(self, wake_word_id: str):
        """Remove a  wake word from the database using id"""
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'remove_wake_word.sql')),
            args=dict(wake_word_id=wake_word_id)
        )
        self.cursor.delete(query)

    def remove_text_to_speech(self, text_to_speech_id: str):
        """Remove a text to speech from the database using id"""
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'remove_text_to_speech.sql')),
            args=dict(text_to_speech_id=text_to_speech_id)
        )
        self.cursor.delete(query)

    def get_account_email_by_device_id(self, device_id):
        query = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'get_account_email_by_device_id.sql')),
            args=dict(device_id=device_id)
        )
        sql_result = self.cursor.select_one(query)
        if sql_result:
            return sql_result['email_address']
