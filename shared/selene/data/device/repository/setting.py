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
"""Data access methods for the device settings."""
from os import path
from typing import Optional

from selene.util.db import get_sql_from_file, Cursor, DatabaseRequest

SQL_DIR = path.join(path.dirname(__file__), "sql")


class SettingRepository:
    """Data access methods for the device settings."""

    def __init__(self, db):
        self.cursor = Cursor(db)

    def get_device_settings_by_device_id(self, device_id: str):
        """Retrieves device settings from database for a supplied device ID."""
        query = DatabaseRequest(
            sql=get_sql_from_file(
                path.join(SQL_DIR, "get_device_settings_by_device_id.sql")
            ),
            args=dict(device_id=device_id),
        )
        return self.cursor.select_one(query)

    def convert_text_to_speech_setting(
        self, setting_name: str, engine: str
    ) -> (str, str):
        """Converts the Selene TTS engine into a value recognized by the device.

        :param setting_name: Selene TTS setting name
        :param engine: Selene TTS engine name
        :return: TTS engine and setting name recognized by the device
        """
        if engine == "mimic":
            if setting_name == "trinity":
                tts_engine = "mimic"
                voice = "trinity"
            elif setting_name == "kusal":
                tts_engine = "mimic2"
                voice = "kusal"
            else:
                tts_engine = "mimic"
                voice = "ap"
        else:
            tts_engine = "google"
            voice = ""

        return tts_engine, voice

    def _format_date_v1(self, date: str) -> str:
        """Converts Selene date format into value recognized by device.

        :param date: date format recognized by Selene
        :return: date format recognized by device
        """
        if date == "DD/MM/YYYY":
            date_format = "DMY"
        else:
            date_format = "MDY"

        return date_format

    def _format_time_v1(self, time: str) -> str:
        """Converts Selene time format into value recognized by device.

        :param time: time format recognized by Selene
        :return: time format recognized by device
        """
        if time == "24 Hour":
            time_format = "full"
        else:
            time_format = "half"

        return time_format

    def get_device_settings(self, device_id: str) -> Optional[dict]:
        """Retrieves device settings from the database for a supplied device ID.

        :param device_id: device uuid
        :return setting entity using the legacy format from the API v1
        """
        settings = None
        query_result = self.get_device_settings_by_device_id(device_id)
        if query_result:
            if query_result["listener_setting"]["uuid"] is None:
                del query_result["listener_setting"]
            tts_setting = query_result["tts_settings"]
            tts_setting = self.convert_text_to_speech_setting(
                tts_setting["setting_name"], tts_setting["engine"]
            )
            tts_setting = {
                "module": tts_setting[0],
                tts_setting[0]: {"voice": tts_setting[1]},
            }
            open_dataset = self._get_open_dataset_agreement_by_device_id(device_id)
            settings = dict(
                uuid=query_result["uuid"],
                ttsSettings=tts_setting,
                dateFormat=self._format_date_v1(query_result["date_format"]),
                timeFormat=self._format_time_v1(query_result["time_format"]),
                systemUnit=query_result["system_unit"].lower(),
                optIn=open_dataset is not None,
            )

        return settings

    def _get_open_dataset_agreement_by_device_id(self, device_id: str) -> dict:
        """Retrieves the open dataset agreement from the database, if there is one.

        :param device_id: the device ID to use in the query
        :return: the open dataset agreement.
        """
        query = DatabaseRequest(
            sql=get_sql_from_file(
                path.join(SQL_DIR, "get_open_dataset_agreement_by_device_id.sql")
            ),
            args=dict(device_id=device_id),
        )

        return self.cursor.select_one(query)
