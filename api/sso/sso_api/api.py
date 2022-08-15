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

"""Define the API that will support Mycroft single sign on (SSO)."""
import os

from flask import Flask, request

from selene.api import get_base_config, selene_api, SeleneResponse
from selene.api.endpoints import (
    AccountEndpoint,
    AgreementsEndpoint,
    ValidateEmailEndpoint,
)
from selene.util.log import configure_selene_logger
from .endpoints import (
    AuthenticateInternalEndpoint,
    GithubTokenEndpoint,
    LogoutEndpoint,
    PasswordChangeEndpoint,
    PasswordResetEndpoint,
    ValidateFederatedEndpoint,
    ValidateTokenEndpoint,
)

configure_selene_logger("sso_api")

# Define the Flask application
sso = Flask(__name__)
sso.config.from_object(get_base_config())
sso.config.update(RESET_SECRET=os.environ["JWT_RESET_SECRET"])
sso.config.update(GITHUB_CLIENT_ID=os.environ["GITHUB_CLIENT_ID"])
sso.config.update(GITHUB_CLIENT_SECRET=os.environ["GITHUB_CLIENT_SECRET"])
sso.response_class = SeleneResponse
sso.register_blueprint(selene_api)

# Define the endpoints
sso.add_url_rule(
    "/api/account",
    view_func=AccountEndpoint.as_view("account_endpoint"),
    methods=["POST"],
)

sso.add_url_rule(
    "/api/agreement/<string:agreement_type>",
    view_func=AgreementsEndpoint.as_view("agreements_endpoint"),
    methods=["GET"],
)

sso.add_url_rule(
    "/api/internal-login",
    view_func=AuthenticateInternalEndpoint.as_view("internal_login"),
    methods=["GET"],
)

sso.add_url_rule(
    "/api/github-token",
    view_func=GithubTokenEndpoint.as_view("github_token_endpoint"),
    methods=["GET"],
)

sso.add_url_rule(
    "/api/logout", view_func=LogoutEndpoint.as_view("logout"), methods=["GET"]
)

sso.add_url_rule(
    "/api/password-change",
    view_func=PasswordChangeEndpoint.as_view("password_change_endpoint"),
    methods=["PUT"],
)

sso.add_url_rule(
    "/api/password-reset",
    view_func=PasswordResetEndpoint.as_view("password_reset"),
    methods=["POST"],
)

sso.add_url_rule(
    "/api/validate-email",
    view_func=ValidateEmailEndpoint.as_view("validate_email"),
    methods=["GET"],
)

sso.add_url_rule(
    "/api/validate-federated",
    view_func=ValidateFederatedEndpoint.as_view("federated_login"),
    methods=["POST"],
)

sso.add_url_rule(
    "/api/validate-token",
    view_func=ValidateTokenEndpoint.as_view("validate_token"),
    methods=["POST"],
)


def add_cors_headers(response):
    """Allow any application to logout"""
    # if 'logout' in request.url:
    response.headers["Access-Control-Allow-Origin"] = "*"
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, POST, PUT"
        headers = request.headers.get("Access-Control-Request-Headers")
        if headers:
            response.headers["Access-Control-Allow-Headers"] = headers
    return response


sso.after_request(add_cors_headers)
