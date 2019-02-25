import json
import os
from http import HTTPStatus

import requests

from selene.api import SeleneEndpoint
from selene.data.account import AccountRepository
from selene.util.db import get_db_connection


class MetricsService(object):
    def __init__(self):
        self.metrics_service_host = os.environ['METRICS_SERVICE_HOST']

    def send_metric(self, metric: str, user_id: str, device_id: str, data: dict):
        body = dict(
            userUuid=user_id,
            deviceUuid=device_id,
            data=data
        )
        url = '{host}/{metric}'.format(host=self.metrics_service_host, metric=metric)
        requests.post(url, body)


class DeviceMetricsEndpoint(SeleneEndpoint):
    """Endpoint to communicate with the metrics service"""

    def __init__(self):
        super(DeviceMetricsEndpoint, self).__init__()
        self.metrics_service: MetricsService = self.config['METRICS_SERVICE']

    def post(self, device_id, metric):
        payload = json.loads(self.request.data)
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            account = AccountRepository(db).get_account_by_device_id(device_id)
        if account:
            self.metrics_service.send_metric(metric, account.id, device_id, payload)
            response = '', HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response
