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

from dataclasses import asdict

from ..entity.preference import AccountPreferences
from ...repository_base import RepositoryBase


class PreferenceRepository(RepositoryBase):
    def __init__(self, db, account_id):
        super(PreferenceRepository, self).__init__(db, __file__)
        self.account_id = account_id

    def get_account_preferences(self) -> AccountPreferences:
        db_request = self._build_db_request(
            sql_file_name="get_account_preferences.sql",
            args=dict(account_id=self.account_id),
        )

        db_result = self.cursor.select_one(db_request)
        if db_result is None:
            preferences = None
        else:
            preferences = AccountPreferences(**db_result)

        return preferences

    def upsert(self, preferences: AccountPreferences):
        db_request_args = dict(account_id=self.account_id)
        db_request_args.update(asdict(preferences))
        db_request = self._build_db_request(
            sql_file_name="upsert_preferences.sql", args=db_request_args
        )
        self.cursor.insert(db_request)
