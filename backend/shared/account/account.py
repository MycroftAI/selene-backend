from dataclasses import dataclass
from os import path

from selene_util.db import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


@dataclass
class Account(object):
    """Representation of a Mycroft user account."""
    id: str
    email_address: str
    date_format: str
    time_format: str
    measurement_system: str
    wake_word: str
    text_to_speech_id: str
    first_name: str = None
    last_name: str = None
    password: str = None
    picture: str = None


def get_account_by_id(db, account_id: str) -> Account:
    """Use a given uuid to query the database for an account

    :param db: psycopg2 connection object to mycroft database
    :param account_id: uuid
    :return:
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_account_by_id.sql'),
        args=dict(account_id=account_id),
        singleton=True
    )
    sql_results = fetch(db, query)

    return Account(**sql_results)
