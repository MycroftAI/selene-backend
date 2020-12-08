# Mycroft Server - Backend
# Copyright (C) 2020 Mycroft AI Inc
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
"""CRUD operations for the account_activity table in the metrics schema."""
from datetime import date, datetime
from logging import getLogger
from os import environ

from selene.data.account import Account, OPEN_DATASET
from ..entity.account_activity import AccountActivity
from ...repository_base import RepositoryBase

_log = getLogger(__package__)


class AccountActivityRepository(RepositoryBase):
    """Query and maintain the account_activity table."""

    def __init__(self, db):
        super().__init__(db, __file__)

    def increment_accounts_added(self):
        """Increment the accounts added metric on the account activity table."""
        request = self._build_db_request(sql_file_name="increment_accounts_added.sql")
        self._update_account_activity(request)

    def increment_accounts_deleted(self):
        """Increment the deleted accounts metric on the account activity table."""
        request = self._build_db_request(sql_file_name="increment_accounts_deleted.sql")
        self._update_account_activity(request)

    def increment_members_added(self):
        """Increment the deleted accounts metric on the account activity table."""
        request = self._build_db_request(sql_file_name="increment_members_added.sql")
        self._update_account_activity(request)

    def increment_members_expired(self):
        """Increment the deleted accounts metric on the account activity table."""
        request = self._build_db_request(sql_file_name="increment_members_expired.sql")
        self._update_account_activity(request)

    def increment_open_dataset_added(self):
        """Increment the deleted accounts metric on the account activity table."""
        request = self._build_db_request(
            sql_file_name="increment_open_dataset_added.sql"
        )
        self._update_account_activity(request)

    def increment_open_dataset_deleted(self):
        """Increment the deleted accounts metric on the account activity table."""
        request = self._build_db_request(
            sql_file_name="increment_open_dataset_deleted.sql"
        )
        self._update_account_activity(request)

    def increment_activity(self, account: Account):
        """Increment the activity counters depending on type of account."""
        first_activity_of_day = (
            account.last_activity is None
            or account.last_activity.date() < datetime.utcnow().date()
        )
        if first_activity_of_day:
            member_increment = 1 if account.membership is not None else 0
            agreements = [agreement.type for agreement in account.agreements]
            open_dataset_increment = 1 if OPEN_DATASET in agreements else 0
            request = self._build_db_request(
                sql_file_name="increment_account_activity.sql",
                args=dict(
                    member_increment=member_increment,
                    open_dataset_increment=open_dataset_increment,
                ),
            )
            self._update_account_activity(request)

    def _update_account_activity(self, update_request):
        """Update today's account activity, adding a row if it doesn't exist."""
        row_updated = self.cursor.update(update_request)
        if not row_updated:
            self._add_account_activity_row()
            self.cursor.update(update_request)

    def _add_account_activity_row(self):
        """Adds a row to the account activity table for a day that does not exist."""
        request = self._build_db_request(sql_file_name="add_account_activity.sql")
        self.cursor.insert(request)

    def get_activity_by_date(self, activity_date: date) -> AccountActivity:
        """Returns the account activity metrics for the given date."""
        return self._select_one_into_dataclass(
            dataclass=AccountActivity,
            sql_file_name="get_account_activity_by_date.sql",
            args=dict(activity_date=activity_date),
        )

    def delete_activity_by_date(self, activity_date: date):
        """ACCOUNT ACTIVITY SHOULD NEVER BE DELETED!  ONLY USE IN TEST CODE!"""
        if environ["SELENE_ENVIRONMENT"] == "dev":
            request = self._build_db_request(
                sql_file_name="delete_account_activity_date.sql",
                args=dict(activity_date=activity_date),
            )
            deleted_rows = self.cursor.delete(request)
            if deleted_rows:
                log_msg = "account activity for {} deleted"
            else:
                log_msg = "no activity row found for {}"
            _log.info(log_msg.format(activity_date))
