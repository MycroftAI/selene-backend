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
from datetime import datetime

from behave import given, then, when
from hamcrest import assert_that, equal_to, greater_than, not_none

from selene.data.account import AccountRepository
from selene.data.metric import AccountActivityRepository, CoreMetricRepository

METRIC_TYPE_TIMING = "timing"
metric_value = dict(type="timing", start="123")


@given("a device registered to a user opted {in_or_out} the open dataset")
def define_authorized_device(context, in_or_out):
    """
    Define a device.

    Args:
        context: (todo): write your description
        in_or_out: (int): write your description
    """
    context.metric_device_id = context.device_login["uuid"]


@given("a non-existent device")
def define_unauthorized_device(context):
    """
    Define a device.

    Args:
        context: (todo): write your description
    """
    context.metric_device_id = str(uuid.uuid4())


@when("someone issues a voice command to the device")
def call_metrics_endpoint(context):
    """
    Post metrics to provider metrics endpoint.

    Args:
        context: (todo): write your description
    """
    headers = dict(
        Authorization="Bearer {token}".format(token=context.device_login["accessToken"])
    )
    url = "/v1/device/{device_id}/metric/{metric}".format(
        device_id=context.metric_device_id, metric="timing"
    )
    context.client.content_type = "application/json"
    context.response = context.client.post(
        url,
        data=json.dumps(metric_value),
        content_type="application/json",
        headers=headers,
    )


@then("usage metrics are saved to the database")
def validate_metric_in_db(context):
    """
    Validate that the metric. metrics.

    Args:
        context: (todo): write your description
    """
    core_metric_repo = CoreMetricRepository(context.db)
    device_metrics = core_metric_repo.get_metrics_by_device(
        context.device_login["uuid"]
    )
    device_metric = device_metrics[0]
    assert_that(device_metric.metric_type, equal_to(METRIC_TYPE_TIMING))
    assert_that(device_metric.metric_value, equal_to(metric_value))
