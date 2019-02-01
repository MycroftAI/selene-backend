from os import path

from selene.util.db import DatabaseRequest, Cursor
from ..entity.account import Account

SQL_DIR = path.join(path.dirname(__file__), 'sql')


class AuthenticationRepository(object):
    def __init__(self, db):
        self.db = db

    def get_account_from_credentials(
            self, email: str, password: str
    ) -> Account:
        """
        Validate email/password combination against the database

        :param email: the user provided email address
        :param password: the user provided password
        :return: the matching account record, if one is found
        """
        query = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'get_account_from_credentials.sql'),
            args=dict(email_address=email, password=password),
        )
        cursor = Cursor(self.db)
        sql_results = cursor.select_one(query)

        if sql_results is not None:
            return Account(**sql_results)
