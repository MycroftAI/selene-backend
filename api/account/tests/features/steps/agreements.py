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

from dataclasses import asdict
import json

from behave import then, when
from hamcrest import assert_that, equal_to

from selene.data.account import PRIVACY_POLICY, TERMS_OF_USE


@when('API request for {agreement} is made')
def call_agreement_endpoint(context, agreement):
    if agreement == PRIVACY_POLICY:
        url = '/api/agreement/privacy-policy'
    elif agreement == TERMS_OF_USE:
        url = '/api/agreement/terms-of-use'
    else:
        raise ValueError('invalid agreement type')

    context.response = context.client.get(url)


@then('{agreement} version {version} is returned')
def validate_response(context, agreement, version):
    response_data = json.loads(context.response.data)
    if agreement == PRIVACY_POLICY:
        expected_response = asdict(context.privacy_policy)
    elif agreement == TERMS_OF_USE:
        expected_response = asdict(context.terms_of_use)
    else:
        raise ValueError('invalid agreement type')

    del(expected_response['effective_date'])
    assert_that(response_data, equal_to(expected_response))
