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

from selene.data.device import Geography, GeographyRepository


def add_account_geography(db, account, **overrides):
    geography = Geography(
        country=overrides.get('country') or 'United States',
        region=overrides.get('region') or 'Missouri',
        city=overrides.get('city') or 'Kansas City',
        time_zone=overrides.get('time_zone') or 'America/Chicago'
    )
    geo_repository = GeographyRepository(db, account.id)
    account_geography_id = geo_repository.add(geography)

    return account_geography_id
