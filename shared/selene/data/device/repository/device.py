# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""Data retrieval and maintenance routines for devices."""
from datetime import datetime
from typing import List

from selene.data.geography import City, Country, Region, Timezone
from selene.data.wake_word import WakeWord
from ..entity.device import Device, PantacorConfig
from ..entity.text_to_speech import TextToSpeech
from ...repository_base import RepositoryBase


class DeviceRepository(RepositoryBase):
    """Data retrieval and maintenance routines for devices."""

    def __init__(self, db):
        super().__init__(db, __file__)

    def get_device_by_id(self, device_id: str) -> Device:
        """Fetch a device using a given device id

        :param device_id: uuid
        :return: Device entity
        """
        db_request = self._build_db_request(
            sql_file_name="get_device_by_id.sql", args=dict(device_id=device_id)
        )
        db_result = self.cursor.select_one(db_request)

        if db_result is None:
            device = None
        else:
            device = self._build_device_from_row(db_result)

        return device

    def get_devices_by_account_id(self, account_id: str) -> List[Device]:
        """Fetch all devices associated to a user from a given account id

        :param account_id: uuid
        :return: List of User's devices
        """
        db_request = self._build_db_request(
            sql_file_name="get_devices_by_account_id.sql",
            args=dict(account_id=account_id),
        )
        db_results = self.cursor.select_all(db_request)

        devices = []
        for row in db_results:
            device = self._build_device_from_row(row)
            devices.append(device)

        return devices

    @staticmethod
    def _build_device_from_row(row: dict) -> Device:
        """Build a Device dataclass instance from query results."""
        row["city"] = City(**row["city"])
        row["country"] = Country(**row["country"])
        row["region"] = Region(**row["region"])
        row["timezone"] = Timezone(**row["timezone"])
        row["wake_word"] = WakeWord(**row["wake_word"])
        row["text_to_speech"] = TextToSpeech(**row["text_to_speech"])
        row["pantacor_config"] = PantacorConfig(**row["pantacor_config"])

        return Device(**row)

    def get_account_device_count(self, account_id: str) -> int:
        """Returns the number of devices assigned to a specified account."""
        db_request = self._build_db_request(
            sql_file_name="get_account_device_count.sql",
            args=dict(account_id=account_id),
        )
        db_results = self.cursor.select_one(db_request)

        return db_results["device_count"]

    def get_all_device_ids(self) -> List:
        """Return a list of all the device IDs on the device table."""
        db_request = self._build_db_request(sql_file_name="get_all_device_ids.sql")

        return self.cursor.select_all(db_request)

    def get_subscription_type_by_device_id(self, device_id: str):
        """Return the type of subscription of device's owner

        :param device_id: device uuid
        """
        subscription_type = None
        db_request = self._build_db_request(
            sql_file_name="get_subscription_type_by_device_id.sql",
            args=dict(device_id=device_id),
        )
        db_result = self.cursor.select_one(db_request)
        if db_result:
            rate_period = db_result["rate_period"]
            # TODO: Remove the @ in the API v2
            subscription_type = {
                "@type": "free" if rate_period is None else rate_period
            }

        return subscription_type

    def add(self, account_id: str, device: dict) -> str:
        """Insert a row on the device table"""
        db_request_args = dict(account_id=account_id)
        db_request_args.update(device)
        del db_request_args["pairing_code"]
        db_request = self._build_db_request(
            sql_file_name="add_device.sql", args=db_request_args
        )
        db_result = self.cursor.insert_returning(db_request)
        return db_result["id"]

    def update_device_from_core(self, device_id: str, updates: dict):
        """Updates a device with data sent to the API from Mycroft core"""
        db_request_args = dict(device_id=device_id)
        db_request_args.update(updates)
        db_request = self._build_db_request(
            sql_file_name="update_device_from_core.sql", args=db_request_args
        )
        self.cursor.update(db_request)

    def add_text_to_speech(self, text_to_speech: TextToSpeech) -> str:
        """Add a row to the text to speech table

        :param text_to_speech: text to speech entity
        :return text to speech id
        """
        db_request = self._build_db_request(
            sql_file_name="add_text_to_speech.sql",
            args=dict(
                setting_name=text_to_speech.setting_name,
                display_name=text_to_speech.display_name,
                engine=text_to_speech.engine,
            ),
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result["id"]

    def remove_wake_word(self, wake_word_id: str):
        """Remove a  wake word from the database using id"""
        db_request = self._build_db_request(
            sql_file_name="remove_wake_word.sql", args=dict(wake_word_id=wake_word_id)
        )
        self.cursor.delete(db_request)

    def remove_text_to_speech(self, text_to_speech_id: str):
        """Remove a text to speech from the database using id"""
        db_request = self._build_db_request(
            sql_file_name="remove_text_to_speech.sql",
            args=dict(text_to_speech_id=text_to_speech_id),
        )
        self.cursor.delete(db_request)

    def remove(self, device_id: str):
        """Remove a row from the device tables and any related child tables.

        :param device_id: UUID identifying a device.
        """
        db_request = self._build_db_request(
            sql_file_name="remove_device.sql", args=dict(device_id=device_id)
        )

        self.cursor.delete(db_request)

    def update_device_from_account(
        self, account_id: str, device_id: str, updates: dict
    ):
        """Updates a device with data sent to the API from account.mycroft.ai

        :param account_id: UUID identifying the user's account
        :param device_id: UUID identifying a device
        :param updates: fields updated and the new values of those fields
        """
        db_request_args = dict(account_id=account_id, device_id=device_id)
        db_request_args.update(updates)
        db_request = self._build_db_request(
            sql_file_name="update_device_from_account.sql", args=db_request_args
        )

        self.cursor.update(db_request)

    def upsert_pantacor_config(self, device_id: str, pantacor_config: PantacorConfig):
        """Add Pantacor configuration to a device that uses this update mechanism.

        If a row already exists for this device on the table, just update the
        IP address.

        :param device_id: UUID identifying a device
        :param pantacor_config: dataclass object containing Pantacor-specific data.
        """
        db_request_args = dict(
            device_id=device_id,
            pantacor_id=pantacor_config.pantacor_id,
            ip_address=pantacor_config.ip_address,
            auto_update=pantacor_config.auto_update,
            release_channel=pantacor_config.release_channel,
        )
        db_request = self._build_db_request(
            sql_file_name="upsert_pantacor_config.sql", args=db_request_args
        )

        self.cursor.insert(db_request)

    def update_pantacor_config(self, device_id: str, updates: dict):
        """Updates a device with data sent to the API from account.mycroft.ai

        :param device_id: UUID identifying a device
        :param updates: Pantacor configuration values being updated.
        """
        db_request_args = dict(device_id=device_id)
        db_request_args.update(updates)
        db_request = self._build_db_request(
            sql_file_name="update_pantacor_config.sql", args=db_request_args
        )

        self.cursor.update(db_request)

    def update_last_contact_ts(self, device_id: str, last_contact_ts: datetime):
        """Update the timestamp indicating the last time the device was heard from.

        :param device_id: UUID identifying a device
        :param last_contact_ts: timestamp representing last time device was seen.
        """
        db_request = self._build_db_request(
            sql_file_name="update_last_contact_ts.sql",
            args=dict(device_id=device_id, last_contact_ts=last_contact_ts),
        )
        self.cursor.update(db_request)
