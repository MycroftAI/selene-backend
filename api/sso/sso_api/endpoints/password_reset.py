from http import HTTPStatus
import os

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository
from selene.util.auth import AuthenticationToken
from selene.util.db import get_db_connection
from selene.util.email import EmailMessage, SeleneMailer

ONE_HOUR = 3600


class PasswordResetEndpoint(SeleneEndpoint):
    def post(self):
        self._get_account_from_email()
        if self.account is None:
            self._send_account_not_found_email()
        else:
            reset_token = self._generate_reset_token()
            self._send_reset_email(reset_token)

        return '', HTTPStatus.OK

    def _get_account_from_email(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            acct_repository = AccountRepository(db)
            self.account = acct_repository.get_account_by_email(
                self.request.json['emailAddress']
            )

    def _generate_reset_token(self):
        reset_token = AuthenticationToken(
            self.config['ACCESS_SECRET'],
            ONE_HOUR
        )
        reset_token.generate(self.account.id)

        return reset_token.jwt

    def _send_reset_email(self, reset_token):
        url = '{base_url}/change-password?token={reset_token}'.format(
            base_url=os.environ['SSO_BASE_URL'],
            reset_token=reset_token
        )
        email = EmailMessage(
            recipient=self.request.json['emailAddress'],
            sender='Mycroft AI<no-reply@mycroft.ai>',
            subject='Password Reset Request',
            template_file_name='reset_password.html',
            template_variables=dict(reset_password_url=url)
        )
        mailer = SeleneMailer(email)
        mailer.send()

    def _send_account_not_found_email(self):
        email = EmailMessage(
            recipient=self.request.json['emailAddress'],
            sender='Mycroft AI<no-reply@mycroft.ai>',
            subject='Password Reset Request',
            template_file_name='account_not_found.html'
        )
        mailer = SeleneMailer(email)
        mailer.send()
