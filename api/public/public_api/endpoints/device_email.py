import json
import smtplib
from email.message import EmailMessage
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository
from selene.util.db import get_db_connection


class SendEmail(Model):
    title = StringType(required=True)
    sender = StringType(required=True)
    body = StringType(required=True)


class DeviceEmailEndpoint(PublicEndpoint):
    """Endpoint to send an email to the account associated to a device"""

    def __init__(self):
        super(DeviceEmailEndpoint, self).__init__()
        self.email_client: smtplib.SMTP = self.config['EMAIL_CLIENT']

    def post(self, device_id):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        send_email = SendEmail(payload)
        send_email.validate()

        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            account = AccountRepository(db).get_account_by_device_id(device_id)

        if account:
            message = EmailMessage()
            message['Subject'] = str(send_email.title)
            message['From'] = str(send_email.sender)
            message.set_content(str(send_email.body))
            message['To'] = account.email_address
            self.email_client.send_message(message)
            self.email_client.quit()
            response = '', HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response
