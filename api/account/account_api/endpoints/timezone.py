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

from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.geography import TimezoneRepository


class TimezoneEndpoint(SeleneEndpoint):
    def get(self):
        country_id = self.request.args["country"]
        timezone_repository = TimezoneRepository(self.db)
        timezones = timezone_repository.get_timezones_by_country(country_id)

        for timezone in timezones:
            timezone.dst_offset = float(timezone.dst_offset)
            timezone.gmt_offset = float(timezone.gmt_offset)

        return timezones, HTTPStatus.OK
