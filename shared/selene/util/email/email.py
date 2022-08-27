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
"""Utilities to send and email using SendGrid."""
from dataclasses import dataclass
from logging import getLogger
from os import environ
from pathlib import Path
from typing import Optional, Tuple

from email_validator import validate_email, EmailNotValidError
from jinja2 import Environment, PackageLoader, select_autoescape
from python_http_client import HTTPError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Mail

_log = getLogger(__name__)


def validate_email_address(email_address: str) -> Tuple[Optional[str], Optional[str]]:
    """Uses a third party package to validate an email address.

    :param email_address: email address supplied by user
    :return: the normalized email address if it is valid, and an error if not
    """
    normalized_address = None
    try:
        normalized_address = validate_email(email_address).email
    except EmailNotValidError as exc:
        error = str(exc)
    else:
        error = None

    return normalized_address, error


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


class SeleneMailer:  # pylint: disable=too-few-public-methods
    """Use the SendGrid API to send an email."""

    template_directory = Path(__file__).parent.joinpath("templates")

    def __init__(self, message: EmailMessage):
        self.mailer = SendGridAPIClient(api_key=environ["SENDGRID_API_KEY"])
        self.message = message

    def send(self, using_jinja: bool = False):
        """Send the email.

        :param using_jinja: indicates if the Jinja templating engine should be used
        :raises: HTTPError if the email delivery is unsuccessful
        """
        message = Mail(
            from_email=self.message.sender,
            to_emails=[self.message.recipient],
            subject=self.message.subject,
            html_content=self._build_content(using_jinja),
        )
        try:
            self.mailer.client.mail.send.post(request_body=message.get())
        except HTTPError as exc:
            _log.exception(f"Email failed to send: {exc.to_dict}")
            raise
        else:
            _log.info("Email sent successfully")

    def _build_content(self, using_jinja: bool) -> Content:
        """Build the content of the email from a template or a predefined body.

        :param using_jinja: indicates if the Jinja templating engine should be used
        :returns the email as it will be recognized in the SendGrid package
        """
        if self.message.body:
            message_content = self.message.body
        else:
            if using_jinja:
                message_content = self._build_content_from_jinja_template()
            else:
                message_content = self._build_content_from_html_template()

        return Content(self.message.content_type, message_content)

    def _build_content_from_html_template(self):
        """Format an HTML template that will be the email body."""
        template_path = self.template_directory.joinpath(
            self.message.template_file_name
        )
        with open(template_path, encoding="utf-8") as template_file:
            email_content = template_file.read()
        if self.message.template_variables is not None:
            email_content = email_content.format(**self.message.template_variables)

        return email_content

    def _build_content_from_jinja_template(self):
        """Uses the Jinja templating engine to populate the email content."""
        jinja_env = Environment(
            loader=PackageLoader("selene.util.email", "templates"),
            autoescape=select_autoescape(["html"]),
        )
        template = jinja_env.get_template(self.message.template_file_name)
        email_content = template.render(self.message.template_variables or {})

        return email_content
