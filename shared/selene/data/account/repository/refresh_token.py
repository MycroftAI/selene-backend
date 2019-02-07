from os import path

from selene.util.db import DatabaseRequest, Cursor, get_sql_from_file
from ..entity.account import Account

SQL_DIR = path.join(path.dirname(__file__), 'sql')


class RefreshTokenRepository(object):
    def __init__(self, db, account: Account):
        self.db = db
        self.account = account

    def add_refresh_token(self, token: str):
        """Add a refresh token to an account"""
        sql = get_sql_from_file(path.join(SQL_DIR, 'add_refresh_token.sql'))
        request = DatabaseRequest(
            sql=sql,
            args=dict(account_id=self.account.id, refresh_token=token),
        )
        cursor = Cursor(self.db)
        cursor.insert(request)

    def delete_refresh_token(self, token: str):
        """When a refresh token expires, delete it."""
        sql = get_sql_from_file(path.join(SQL_DIR, 'delete_refresh_token.sql'))
        request = DatabaseRequest(
            sql=sql,
            args=dict(account_id=self.account.id, refresh_token=token),
        )
        cursor = Cursor(self.db)
        cursor.delete(request)

    def update_refresh_token(self, old: str, new: str):
        """When a new refresh token is generated replace the old one"""
        sql = get_sql_from_file(path.join(SQL_DIR, 'update_refresh_token.sql'))
        request = DatabaseRequest(
            sql=sql,
            args=dict(
                account_id=self.account.id,
                new_refresh_token=new,
                old_refresh_token=old
            ),
        )
        cursor = Cursor(self.db)
        cursor.update(request)
