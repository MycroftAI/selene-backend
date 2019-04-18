"""Log a user out of Mycroft web sites"""

from http import HTTPStatus
from logging import getLogger

from selene.api import SeleneEndpoint

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
        self._generate_tokens()
        self._set_token_cookies(expire=True)

        self.response = ('', HTTPStatus.NO_CONTENT)
