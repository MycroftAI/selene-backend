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

from dataclasses import asdict

from ...repository_base import RepositoryBase
from ..entity.job import JobMetric


class JobRepository(RepositoryBase):
    def __init__(self, db):
        super(JobRepository, self).__init__(db, __file__)

    def add(self, job: JobMetric):
        db_request = self._build_db_request(
            sql_file_name='add_job_metric.sql',
            args=asdict(job)
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result.id
