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
"""Common test code for devices."""
from selene.data.device import DeviceRepository


def add_device(db, account_id, geography_id):
    """Add a device to the database for testing."""
    device = dict(
        name="Selene Test Device",
        pairing_code="ABC123",
        placement="kitchen",
        geography_id=geography_id,
        country="United States",
        region="Missouri",
        city="Kansas City",
        timezone="America/Chicago",
        wake_word="hey selene",
        voice="Selene Test Voice",
    )
    device_repository = DeviceRepository(db)
    device["id"] = device_repository.add(account_id, device)
    core_data = dict(
        platform="picroft", core_version="18.8.0", enclosure_version="1.4.0"
    )
    device_repository.update_device_from_core(device["id"], core_data)
    device.update(core_data)

    return device
