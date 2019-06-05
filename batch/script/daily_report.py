import os
from datetime import datetime
from os import environ

import schedule
import time

from selene.data.account import AccountRepository
from selene.util.db import DatabaseConnectionConfig, connect_to_db
from selene.util.email import EmailMessage, SeleneMailer

mycroft_db = DatabaseConnectionConfig(
    host=environ['DB_HOST'],
    db_name=environ['DB_NAME'],
    user=environ['DB_USER'],
    password=environ['DB_PASSWORD'],
    port=environ['DB_PORT'],
    sslmode=environ['DB_SSL_MODE']
)


def build_report():
    with connect_to_db(mycroft_db) as db:
        user_metrics = AccountRepository(db).daily_report(datetime.now())

    email = EmailMessage(
        sender='reports@mycroft.ai',
        recipient=os.environ['REPORT_RECIPIENT'],
        subject='Mycroft Daily Report',
        template_file_name='metrics.html',
        template_variables=dict(user_metrics=user_metrics)
    )

    mailer = SeleneMailer(email)
    mailer.send(True)


schedule.every().day.at('00:00').do(build_report)

while True:
    schedule.run_pending()
    time.sleep(1)
