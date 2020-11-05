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
from dataclasses import asdict
from datetime import date
from typing import List
from ..entity.core import CoreMetric, CoreInteraction
from ...repository_base import RepositoryBase


class CoreMetricRepository(RepositoryBase):
    def __init__(self, db):
        """
        Initialize the database

        Args:
            self: (todo): write your description
            db: (todo): write your description
        """
        super(CoreMetricRepository, self).__init__(db, __file__)

    def add(self, metric: CoreMetric):
        """
        Add a metric to the database.

        Args:
            self: (todo): write your description
            metric: (str): write your description
        """
        db_request_args = asdict(metric)
        db_request_args['metric_value'] = json.dumps(
            db_request_args['metric_value']
        )
        db_request = self._build_db_request(
            sql_file_name='add_core_metric.sql',
            args=db_request_args
        )
        self.cursor.insert(db_request)

    def get_metrics_by_device(self, device_id):
        """
        Retrieve metrics by device by device.

        Args:
            self: (todo): write your description
            device_id: (int): write your description
        """
        return self._select_all_into_dataclass(
            CoreMetric,
            sql_file_name='get_core_metric_by_device.sql',
            args=dict(device_id=device_id)
        )

    def get_metrics_by_date(self, metric_date: date) -> List[CoreMetric]:
        """
        Gets all metrics for a given metric.

        Args:
            self: (todo): write your description
            metric_date: (str): write your description
        """
        return self._select_all_into_dataclass(
            CoreMetric,
            sql_file_name='get_core_timing_metrics_by_date.sql',
            args=dict(metric_date=metric_date)
        )

    def add_interaction(self, interaction: CoreInteraction) -> str:
        """
        Add an interaction to the database.

        Args:
            self: (todo): write your description
            interaction: (todo): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='add_core_interaction.sql',
            args=asdict(interaction)
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result.id
