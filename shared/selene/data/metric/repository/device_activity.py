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
"""CRUD operations for the device_activity table in the metrics schema."""
from datetime import date, datetime
from logging import getLogger
from typing import List

from selene.util.db import use_transaction
from ..entity.device_activity import DeviceActivity
from ...device import DeviceRepository
from ...repository_base import RepositoryBase

_log = getLogger(__package__)


class DeviceActivityRepository(RepositoryBase):
    """Query and maintain the account_activity table."""

    def __init__(self, db):
        super().__init__(db, __file__)

    def increment_activity(self, device_id: str):
        """Increment the activity counters depending on device's platform."""
        device = self._get_device_by_id(device_id)
        first_activity_of_day = (
            device.last_contact_ts is None
            or device.last_contact_ts.date() < datetime.utcnow().date()
        )
        if first_activity_of_day:
            request = self._build_db_request(
                sql_file_name="increment_device_activity.sql",
                args=dict(platform=device.platform),
            )
            self._update_device_activity(request)

    def _get_device_by_id(self, device_id):
        """Get the device so we can know the last contact timestamp."""
        device_repository = DeviceRepository(self.db)
        device = device_repository.get_device_by_id(device_id)

        return device

    @use_transaction
    def _update_device_activity(self, update_request):
        """Update today's device activity, adding a row if it doesn't exist."""
        row_updated = self.cursor.update(update_request)
        if not row_updated:
            self._add_device_activity_row()
            self.cursor.update(update_request)

    def _add_device_activity_row(self):
        """Adds a row to the device activity table for a day that does not exist."""
        request = self._build_db_request(sql_file_name="add_device_activity.sql")
        self.cursor.insert(request)

    def get_activity_by_date(self, activity_date: date) -> List[DeviceActivity]:
        """Returns the device activity metrics for the given date."""
        return self._select_all_into_dataclass(
            dataclass=DeviceActivity,
            sql_file_name="get_device_activity_by_date.sql",
            args=dict(activity_date=activity_date),
        )
