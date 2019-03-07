import os
from http import HTTPStatus

import requests
from flask import Response

from selene.api import PublicEndpoint


class WolframAlphaEndpoint(PublicEndpoint):
    """Proxy to the Wolfram Alpha API"""
    def __init__(self):
        super(WolframAlphaEndpoint, self).__init__()
        self.wolfram_alpha_key = os.environ['WOLFRAM_ALPHA_KEY']
        self.wolfram_alpha_url = os.environ['WOLFRAM_ALPHA_URL']

    def get(self):
        self._authenticate()
        input = self.request.args.get('input')
        if input:
            params = dict(appid=self.wolfram_alpha_key, input=input)
            response = requests.get(self.wolfram_alpha_url + '/v2/query', params=params)
            if response.status_code == HTTPStatus.OK:
                return Response(response.content, mimetype='text/xml')
