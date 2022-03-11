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

import hashlib
import json
from http import HTTPStatus

from selene.api import PublicEndpoint, generate_device_login
from selene.util.auth import AuthenticationError


class DeviceRefreshTokenEndpoint(PublicEndpoint):

    ONE_DAY = 86400

    def __init__(self):
        super(DeviceRefreshTokenEndpoint, self).__init__()
        self.sha512 = hashlib.sha512()

    def get(self):
        headers = self.request.headers
        if "Authorization" not in headers:
            raise AuthenticationError("Oauth token not found")
        token_header = self.request.headers["Authorization"]
        if token_header.startswith("Bearer "):
            refresh = token_header[len("Bearer ") :]
            session = self._refresh_session_token(refresh)
            # Trying to fetch a session using the refresh token
            if session:
                response = session, HTTPStatus.OK
            else:
                device = self.request.headers.get("Device")
                if device:
                    # trying to fetch a session using the device uuid
                    session = self._refresh_session_token_device(device)
                    if session:
                        response = session, HTTPStatus.OK
                    else:
                        response = "", HTTPStatus.UNAUTHORIZED
                else:
                    response = "", HTTPStatus.UNAUTHORIZED
        else:
            response = "", HTTPStatus.UNAUTHORIZED
        return response

    def _refresh_session_token(self, refresh: str):
        refresh_key = "device.token.refresh:{}".format(refresh)
        session = self.cache.get(refresh_key)
        if session:
            old_login = json.loads(session)
            device_id = old_login["uuid"]
            self.cache.delete(refresh_key)
            return generate_device_login(device_id, self.cache)

    def _refresh_session_token_device(self, device: str):
        refresh_key = "device.session:{}".format(device)
        session = self.cache.get(refresh_key)
        if session:
            old_login = json.loads(session)
            device_id = old_login["uuid"]
            self.cache.delete(refresh_key)
            return generate_device_login(device_id, self.cache)
