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

from ..entity.geography import Geography
from ...repository_base import RepositoryBase


class GeographyRepository(RepositoryBase):
    def __init__(self, db, account_id):
        """
        Initialize db.

        Args:
            self: (todo): write your description
            db: (todo): write your description
            account_id: (str): write your description
        """
        super(GeographyRepository, self).__init__(db, __file__)
        self.account_id = account_id

    def get_account_geographies(self):
        """
        Returns a list of all geometries.

        Args:
            self: (todo): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='get_account_geographies.sql',
            args=dict(account_id=self.account_id)
        )
        db_response = self.cursor.select_all(db_request)

        return [Geography(**row) for row in db_response]

    def get_geography_id(self, geography: Geography):
        """
        Return the geometry id for a given geometry.

        Args:
            self: (todo): write your description
            geography: (str): write your description
        """
        geography_id = None
        acct_geographies = self.get_account_geographies()
        for acct_geography in acct_geographies:
            match = (
                acct_geography.city == geography.city and
                acct_geography.country == geography.country and
                acct_geography.region == geography.region and
                acct_geography.time_zone == geography.time_zone
            )
            if match:
                geography_id = acct_geography.id
                break

        return geography_id

    def add(self, geography: Geography):
        """
        Add a new geography to this account.

        Args:
            self: (todo): write your description
            geography: (todo): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='add_geography.sql',
            args=dict(
                account_id=self.account_id,
                city=geography.city,
                country=geography.country,
                region=geography.region,
                timezone=geography.time_zone
            )
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result['id']

    def get_location_by_device_id(self, device_id):
        """
        Returns the location of a device by its id.

        Args:
            self: (todo): write your description
            device_id: (int): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='get_location_by_device_id.sql',
            args=dict(device_id=device_id)
        )
        return self.cursor.select_one(db_request)
