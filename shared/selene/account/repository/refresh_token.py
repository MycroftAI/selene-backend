from os import path

from selene.util.db import DatabaseRequest, Cursor
from ..entity.account import Account

SQL_DIR = path.join(path.dirname(__file__), 'sql')


class RefreshTokenRepository(object):
    def __init__(self, db, account: Account):
        self.db = db
        self.account = account

    def add_refresh_token(self, token: str):
        """Add a refresh token to an account"""
        request = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'add_refresh_token.sql'),
            args=dict(account_id=self.account.id, refresh_token=token),
        )
        cursor = Cursor(self.db)
        cursor.insert(request)

    def delete_refresh_token(self, token: str):
        """When a refresh token expires, delete it."""
        request = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'delete_refresh_token.sql'),
            args=dict(account_id=self.account.id, refresh_token=token),
        )
        cursor = Cursor(self.db)
        cursor.delete(request)

    def update_refresh_token(self, old: str, new: str):
        """When a new refresh token is generated replace the old one"""
        request = DatabaseRequest(
            file_path=path.join(SQL_DIR, 'update_refresh_token.sql'),
            args=dict(
                account_id=self.account.id,
                new_refresh_token=new,
                old_refresh_token=old
            ),
        )
        cursor = Cursor(self.db)
        cursor.update(request)
