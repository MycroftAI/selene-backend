import os

import requests
from flask.views import MethodView


class OauthCallbackEndpoint(MethodView):

    def __init__(self):
        self.oauth_service_host = os.environ['OAUTH_BASE_URL']

    def get(self):
        params = dict(self.request.args)
        url = self.oauth_service_host + '/auth/callback'
        return requests.get(url, params=params)
