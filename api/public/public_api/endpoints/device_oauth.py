import os

import requests

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository


class OauthServiceEndpoint(PublicEndpoint):

    def __init__(self):
        super(OauthServiceEndpoint, self).__init__()
        self.oauth_service_host = os.environ['OAUTH_BASE_URL']

    def get(self, device_id, credentials, oauth_path):
        account = AccountRepository(self.db).get_account_by_device_id(device_id)
        uuid = account.id
        url = '{host}/auth/{credentials}/{oauth_path}'.format(
            host=self.oauth_service_host,
            credentials=credentials,
            oauth_path=oauth_path
        )
        params = dict(uuid=uuid)
        response = requests.get(url, params=params)
        return response.text, response.status_code
