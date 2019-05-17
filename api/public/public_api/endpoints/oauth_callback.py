import os

import requests

from selene.api import PublicEndpoint


class OauthCallbackEndpoint(PublicEndpoint):

    def __init__(self):
        super(OauthCallbackEndpoint, self).__init__()
        self.oauth_service_host = os.environ['OAUTH_BASE_URL']

    def get(self):
        params = dict(self.request.args)
        url = self.oauth_service_host + '/auth/callback'
        response = requests.get(url, params=params)
        return response.text, response.status_code
