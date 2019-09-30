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

"""
Base class that should be inherited by any batch job.

The logic in this class handles boilerplate code that is required for all batch
jobs, such as argument parsing, logging setup and database connectivity.
"""
from argparse import ArgumentParser
from datetime import date, datetime
from os import environ, path
import sys

from selene.data.metric import JobMetric, JobRepository
from selene.util.db import DatabaseConnectionConfig, connect_to_db
from selene.util.log import configure_logger


class SeleneScript(object):
    _db = None
    _job_name = None

    def __init__(self, job_file_path):
        self._job_file_path = job_file_path
        self.log = configure_logger(self.job_name)
        self._arg_parser = ArgumentParser()
        self.args = None
        self.start_ts = datetime.now()
        self.end_ts = None
        self.success = False

    @property
    def job_name(self):
        if self._job_name is None:
            job_file_name = path.basename(self._job_file_path)
            self._job_name = job_file_name[:-3]

        return self._job_name

    @property
    def db(self):
        """Connect to the mycroft database"""
        if self._db is None:
            db_connection_config = DatabaseConnectionConfig(
                host=environ['DB_HOST'],
                db_name=environ['DB_NAME'],
                password=environ['DB_PASSWORD'],
                port=environ.get('DB_PORT', 5432),
                user=environ['DB_USER'],
                sslmode=environ.get('DB_SSLMODE'),
                use_namedtuple_cursor=True
            )
            self._db = connect_to_db(db_connection_config)

        return self._db

    def run(self):
        """Call this method to run the job."""
        try:
            self._start_job()
            self._run()
            self.success = True
        except:
            self.log.exception('An exception occurred - aborting script')
            raise
        finally:
            self._finish_job()

    def _start_job(self):
        """Initialization tasks."""
        # Logger builds daily files, delineate start in case of multiple runs
        self.log.info('* * * * *  START OF JOB  * * * * *')
        self._define_args()
        self.args = self._arg_parser.parse_args()

    def _define_args(self):
        """Define the command-line arguments for the batch job."""
        self._arg_parser.add_argument(
            "--date",
            default=date.today(),
            help='Processing date in YYYY-MM-DD format',
            type=lambda dt: datetime.strptime(dt, '%Y-%m-%d').date()
        )

    def _run(self):
        """Subclass must override this to perform job-specific logic"""
        raise NotImplementedError

    def _finish_job(self):
        """Tie up any loose ends."""
        self.end_ts = datetime.now()
        self._insert_metrics()
        self.db.close()
        self.log.info(
            'script run time: ' + str(self.end_ts - self.start_ts)
        )
        # Logger builds daily files, delineate end in case of multiple runs
        self.log.info('* * * * *  END OF JOB  * * * * *')

    def _insert_metrics(self):
        """Add a row to the job metric table for monitoring purposes."""
        if self.args is not None:
            job_repository = JobRepository(self.db)
            job_metric = JobMetric(
                job_name=self.job_name,
                batch_date=self.args.date,
                start_ts=self.start_ts,
                end_ts=self.end_ts,
                command=' '.join(sys.argv),
                success=self.success
            )
            job_id = job_repository.add(job_metric)
            self.log.info('Job ID: ' + job_id)
