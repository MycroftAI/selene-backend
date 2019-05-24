import json
import os
import smtplib
from email.message import EmailMessage
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository


class SendEmail(Model):
    title = StringType(required=True)
    sender = StringType(required=True)
    body = StringType(required=True)


class DeviceEmailEndpoint(PublicEndpoint):
    """Endpoint to send an email to the account associated to a device"""

    def __init__(self):
        super(DeviceEmailEndpoint, self).__init__()

    def put(self, device_id):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        send_email = SendEmail(payload)
        send_email.validate()

        account = AccountRepository(self.db).get_account_by_device_id(device_id)

        if account:
            message = EmailMessage()
            message['Subject'] = str(send_email.title)
            message['From'] = str(send_email.sender)
            message.set_content(str(send_email.body))
            message['To'] = account.email_address
            self._send_email(message)
            response = '', HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response

    def _send_email(self, message: EmailMessage):
        email_client = self.config.get('EMAIL_CLIENT')
        if email_client is None:
            host = os.environ['EMAIL_SERVICE_HOST']
            port = os.environ['EMAIL_SERVICE_PORT']
            user = os.environ['EMAIL_SERVICE_USER']
            password = os.environ['EMAIL_SERVICE_PASSWORD']
            email_client = smtplib.SMTP(host, port)
            email_client.login(user, password)
        email_client.send_message(message)
        email_client.quit()
