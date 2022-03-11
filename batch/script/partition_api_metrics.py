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

"""Copy api metric from a transient table to a partitioned table.

Millions of rows per day are added to the metric.api table.  To help with
query performance, copy the rows from this table to a partitioned table on a
daily basis.
"""
from selene.batch.base import SeleneScript
from selene.data.metric import ApiMetricsRepository
from selene.util.db import use_transaction


class PartitionApiMetrics(SeleneScript):
    def __init__(self):
        super(PartitionApiMetrics, self).__init__(__file__)

    @use_transaction
    def _run(self):
        api_metrics_repo = ApiMetricsRepository(self.db)
        api_metrics_repo.create_partition(self.args.date)
        api_metrics_repo.copy_to_partition(self.args.date)
        api_metrics_repo.remove_by_date(self.args.date)


if __name__ == "__main__":
    PartitionApiMetrics().run()
