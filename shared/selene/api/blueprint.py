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
from datetime import datetime
from decimal import Decimal
from http import HTTPStatus

from flask import current_app, Blueprint, g as global_context, request
from schematics.exceptions import DataError

from selene.data.metric import ApiMetric, ApiMetricsRepository
from selene.util.auth import AuthenticationError
from selene.util.cache import DEVICE_LAST_CONTACT_KEY
from selene.util.db import connect_to_db
from selene.util.exceptions import NotModifiedException

selene_api = Blueprint('selene_api', __name__)


@selene_api.app_errorhandler(DataError)
def handle_data_error(error):
    """
    Convert json error.

    Args:
        error: (todo): write your description
    """
    return json.dumps(error.to_primitive()), HTTPStatus.BAD_REQUEST


@selene_api.app_errorhandler(AuthenticationError)
def handle_data_error(error):
    """
    Convert the error response.

    Args:
        error: (todo): write your description
    """
    return dict(error=str(error)), HTTPStatus.UNAUTHORIZED


@selene_api.app_errorhandler(NotModifiedException)
def handle_not_modified(_):
    """
    Returns true if the request was modified.

    Args:
        _: (todo): write your description
    """
    return '', HTTPStatus.NOT_MODIFIED


@selene_api.before_app_request
def setup_request():
    """
    Setup the global request.

    Args:
    """
    global_context.start_ts = datetime.utcnow()


@selene_api.after_app_request
def teardown_request(response):
    """
    Teardown request.

    Args:
        response: (todo): write your description
    """
    add_api_metric(response.status_code)
    update_device_last_contact()

    return response


def add_api_metric(http_status):
    """Add a row to the table tracking metric for API calls"""
    api = None
    # We are not logging metric for the public API until after the socket
    # implementation to avoid putting millions of rows a day on the table
    for api_name in ('account', 'sso', 'market', 'public'):
        if api_name in current_app.name:
            api = api_name

    if api is not None and int(http_status) != 304:
        if 'db' not in global_context:
            global_context.db = connect_to_db(
                current_app.config['DB_CONNECTION_CONFIG']
            )
        if 'account_id' in global_context:
            account_id = global_context.account_id
        else:
            account_id = None

        if 'device_id' in global_context:
            device_id = global_context.device_id
        else:
            device_id = None

        duration = (datetime.utcnow() - global_context.start_ts)
        api_metric = ApiMetric(
            access_ts=datetime.utcnow(),
            account_id=account_id,
            api=api,
            device_id=device_id,
            duration=Decimal(str(duration.total_seconds())),
            http_method=request.method,
            http_status=int(http_status),
            url=global_context.url
        )
        metric_repository = ApiMetricsRepository(global_context.db)
        metric_repository.add(api_metric)


def update_device_last_contact():
    """Update the timestamp on the device table indicating last contact.

    This should only be done on public API calls because we are tracking
    device activity only.
    """
    if 'public' in current_app.name and 'device_id' in global_context:
        key = DEVICE_LAST_CONTACT_KEY.format(device_id=global_context.device_id)
        global_context.cache.set(key, str(datetime.utcnow()))
