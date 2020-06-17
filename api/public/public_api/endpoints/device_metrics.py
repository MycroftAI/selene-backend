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
from datetime import datetime
from http import HTTPStatus

from selene.api import PublicEndpoint, track_account_activity
from selene.data.metric import CoreMetric, CoreMetricRepository


class DeviceMetricsEndpoint(PublicEndpoint):
    """Endpoint to communicate with the metric service"""

    def post(self, device_id, metric):
        self._authenticate(device_id)
        self._add_core_metric(metric)
        track_account_activity(self.db, self.device_id)

        return "", HTTPStatus.NO_CONTENT

    def _add_core_metric(self, metric: str):
        core_metric = CoreMetric(
            device_id=self.device_id, metric_type=metric, metric_value=self.request.json
        )
        core_metrics_repo = CoreMetricRepository(self.db)
        core_metrics_repo.add(core_metric)
