from binascii import a2b_base64
from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository
from selene.util.db import get_db_connection


class PasswordChangeEndpoint(SeleneEndpoint):
    def put(self):
        account_id = self.request.json['accountId']
        coded_password = self.request.json['password']
        binary_password = a2b_base64(coded_password)
        password = binary_password.decode()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            acct_repository = AccountRepository(db)
            acct_repository.change_password(account_id, password)

        return '', HTTPStatus.NO_CONTENT
