from logging import getLogger
from os import environ, path
from typing import List

from passlib.hash import sha512_crypt

from selene.util.db import (
    DatabaseRequest,
    Cursor,
    get_sql_from_file,
    use_transaction
)
from ..entity.account import Account, AccountAgreement, AccountMembership

SQL_DIR = path.join(path.dirname(__file__), 'sql')

_log = getLogger('selene.data.account')


def _encrypt_password(password):
    salt = environ['SALT']
    hash_result = sha512_crypt.using(salt=salt, rounds=5000).hash(password)
    hashed_password_index = hash_result.rindex('$') + 1

    return hash_result[hashed_password_index:]


class AccountRepository(object):
    def __init__(self, db):
        self.db = db
        self.cursor = Cursor(db)

    @use_transaction
    def add(self, account: Account, password: str) -> str:
        account_id = self._add_account(account, password)
        self._add_agreements(account_id, account.agreements)
        if account.membership is not None:
            self._add_membership(account_id, account.membership)

        _log.info('Added account {}'.format(account.email_address))

        return account_id

    def _add_account(self, account: Account, password: str):
        """Add a row to the account table."""
        encrypted_password = _encrypt_password(password)
        request = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'add_account.sql')),
            args=dict(
                email_address=account.email_address,
                password=encrypted_password,
                username=account.username
            )
        )
        result = self.cursor.insert_returning(request)

        return result['id']

    def _add_agreements(self, acct_id: str, agreements: List[AccountAgreement]):
        """Accounts cannot be added without agreeing to terms and privacy"""
        for agreement in agreements:
            request = DatabaseRequest(
                sql=get_sql_from_file(
                    path.join(SQL_DIR, 'add_account_agreement.sql')
                ),
                args=dict(
                    account_id=acct_id,
                    agreement_name=agreement.type
                )
            )
            self.cursor.insert(request)

    def _add_membership(self, acct_id: str, membership: AccountMembership):
        """A membership is optional, add it if one was selected"""
        request = DatabaseRequest(
            sql=get_sql_from_file(
                path.join(SQL_DIR, 'add_account_membership.sql')
            ),
            args=dict(
                account_id=acct_id,
                membership_type=membership.type,
                payment_method=membership.payment_method,
                payment_account_id=membership.payment_account_id
            )
        )
        self.cursor.insert(request)

    def remove(self, account: Account):
        """Delete and account and all of its children"""
        request = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'remove_account.sql')),
            args=dict(id=account.id)
        )
        self.cursor.delete(request)

        log_msg = 'Deleted account {} and all it\'s related data'
        _log.info(log_msg.format(account.email_address))

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
        result = self.cursor.select_one(db_request)

        if result is not None:
            account_agreements = []
            if result['account']['agreements'] is not None:
                for agreement in result['account']['agreements']:
                    account_agreements.append(AccountAgreement(**agreement))
            result['account']['agreements'] = account_agreements
            if result['account']['membership'] is not None:
                result['account']['membership'] = AccountMembership(
                    **result['account']['membership']
                )
            account = Account(**result['account'])

        return account

    def get_account_by_device_id(self, device_id) -> Account:
        """Return an account using the id of the device associated to the account"""
        request = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'get_account_by_device_id.sql')),
            args=dict(device_id=device_id)
        )
        return self._get_account(request)
