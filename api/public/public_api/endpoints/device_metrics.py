import json
import os
from http import HTTPStatus

import requests

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository


class MetricsService(object):
    def __init__(self):
        self.metrics_service_host = os.environ['METRICS_SERVICE_HOST']

    def send_metric(self, metric: str, user_id: str, device_id: str, data: dict):
        body = dict(
            userUuid=user_id,
            deviceUuid=device_id,
            data=data
        )
        url = '{host}/metrics/{metric}'.format(host=self.metrics_service_host, metric=metric)
        requests.post(url, body)


class DeviceMetricsEndpoint(PublicEndpoint):
    """Endpoint to communicate with the metrics service"""

    def __init__(self):
        super(DeviceMetricsEndpoint, self).__init__()
        self.metrics_service: MetricsService = self.config['METRICS_SERVICE']

    def post(self, device_id, metric):
        self._authenticate(device_id)
        payload = json.loads(self.request.data)
        account = AccountRepository(self.db).get_account_by_device_id(device_id)
        if account:
            self.metrics_service.send_metric(metric, account.id, device_id, payload)
            response = '', HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response
