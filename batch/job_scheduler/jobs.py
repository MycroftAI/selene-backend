"""Define the commands to run Selene batch jobs and the execution schedule.

This module is run as a daemon on the Selene batch host.  It defines the
commands needed to run each job using the subprocess module.  The jobs are
scheduled using the "schedule" library.
"""
import os
import subprocess
import time
from datetime import date, timedelta

import schedule

from selene.util.log import configure_logger

_log = configure_logger('selene_job_scheduler')


class JobRunner(object):
    """Build the command to run a batch job and run it via subprocess."""
    def __init__(self, script_name: str):
        self.script_name = script_name
        self.job_args: str = None
        self.job_date: date = None

    def run_job(self):
        if self.job_date is not None:
            self._add_date_to_args()
        command = self._build_command()
        self._execute_command(command)

    def _add_date_to_args(self):
        """Adds a date argument to the argument string.

        The SeleneScript base class defaults the run date to current date so the
        date argument only needs to be specified when it is not current date.
        """
        if self.job_args is None:
            self.job_args = ''
        date_arg = ' --date ' + str(self.job_date)
        self.job_args += date_arg

    def _build_command(self):
        """Build the command to run the script."""
        command = ['pipenv', 'run', 'python']
        script_path = os.path.join(
            os.environ['SELENE_SCRIPT_DIR'],
            self.script_name
        )
        command.append(script_path)
        if self.job_args is not None:
            command.extend(self.job_args.split())
        _log.info(command)

        return command

    def _execute_command(self, command):
        """Run the script using the subprocess module."""
        result = subprocess.run(command, capture_output=True)
        if result.returncode:
            _log.error(
                'Job {job_name} failed\n'
                '\tSTDOUT - {stdout}'
                '\tSTDERR - {stderr}'.format(
                    job_name=self.script_name[:-3],
                    stdout=result.stdout.decode(),
                    stderr=result.stderr.decode()
                )
            )
        else:
            log_msg = 'Job {job_name} completed successfully'
            _log.info(log_msg.format(job_name=self.script_name[:-3]))


def test_scheduler():
    """Run in non-production environments to test scheduler functionality."""
    job_runner = JobRunner('test_scheduler.py')
    job_runner.job_date = date.today() - timedelta(days=1)
    job_runner.job_args = '--arg-with-value test --arg-no-value'
    job_runner.run_job()


def partition_api_metrics():
    """Copy rows from metric.api table to partitioned metric.api_history table

    Build a partition on the metric.api_history table for yesterday's date.
    Copy yesterday's metric.api table rows to the partition.
    """
    job_runner = JobRunner('partition_api_metrics.py')
    job_runner.job_date = date.today() - timedelta(days=1)
    job_runner.run_job()


def update_device_last_contact():
    """Update the last time a device was seen.

    Each time a device calls the public API, the Redis database is updated with
    to associate the time of the call with the device.  Dump the contents of
    the Redis data to the device.device table on the Postgres database.
    """
    job_runner = JobRunner('update_device_last_contact.py')
    job_runner.run_job()


# Define the schedule
if os.environ['SELENE_ENVIRONMENT'] != 'prod':
    schedule.every(5).minutes.do(test_scheduler)

schedule.every().day.at('00:00').do(partition_api_metrics)
schedule.every().day.at('00:05').do(update_device_last_contact)

# Run the schedule
while True:
    schedule.run_pending()
    time.sleep(1)
