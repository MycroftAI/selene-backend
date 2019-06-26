import json
from datetime import datetime
from http import HTTPStatus

from flask import current_app, Blueprint, g as global_context
from schematics.exceptions import DataError

from selene.data.metrics import ApiMetric, ApiMetricsRepository
from selene.util.auth import AuthenticationError
from selene.util.cache import DEVICE_LAST_CONTACT_KEY
from selene.util.db import connect_to_db
from selene.util.exceptions import NotModifiedException

selene_api = Blueprint('selene_api', __name__)


@selene_api.app_errorhandler(DataError)
def handle_data_error(error):
    return json.dumps(error.to_primitive()), HTTPStatus.BAD_REQUEST


@selene_api.app_errorhandler(AuthenticationError)
def handle_data_error(error):
    return dict(error=str(error)), HTTPStatus.UNAUTHORIZED


@selene_api.app_errorhandler(NotModifiedException)
def handle_not_modified(_):
    return '', HTTPStatus.NOT_MODIFIED


@selene_api.before_app_request
def setup_request():
    global_context.start_ts = datetime.utcnow()


@selene_api.after_app_request
def teardown_request(response):
    add_api_metric(response.status_code)
    update_device_last_contact()

    return response


def add_api_metric(http_status):
    """Add a row to the table tracking metrics for API calls"""
    api = None
    # We are not logging metrics for the public API until after the socket
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

        api_metric = ApiMetric(
            access_ts=datetime.utcnow(),
            account_id=account_id,
            api=api,
            device_id=device_id,
            duration=(datetime.utcnow() - global_context.start_ts).microseconds,
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
