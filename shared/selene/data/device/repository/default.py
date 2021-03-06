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
"""Data access and manipulation for account defaults."""
from selene.data.geography import City, Country, Region, Timezone
from selene.data.wake_word.entity.wake_word import WakeWord
from ..entity.default import AccountDefaults
from ..entity.text_to_speech import TextToSpeech
from ...repository_base import RepositoryBase


class DefaultsRepository(RepositoryBase):
    """Methods to access and manipulate account defaults."""

    def __init__(self, db, account_id):
        super().__init__(db, __file__)
        self.account_id = account_id

    def upsert(self, defaults):
        """Update account defaults if they exist, otherwise, add them"""
        db_request_args = dict(account_id=self.account_id)
        db_request_args.update(defaults)
        db_request_args["wake_word"] = db_request_args["wake_word"]
        db_request = self._build_db_request(
            sql_file_name="upsert_defaults.sql", args=db_request_args
        )
        self.cursor.insert(db_request)

    def get_account_defaults(self) -> AccountDefaults:
        """Build an instance of the AccountDefaults dataclass"""
        db_request = self._build_db_request(
            sql_file_name="get_account_defaults.sql",
            args=dict(account_id=self.account_id),
        )
        db_result = self.cursor.select_one(db_request)
        if db_result is None:
            defaults = None
        else:
            db_result["city"] = City(**db_result["city"])
            db_result["country"] = Country(**db_result["country"])
            db_result["region"] = Region(**db_result["region"])
            db_result["timezone"] = Timezone(**db_result["timezone"])
            db_result["voice"] = TextToSpeech(**db_result["voice"])
            db_result["wake_word"] = WakeWord(**db_result["wake_word"])
            defaults = AccountDefaults(**db_result)

        return defaults
