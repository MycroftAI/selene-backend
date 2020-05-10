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
from behave import then
from hamcrest import assert_that, equal_to, not_none

from selene.testing.api import check_http_success, check_http_error


@then('the request will be successful')
def check_request_success(context):
    check_http_success(context)


@then('the request will fail with {error_type} error')
def check_for_bad_request(context, error_type):
    check_http_error(context, error_type)


@then('the response will contain a error message')
def check_error_message(context):
    assert_that(context.response.data, not_none())


@then('the response will contain a "{error_msg}" error message')
def check_error_message(context, error_msg):
    assert_that(context.response.json['error'], equal_to(error_msg))
