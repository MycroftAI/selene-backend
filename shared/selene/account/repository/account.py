from os import path

from selene.util.db import DatabaseQuery, fetch
from ..entity.account import Account

SQL_DIR = path.join(path.dirname(__file__), 'sql')


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
