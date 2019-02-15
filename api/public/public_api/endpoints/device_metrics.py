import os
from http import HTTPStatus

import requests
from selene.api import SeleneEndpoint
from selene.data.device import DeviceRepository
from selene.util.db import get_db_connection


class DeviceMetricsEndpoint(SeleneEndpoint):
    """Endpoint to communicate with the metrics service"""

    def __init__(self):
        super(DeviceMetricsEndpoint, self).__init__()
        self.metrics_service_host = os.environ['METRICS_SERVICE_HOST']

    def post(self, device_id, metric):
        payload = self.request.get_json()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            account_id = DeviceRepository(db).get_account_id_by_device_id(device_id)
        if account_id:
            body = dict(
                userUuid=account_id,
                deviceUuid=device_id,
                data=payload
            )
            url = '{host}/{metric}'.format(host=self.metrics_service_host, metric=metric)
            requests.post(url, body)
            response = '', HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response
