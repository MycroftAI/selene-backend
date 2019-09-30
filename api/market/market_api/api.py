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

"""Entry point for the API that supports the Mycroft Marketplace."""
from flask import Flask

from selene.api import get_base_config, selene_api, SeleneResponse
from selene.api.endpoints import AccountEndpoint
from selene.util.cache import SeleneCache
from selene.util.log import configure_logger
from .endpoints import (
    AvailableSkillsEndpoint,
    SkillDetailEndpoint,
    SkillInstallEndpoint,
    SkillInstallStatusEndpoint
)

_log = configure_logger('market_api')

# Define the Flask application
market = Flask(__name__)
market.config.from_object(get_base_config())
market.response_class = SeleneResponse
market.register_blueprint(selene_api)
market.config['SELENE_CACHE'] = SeleneCache()

# Define the API and its endpoints.
account_endpoint = AccountEndpoint.as_view('account_endpoint')
market.add_url_rule(
    '/api/account',
    view_func=account_endpoint,
    methods=['GET']
)

available_endpoint = AvailableSkillsEndpoint.as_view('available_endpoint')
market.add_url_rule(
    '/api/skills/available',
    view_func=available_endpoint,
    methods=['GET']
)

status_endpoint = SkillInstallStatusEndpoint.as_view('status_endpoint')
market.add_url_rule(
    '/api/skills/status',
    view_func=status_endpoint,
    methods=['GET']
)

skill_detail_endpoint = SkillDetailEndpoint.as_view('skill_detail_endpoint')
market.add_url_rule(
    '/api/skills/<string:skill_display_id>',
    view_func=skill_detail_endpoint,
    methods=['GET']
)

install_endpoint = SkillInstallEndpoint.as_view('install_endpoint')
market.add_url_rule(
    '/api/skills/install',
    view_func=install_endpoint,
    methods=['PUT']
)
