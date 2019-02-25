from psycopg2 import connect

connection_config = dict(
    host='127.0.0.1',
    dbname='postgres',
    user='mycroft',
    password='holmes'
)


def create_test_db():
    db = connect(**connection_config)
    db.autocommit = True
    cursor = db.cursor()
    cursor.execute(
        'CREATE DATABASE '
        '   mycroft_test '
        'WITH TEMPLATE '
        '    mycroft_template '
        'OWNER '
        '    mycroft;'
    )


def drop_test_db():
    db = connect(**connection_config)
    db.autocommit = True
    cursor = db.cursor()
    cursor.execute(
        'SELECT pg_terminate_backend(pid) '
        'FROM pg_stat_activity '
        'WHERE datname = \'mycroft_test\';'
    )
    cursor.execute('DROP DATABASE mycroft_test')
