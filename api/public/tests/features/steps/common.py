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

from http import HTTPStatus
from datetime import datetime

from behave import given, then
from hamcrest import assert_that, equal_to, is_in, not_none

from selene.data.account import AccountRepository
from selene.data.metric import AccountActivityRepository
from selene.util.cache import DEVICE_LAST_CONTACT_KEY


@then("the device's last contact time is updated")
def check_device_last_contact(context):
    """
    Check if contact contact contact is valid.

    Args:
        context: (todo): write your description
    """
    key = DEVICE_LAST_CONTACT_KEY.format(device_id=context.device_id)
    value = context.cache.get(key).decode()
    assert_that(value, not_none())

    last_contact_ts = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
    assert_that(last_contact_ts.date(), equal_to(datetime.utcnow().date()))


@then("the request will be successful")
def check_request_success(context):
    """
    Check if the request was successful.

    Args:
        context: (todo): write your description
    """
    assert_that(
        context.response.status_code, is_in([HTTPStatus.OK, HTTPStatus.NO_CONTENT])
    )


@then('the request will succeed with a "not modified" return code')
def check_request_success(context):
    """
    Check if the request was successful.

    Args:
        context: (todo): write your description
    """
    assert_that(context.response.status_code, equal_to(HTTPStatus.NOT_MODIFIED))


@then("the request will fail with {error_type} error")
def check_for_bad_request(context, error_type):
    """
    Checks the bad bad bad response.

    Args:
        context: (todo): write your description
        error_type: (todo): write your description
    """
    if error_type == "a bad request":
        assert_that(context.response.status_code, equal_to(HTTPStatus.BAD_REQUEST))
    elif error_type == "an unauthorized":
        assert_that(context.response.status_code, equal_to(HTTPStatus.UNAUTHORIZED))
    else:
        raise ValueError("unsupported error_type")


@given("an authorized device")
def build_request_header(context):
    """
    Builds the request context.

    Args:
        context: (todo): write your description
    """
    context.request_header = dict(
        Authorization="Bearer {token}".format(token=context.access_token)
    )


@given("an unauthorized device")
def build_unauthorized_request_header(context):
    """
    Builds the request context.

    Args:
        context: (todo): write your description
    """
    context.request_header = dict(
        Authorization="Bearer {token}".format(token="bogus_token")
    )


@then("the account's last activity time is updated")
def validate_account_last_activity(context):
    """
    Check if activity activity.

    Args:
        context: (todo): write your description
    """
    account_repo = AccountRepository(context.db)
    account = account_repo.get_account_by_device_id(context.device_login["uuid"])
    assert_that(account.last_activity, not_none())
    assert_that(account.last_activity.date(), equal_to(datetime.utcnow().date()))


@then("the account activity metrics will be updated")
def validate_account_activity_metrics(context):
    """
    Validate activity activity activity.

    Args:
        context: (todo): write your description
    """
    account_activity_repo = AccountActivityRepository(context.db)
    account_activity = account_activity_repo.get_activity_by_date(
        datetime.utcnow().date()
    )
    assert_that(account_activity.accounts_active, equal_to(1))
    assert_that(account_activity.members_active, equal_to(0))
    assert_that(account_activity.open_dataset_active, equal_to(1))
