"""Log a user out of Mycroft web sites"""

from http import HTTPStatus
from logging import getLogger

from selene.data.account import RefreshTokenRepository
from selene.api import SeleneEndpoint
from selene.util.db import get_db_connection

_log = getLogger(__package__)


class LogoutEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        self._logout()

        return self.response

    def _logout(self):
        """Delete tokens from database and expire the token cookies.

        An absence of tokens will force the user to re-authenticate next time
        they visit the site.
        """
        request_refresh_token = self.request.cookies['seleneRefresh']
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            token_repository = RefreshTokenRepository(db, self.account.id)
            token_repository.delete_refresh_token(request_refresh_token)
        self._generate_tokens()
        self._set_token_cookies(expire=True)

        self.response = ('logged out', HTTPStatus.OK)
