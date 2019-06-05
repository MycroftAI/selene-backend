import os
from dataclasses import dataclass
from logging import getLogger

from jinja2 import Template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Mail

_log = getLogger(__package__)


@dataclass
class EmailMessage(object):
    recipient: str
    sender: str
    subject: str
    template_file_name: str
    template_variables: dict = None
    content_type: str = 'text/html'


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

    def send(self, using_jinja=False):
        message = Mail(
            from_email=self.message.sender,
            to_emails=[self.message.recipient],
            subject=self.message.subject,
            html_content=self._build_content(using_jinja)
        )
        response = self.mailer.client.mail.send.post(request_body=message.get())

        if response.status_code < 300:
            _log.info('Email sent successfully')
        else:
            _log.error(
                'Email failed to send.  Status code: {}  '
                'Status message: {}'.format(response.status_code, response.body)
            )

    def _build_content(self, using_jinja=False) -> Content:
        with open(self.template_path) as template_file:
            email_content = template_file.read()
        if self.message.template_variables is not None:
            if using_jinja:
                template = Template(email_content)
                email_content = template.render(**self.message.template_variables)
            else:
                email_content = email_content.format(
                    **self.message.template_variables
                )
        return Content(self.message.content_type, email_content)
