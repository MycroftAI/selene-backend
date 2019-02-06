"""Log a user out of Mycroft web sites"""

from http import HTTPStatus
from logging import getLogger

from selene.account import RefreshTokenRepository
from selene.api import SeleneEndpoint
from selene.util.db import get_db_connection

_log = getLogger(__package__)


class LogoutEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        if self.authenticated or self.refresh_token_expired:
            self._logout()

        return self.response

    def _logout(self):
        request_refresh_token = self.request.cookies['seleneRefresh']
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            token_repository = RefreshTokenRepository(db, self.account)
            token_repository.delete_refresh_token(request_refresh_token)
        access_token, refresh_token = self._generate_tokens()
        self._set_token_cookies(access_token, refresh_token, expire=True)

        self.response = ('logged out', HTTPStatus.OK)
