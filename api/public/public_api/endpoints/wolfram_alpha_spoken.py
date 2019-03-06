import os
from http import HTTPStatus

import requests

from selene.api import SeleneEndpoint


class WolframAlphaSpokenEndpoint(SeleneEndpoint):
    """Endpoint to communicate with the Wolfram Alpha Spoken API"""

    def __init__(self):
        super(WolframAlphaSpokenEndpoint, self).__init__()
        self.wolfram_alpha_key = os.environ['WOLFRAM_ALPHA_KEY']
        self.wolfram_alpha_url = os.environ['WOLFRAM_ALPHA_URL']

    def get(self):
        params = dict(self.request.args)
        params['appid'] = self.wolfram_alpha_key
        response = requests.get(self.wolfram_alpha_url + '/v1/spoken', params=params)
        code = response.status_code
        response = (response.text, code) if code == HTTPStatus.OK else ('', code)
        return response
