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

