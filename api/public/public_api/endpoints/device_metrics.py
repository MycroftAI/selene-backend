from datetime import datetime
from http import HTTPStatus

from selene.api import PublicEndpoint
from selene.data.metrics import CoreMetric, CoreMetricRepository


class DeviceMetricsEndpoint(PublicEndpoint):
    """Endpoint to communicate with the metrics service"""

    def post(self, device_id, metric):
        self._authenticate(device_id)
        core_metric = CoreMetric(
            device_id=device_id,
            metric_type=metric,
            insert_ts=datetime.now(),
            metric_value=self.request.json
        )
        self._add_metric(core_metric)
        return '', HTTPStatus.NO_CONTENT

    def _add_metric(self, metric: CoreMetric):
        core_metrics_repo = CoreMetricRepository(self.db)
        core_metrics_repo.add(metric)
