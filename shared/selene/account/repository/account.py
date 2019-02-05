from passlib.hash import sha512_crypt
from os import environ, path

from selene.util.db import DatabaseRequest, Cursor
from ..entity.account import Account

SQL_DIR = path.join(path.dirname(__file__), 'sql')


def _encrypt_password(password):
    salt = environ['SALT']
    hash_result = sha512_crypt.using(salt=salt, rounds=5000).hash(password)
    hashed_password_index = hash_result.rindex('$') + 1

    return hash_result[hashed_password_index:]


class AccountRepository(object):
    def __init__(self, db):
        self.db = db

    def add(self, email_address: str, password: str):
        encrypted_password = _encrypt_password(password)
        request = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'add_account.sql'),
            args=dict(email_address=email_address, password=encrypted_password)
        )
        cursor = Cursor(self.db)
        result = cursor.insert_returning(request)

        return Account(
            id=result['id'],
            email_address=email_address,
            password=encrypted_password,
            refresh_tokens=[]
        )

    def remove(self, account: Account):
        request = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'remove_account.sql'),
            args=dict(id=account.id)
        )
        cursor = Cursor(self.db)
        cursor.delete(request)

    def get_account_by_id(self, account_id: str) -> Account:
        """Use a given uuid to query the database for an account

        :param account_id: uuid
        :return: an account entity, if one is found
        """
        request = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'get_account_by_id.sql'),
            args=dict(account_id=account_id),
        )
        cursor = Cursor(self.db)
        sql_results = cursor.select_one(request)

        if sql_results is not None:
            return Account(**sql_results)

    def get_account_from_credentials(
            self, email: str, password: str
    ) -> Account:
        """
        Validate email/password combination against the database

        :param email: the user provided email address
        :param password: the user provided password
        :return: the matching account record, if one is found
        """
        encrypted_password = _encrypt_password(password)
        query = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'get_account_from_credentials.sql'),
            args=dict(email_address=email, password=encrypted_password),
        )
        cursor = Cursor(self.db)
        sql_results = cursor.select_one(query)

        if sql_results is not None:
            return Account(**sql_results)

    def get_account_by_email(self, email_address):
        account = None
        request = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'get_account_by_email.sql'),
            args=dict(email_address=email_address),
        )
        cursor = Cursor(self.db)
        db_response = cursor.select_one(request)

        if db_response is not None:
            account = Account(**db_response)

        return account
