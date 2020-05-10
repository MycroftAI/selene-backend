# Mycroft Server - Backend
# Copyright (C) 2020 Mycroft AI Inc
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
"""Step functions for single sign on agreement tests."""
from behave import then, when

from selene.testing.agreement import (
    get_agreements_from_api,
    validate_agreement_response
)


@when('API request for {agreement} is made')
def call_agreement_endpoint(context, agreement):
    get_agreements_from_api(context, agreement)


@then('the current version of the {agreement} agreement is returned')
def validate_response(context, agreement):
    validate_agreement_response(context, agreement)
