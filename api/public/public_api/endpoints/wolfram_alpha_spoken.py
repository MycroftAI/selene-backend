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

import os
from http import HTTPStatus

import requests

from selene.api import PublicEndpoint


class WolframAlphaSpokenEndpoint(PublicEndpoint):
    """Endpoint to communicate with the Wolfram Alpha Spoken API"""

    def __init__(self):
        super(WolframAlphaSpokenEndpoint, self).__init__()
        self.wolfram_alpha_key = os.environ["WOLFRAM_ALPHA_KEY"]
        self.wolfram_alpha_url = os.environ["WOLFRAM_ALPHA_URL"]

    def get(self):
        self._authenticate()
        params = dict(self.request.args)
        params["appid"] = self.wolfram_alpha_key
        response = requests.get(self.wolfram_alpha_url + "/v1/spoken", params=params)
        code = response.status_code
        response = (response.text, code) if code == HTTPStatus.OK else ("", code)
        return response
