import os

from flask_restful import http_status_message
from selene.api import SeleneEndpoint
import smtplib

from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection
from email.message import EmailMessage


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
        email_parameters = self.request.get_json()

        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            email_address = DeviceRepository(db).get_account_email_by_device_id(device_id)
        if 'title' in email_parameters and 'body' in email_parameters and 'sender' in email_parameters and email_address:
            message = EmailMessage()
            message['Subject'] = email_parameters['title']
            message['From'] = email_parameters['sender']
            message.set_content(email_parameters['body'])
            message['To'] = email_address
            self.email_client.send_message(message)
            self.email_client.quit()
            return http_status_message(200)
        return http_status_message(204)
