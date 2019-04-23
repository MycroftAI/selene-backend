from binascii import a2b_base64
from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository


class PasswordChangeEndpoint(SeleneEndpoint):
    def put(self):
        account_id = self.request.json['accountId']
        coded_password = self.request.json['password']
        binary_password = a2b_base64(coded_password)
        password = binary_password.decode()
        acct_repository = AccountRepository(self.db)
        acct_repository.change_password(account_id, password)

        return '', HTTPStatus.NO_CONTENT
