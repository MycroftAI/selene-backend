import os
from datetime import datetime
from os import environ

import schedule
import time

from selene.batch import SeleneScript
from selene.data.account import AccountRepository
from selene.util.db import DatabaseConnectionConfig
from selene.util.email import EmailMessage, SeleneMailer

mycroft_db = DatabaseConnectionConfig(
    host=environ['DB_HOST'],
    db_name=environ['DB_NAME'],
    user=environ['DB_USER'],
    password=environ['DB_PASSWORD'],
    port=environ['DB_PORT'],
    sslmode=environ['DB_SSL_MODE']
)


class DailyReport(SeleneScript):
    def __init__(self):
        super(DailyReport, self).__init__(__file__)
        self._arg_parser.add_argument(
            '--run-mode',
            help='If the script should run as a job or just once',
            choices=['job', 'once'],
            type=str,
            default='job'
        )

    def _run(self):
        if self.args.run_mode == 'job':
            schedule.every().day.at('00:00').do(self._build_report)
            while True:
                schedule.run_pending()
                time.sleep(1)
        else:
            self._build_report(self.args.date)

    def _build_report(self, date: datetime = None):
        if date is None:
            date = datetime.now()
        user_metrics = AccountRepository(self.db).daily_report(date)

        email = EmailMessage(
            sender='reports@mycroft.ai',
            recipient=os.environ['REPORT_RECIPIENT'],
            subject='Mycroft Daily Report - {}'.format(date.strftime('%Y-%m-%d')),
            template_file_name='metrics.html',
            template_variables=dict(user_metrics=user_metrics)
        )

        mailer = SeleneMailer(email)
        mailer.send(True)


DailyReport().run()
