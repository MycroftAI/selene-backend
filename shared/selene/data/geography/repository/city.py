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

from ..entity.city import City
from ...repository_base import RepositoryBase


class CityRepository(RepositoryBase):
    def __init__(self, db):
        super(CityRepository, self).__init__(db, __file__)

    def get_cities_by_region(self, region_id):
        db_request = self._build_db_request(
            sql_file_name='get_cities_by_region.sql',
            args=dict(region_id=region_id)
        )
        db_result = self.cursor.select_all(db_request)

        return [City(**row) for row in db_result]
