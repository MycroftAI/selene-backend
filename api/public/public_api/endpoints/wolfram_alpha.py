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
from flask import Response

from selene.api import PublicEndpoint, track_account_activity


class WolframAlphaEndpoint(PublicEndpoint):
    """Proxy to the Wolfram Alpha API.

    WARNING: This Endpoint is deprecated in favor of WolframAlphaV2Endpoint.

    The new endpoint allows for the usage of additional query params beyond
    the 'input' such as output format to return JSON or XML.
    """

    def __init__(self):
        super(WolframAlphaEndpoint, self).__init__()
        self.wolfram_alpha_key = os.environ["WOLFRAM_ALPHA_KEY"]
        self.wolfram_alpha_url = os.environ["WOLFRAM_ALPHA_URL"]

    def get(self):
        self._authenticate()
        track_account_activity(self.db, self.device_id)
        return self._query_wolfram_alpha()

    def _query_wolfram_alpha(self):
        query = self.request.args.get("input")
        if query:
            params = dict(appid=self.wolfram_alpha_key, input=query)
            response = requests.get(self.wolfram_alpha_url + "/v2/query", params=params)
            if response.status_code == HTTPStatus.OK:
                return Response(response.content, mimetype="text/xml")
