from passlib.hash import sha512_crypt
from os import environ, path

from selene.util.db import DatabaseRequest, Cursor, get_sql_from_file
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

    def add(self, email_address: str, password: str) -> str:
        encrypted_password = _encrypt_password(password)
        request = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'add_account.sql')),
            args=dict(email_address=email_address, password=encrypted_password)
        )
        cursor = Cursor(self.db)
        result = cursor.insert_returning(request)

        return result['id']

    def remove(self, account: Account):
        request = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'remove_account.sql')),
            args=dict(id=account.id)
        )
        cursor = Cursor(self.db)
        cursor.delete(request)

    def get_account_by_id(self, account_id: str) -> Account:
        """Use a given uuid to query the database for an account

        :param account_id: uuid
        :return: an account entity, if one is found
        """
        account_id_resolver = '%(account_id)s'
        sql = get_sql_from_file(path.join(SQL_DIR, 'get_account.sql')).format(
            account_id_resolver=account_id_resolver,
        )
        request = DatabaseRequest(sql=sql, args=dict(account_id=account_id))

        return self._get_account(request)

    def get_account_by_email(self, email_address: str) -> Account:
        account_id_resolver = (
            '(SELECT id FROM account.account '
            'WHERE email_address = %(email_address)s)'
        )
        sql = get_sql_from_file(path.join(SQL_DIR, 'get_account.sql')).format(
            account_id_resolver=account_id_resolver,
        )
        request = DatabaseRequest(
            sql=sql,
            args=dict(email_address=email_address),
        )

        return self._get_account(request)

    def get_account_from_credentials(
            self, email: str, password: str
    ) -> Account:
        """
        Validate email/password combination against the database

        :param email: the user provided email address
        :param password: the user provided password
        :return: the matching account record, if one is found
        """
        account_id_resolver = (
            '(SELECT id FROM account.account '
            'WHERE email_address = %(email_address)s and password=%(password)s)'
        )
        sql = get_sql_from_file(
            path.join(SQL_DIR, 'get_account.sql')
        )
        encrypted_password = _encrypt_password(password)
        request = DatabaseRequest(
            sql=sql.format(account_id_resolver=account_id_resolver),
            args=dict(email_address=email, password=encrypted_password),
        )

        return self._get_account(request)

    def _get_account(self, db_request):
        account = None
        cursor = Cursor(self.db)
        result = cursor.select_one(db_request)

        if result is not None:
            account = Account(**result['account'])

        return account
