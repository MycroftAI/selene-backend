from os import path

from selene.util.db import DatabaseRequest, Cursor
from ..entity.account import Account

SQL_DIR = path.join(path.dirname(__file__), 'sql')


class AccountRepository(object):
    def __init__(self, db):
        self.db = db

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

    def delete_refresh_token(self, account: Account, token: str):
        """When a new refresh token is generated update the account table"""
        request = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'delete_refresh_token.sql'),
            args=dict(account_id=account.id, refresh_token=token),
        )
        cursor = Cursor(self.db)
        cursor.update(request)

    def update_refresh_token(self, account: Account, old: str, new: str):
        """When a new refresh token is generated update the account table"""
        request = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'update_refresh_token.sql'),
            args=dict(
                account_id=account.id,
                new_refresh_token=new,
                old_refresh_token=old
            ),
        )
        cursor = Cursor(self.db)
        cursor.update(request)
