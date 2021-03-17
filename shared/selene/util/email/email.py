# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""Utilities to send and email using SendGrid"""
from dataclasses import dataclass
from logging import getLogger
from os import environ
from pathlib import Path

from jinja2 import Template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Mail

_log = getLogger(__package__)


@dataclass
class EmailMessage:
    """Data representation of an email to be sent."""

    recipient: str
    sender: str
    subject: str
    body: str = None
    template_file_name: str = None
    template_variables: dict = None
    content_type: str = "text/html"

    def __post_init__(self):
        if self.body is not None and self.template_file_name is not None:
            raise ValueError("Specify body or template file name, not both.")
        if self.body is None and self.template_file_name is None:
            raise ValueError("One of body or template file name must be supplied.")


class SeleneMailer:
    """Use the SendGrid API to send an email."""

    template_directory = Path(__file__).parent.joinpath("templates")

    def __init__(self, message: EmailMessage):
        self.mailer = SendGridAPIClient(api_key=environ["SENDGRID_API_KEY"])
        self.message = message

    def send(self, using_jinja=False):
        """Send the email."""
        message = Mail(
            from_email=self.message.sender,
            to_emails=[self.message.recipient],
            subject=self.message.subject,
            html_content=self._build_content(using_jinja),
        )
        response = self.mailer.client.mail.send.post(request_body=message.get())

        if response.status_code < 300:
            _log.info("Email sent successfully")
        else:
            _log.error(
                "Email failed to send.  Status code: {}  "
                "Status message: {}".format(response.status_code, response.body)
            )

    def _build_content(self, using_jinja) -> Content:
        """Build the content of the email from a template or a predefined body."""
        if self.message.body:
            message_content = self.message.body
        else:
            message_content = self._build_content_from_template(using_jinja)

        return Content(self.message.content_type, message_content)

    def _build_content_from_template(self, using_jinja):
        """Format an HTML template that will be the email body."""
        template_path = self.template_directory.joinpath(
            self.message.template_file_name
        )
        with open(template_path) as template_file:
            email_content = template_file.read()
        if self.message.template_variables is not None:
            if using_jinja:
                template = Template(email_content)
                email_content = template.render(**self.message.template_variables)
            else:
                email_content = email_content.format(**self.message.template_variables)

        return email_content
