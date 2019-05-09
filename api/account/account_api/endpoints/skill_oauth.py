import os
from http import HTTPStatus

import requests

from selene.api import SeleneEndpoint


class SkillOauthEndpoint(SeleneEndpoint):
    def __init__(self):
        super(SkillOauthEndpoint, self).__init__()
        self.oauth_base_url = os.environ['OAUTH_BASE_URL']

    def get(self, oauth_id):
        self._authenticate()
        self._get_oauth_url(oauth_id)

        return '', HTTPStatus.NO_CONTENT

    def _get_oauth_url(self, oauth_id):
        url = '{base_url}/auth/{oauth_id}/auth_url?uuid={account_id}'.format(
            base_url=self.oauth_base_url,
            oauth_id=oauth_id,
            account_id=self.account.id
        )
        return requests.get(url)
