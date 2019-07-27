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

import json
import uuid
from datetime import date
from http import HTTPStatus

from behave import when, then
from hamcrest import assert_that, has_entry, equal_to

from selene.data.account import AccountRepository, AccountMembership
from selene.util.db import connect_to_db


@when('the subscription endpoint is called')
def get_device_subscription(context):
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.subscription_response = context.client.get(
        '/v1/device/{uuid}/subscription'.format(uuid=device_id),
        headers=headers
    )


@then('free type should be returned')
def validate_response(context):
    response = context.subscription_response
    assert_that(response.status_code, HTTPStatus.OK)
    subscription = json.loads(response.data)
    assert_that(subscription, has_entry('@type', 'free'))


@when('the subscription endpoint is called for a monthly account')
def get_device_subscription(context):
    membership = AccountMembership(
        start_date=date.today(),
        type='Monthly Membership',
        payment_method='Stripe',
        payment_account_id='test_monthly',
        payment_id='stripe_id'
    )
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    AccountRepository(db).add_membership(context.account.id, membership)
    context.subscription_response = context.client.get(
        '/v1/device/{uuid}/subscription'.format(uuid=device_id),
        headers=headers
    )


@then('monthly type should be returned')
def validate_response_monthly(context):
    response = context.subscription_response
    assert_that(response.status_code, HTTPStatus.OK)
    subscription = json.loads(response.data)
    assert_that(subscription, has_entry('@type', 'Monthly Membership'))


@when('try to get the subscription for a nonexistent device')
def get_subscription_nonexistent_device(context):
    access_token = context.device_login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.invalid_subscription_response = context.client.get(
        '/v1/device/{uuid}/subscription'.format(uuid=str(uuid.uuid4())),
        headers=headers
    )


@then('401 status code should be returned for the subscription endpoint')
def validate_nonexistent_device(context):
    response = context.invalid_subscription_response
    assert_that(response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))
