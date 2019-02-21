import json
import os
from http import HTTPStatus

from schematics import Model
from schematics.types import StringType

from selene.api import SeleneEndpoint
import smtplib

from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection
from email.message import EmailMessage


class SendEmail(Model):
    title = StringType(required=True)
    sender = StringType(required=True)
    body = StringType(required=True)


class DeviceEmailEndpoint(SeleneEndpoint):
    """Endpoint to send an email to the account associated to a device"""

    def __init__(self):
        super(DeviceEmailEndpoint, self).__init__()
        host = os.environ['EMAIL_SERVICE_HOST']
        port = os.environ['EMAIL_SERVICE_PORT']
        user = os.environ['EMAIL_SERVICE_USER']
        password = os.environ['EMAIL_SERVICE_PASSWORD']
        self.email_client = smtplib.SMTP(host, port)
        self.email_client.login(user, password)

    def post(self, device_id):
        payload = json.loads(self.request.data)
        send_email = SendEmail(payload)
        send_email.validate()

        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            email_address = DeviceRepository(db).get_account_email_by_device_id(device_id)

        if email_address:
            message = EmailMessage()
            message['Subject'] = str(send_email.title)
            message['From'] = str(send_email.sender)
            message.set_content(str(send_email.body))
            message['To'] = email_address
            self.email_client.send_message(message)
            self.email_client.quit()
            response = '', HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response
