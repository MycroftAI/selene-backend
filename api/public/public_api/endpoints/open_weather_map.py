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

import json
import os

import requests

from selene.api import PublicEndpoint


class OpenWeatherMapEndpoint(PublicEndpoint):
    """Proxy to the Open Weather Map API"""
    def __init__(self):
        super(OpenWeatherMapEndpoint, self).__init__()
        self.owm_key = os.environ['OWM_KEY']
        self.owm_url = os.environ['OWM_URL']

    def get(self, path):
        self._authenticate()
        params = dict(self.request.args)
        params['APPID'] = self.owm_key
        response = requests.get(self.owm_url + '/' + path, params=params)
        return json.loads(response.content.decode('utf-8'))

