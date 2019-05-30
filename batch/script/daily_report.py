from os import environ

from selene.util.db import DatabaseConnectionConfig

mycroft_db = DatabaseConnectionConfig(
    host=environ['DB_HOST'],
    db_name=environ['DB_NAME'],
    user=environ['DB_USER'],
    password=environ['DB_PASSWORD'],
    port=environ['DB_PORT'],
    sslmode=environ['DB_SSL_MODE']
)