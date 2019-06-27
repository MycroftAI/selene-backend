import os
import subprocess
import time

import schedule

from selene.util.log import configure_logger

_log = configure_logger('selene_job_scheduler')


def run_job(script_name: str, script_args: str = None):
    command = ['pipenv', 'run', 'python']
    script_path = os.path.join(
        os.environ['SELENE_SCRIPT_DIR'],
        script_name
    )
    command.append(script_path)
    if script_args is not None:
        command.extend(script_args.split())
    _log.info(command)
    result = subprocess.run(command, capture_output=True)
    if result.returncode:
        _log.error(
            'Job {job_name} failed\n'
            '\tSTDOUT - {stdout}'
            '\tSTDERR - {stderr}'.format(
                job_name=script_name[:-3],
                stdout=result.stdout.decode(),
                stderr=result.stderr.decode()
            )
        )
    else:
        log_msg = 'Job {job_name} completed successfully'
        _log.info(log_msg.format(job_name=script_name[:-3]))


# Define the schedule
schedule.every().day.at('00:00').do(run_job, 'partition_api_metrics.py')
schedule.every().day.at('00:05').do(run_job, 'update_device_last_contact.py')

while True:
    schedule.run_pending()
    time.sleep(1)
