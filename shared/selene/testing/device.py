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
"""Testing helper functions for testing devices."""
from selene.data.device import DeviceRepository, PantacorConfig


def add_device(db, account_id, geography_id):
    """Add a row to the device table for testing."""
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
    device_id = device_repository.add(account_id, device)

    return device_id


def add_pantacor_config(db, device_id):
    """Add a row to the pantacor_config table for testing Pantacor capabilities."""
    device_repository = DeviceRepository(db)
    pantacor_config = PantacorConfig(
        pantacor_id="test_pantacor_id",
        ip_address="192.168.1.2",
        auto_update=False,
        release_channel="latest",
    )
    device_repository.add_pantacor_config(device_id, pantacor_config)
