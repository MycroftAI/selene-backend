from dataclasses import dataclass
from logging import getLogger
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail

_log = getLogger(__package__)


@dataclass
class EmailMessage(object):
    recipient: str
    sender: str
    subject: str
    template_file_name: str
    template_variables: dict = None
    content_type: str = 'text/html'

    def __post_init__(self):
        self.recipient = Email(self.recipient)
        self.sender = Email(self.sender)


class SeleneMailer(object):
    template_directory = os.path.join(os.path.dirname(__file__), 'templates')

    def __init__(self, message: EmailMessage):
        self.mailer = SendGridAPIClient(api_key=os.environ['SENDGRID_API_KEY'])
        self.message = message

    @property
    def template_path(self):
        return os.path.join(
            self.template_directory,
            self.message.template_file_name
        )

    def send(self):
        message = Mail(
            self.message.sender,
            self.message.subject,
            self.message.recipient,
            self._build_content()
        )
        response = self.mailer.client.mail.send.post(request_body=message.get())

        if response.status_code < 300:
            _log.info('Email sent successfully')
        else:
            _log.error(
                'Email failed to send.  Status code: {}  '
                'Status message: {}'.format(response.status_code, response.body)
            )

    def _build_content(self) -> Content:
        with open(self.template_path) as template_file:
            email_content = template_file.read()
        if self.message.template_variables is not None:
            email_content = email_content.format(
                **self.message.template_variables
            )

        return Content(self.message.content_type, email_content)
