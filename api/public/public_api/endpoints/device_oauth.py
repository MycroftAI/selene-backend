import requests

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository
from selene.util.db import get_db_connection


class OauthServiceEndpoint(PublicEndpoint):

    def __init__(self):
        super(OauthServiceEndpoint, self).__init__()
        self.oauth_service_host = self.config['OAUTH_BASE_URL']

    def get(self, device_id, credentials, oauth_path):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            account = AccountRepository(db).get_account_by_device_id(device_id)
        uuid = account.id
        url = '{host}/auth/{credentials}/{oauth_path}'.format(
            host=self.oauth_service_host,
            credentials=credentials,
            oauth_path=oauth_path
        )
        params = dict(uuid=uuid)
        return requests.get(url, params=params)
