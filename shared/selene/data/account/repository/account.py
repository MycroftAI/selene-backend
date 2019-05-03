from logging import getLogger
from os import environ

from passlib.hash import sha512_crypt

from selene.util.db import use_transaction
from ..entity.account import Account, AccountAgreement, AccountMembership
from ..entity.agreement import OPEN_DATASET
from ...repository_base import RepositoryBase

_log = getLogger('selene.data.account')


def _encrypt_password(password):
    salt = environ['SALT']
    hash_result = sha512_crypt.using(salt=salt, rounds=5000).hash(password)
    hashed_password_index = hash_result.rindex('$') + 1

    return hash_result[hashed_password_index:]


class AccountRepository(RepositoryBase):
    def __init__(self, db):
        super(AccountRepository, self).__init__(db, __file__)
        self.db = db

    @use_transaction
    def add(self, account: Account, password: str) -> str:
        account_id = self._add_account(account, password)
        for agreement in account.agreements:
            self.add_agreement(account_id, agreement)

        _log.info('Added account {}'.format(account.email_address))

        return account_id

    def _add_account(self, account: Account, password: str):
        """Add a row to the account table."""
        if password is None:
            encrypted_password = None
        else:
            encrypted_password = _encrypt_password(password)
        request = self._build_db_request(
            sql_file_name='add_account.sql',
            args=dict(
                email_address=account.email_address,
                password=encrypted_password,
                username=account.username
            )
        )
        result = self.cursor.insert_returning(request)

        return result['id']

    def add_agreement(self, account_id: str, agreement: AccountAgreement):
        """Accounts cannot be added without agreeing to terms and privacy"""
        request = self._build_db_request(
            sql_file_name='add_account_agreement.sql',
            args=dict(
                account_id=account_id,
                agreement_name=agreement.type
            )
        )
        self.cursor.insert(request)

    def add_membership(self, acct_id: str, membership: AccountMembership):
        """A membership is optional, add it if one was selected"""
        request = self._build_db_request(
            sql_file_name='add_account_membership.sql',
            args=dict(
                account_id=acct_id,
                membership_type=membership.type,
                payment_method=membership.payment_method,
                payment_account_id=membership.payment_account_id,
                payment_id=membership.payment_id
            )
        )
        self.cursor.insert(request)

    def remove(self, account: Account):
        """Delete and account and all of its children"""
        request = self._build_db_request(
            sql_file_name='remove_account.sql',
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
        request = self._build_db_request(
            sql_file_name='get_account.sql',
            args=dict(account_id=account_id),
        )
        request.sql = request.sql.format(
            account_id_resolver=account_id_resolver
        )

        return self._get_account(request)

    def get_account_by_email(self, email_address: str) -> Account:
        account_id_resolver = (
            '(SELECT id FROM account.account '
            'WHERE email_address = %(email_address)s)'
        )
        request = self._build_db_request(
            sql_file_name='get_account.sql',
            args=dict(email_address=email_address),
        )
        request.sql = request.sql.format(
            account_id_resolver=account_id_resolver
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
        encrypted_password = _encrypt_password(password)
        request = self._build_db_request(
            sql_file_name='get_account.sql',
            args=dict(email_address=email, password=encrypted_password),
        )
        request.sql = request.sql.format(
            account_id_resolver=account_id_resolver
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
        """Return an account associated with the specified device."""
        request = self._build_db_request(
            sql_file_name='get_account_by_device_id.sql',
            args=dict(device_id=device_id)
        )
        return self._get_account(request)

    def change_password(self, account_id, password):
        encrypted_password = _encrypt_password(password)
        db_request = self._build_db_request(
            sql_file_name='change_password.sql',
            args=dict(account_id=account_id, password=encrypted_password)
        )
        self.cursor.update(db_request)

    def update_username(self, account_id: str, username: str):
        db_request = self._build_db_request(
            sql_file_name='update_username.sql',
            args=dict(account_id=account_id, username=username)
        )
        self.cursor.update(db_request)

    def expire_open_dataset_agreement(self, account_id: str):
        db_request = self._build_db_request(
            sql_file_name='expire_account_agreement.sql',
            args=dict(account_id=account_id, agreement_type=OPEN_DATASET)
        )
        self.cursor.delete(db_request)
