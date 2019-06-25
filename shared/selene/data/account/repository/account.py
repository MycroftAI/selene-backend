from datetime import datetime, timedelta
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

    def daily_report(self, date: datetime):
        base = date - timedelta(days=1)
        end_date = base.strftime('%Y-%m-%d')
        start_date_1_day = (base - timedelta(days=1)).strftime('%Y-%m-%d')
        start_date_15_days = (base - timedelta(days=15)).strftime('%Y-%m-%d')
        start_date_30_days = (base - timedelta(days=30)).strftime('%Y-%m-%d')
        db_request = self._build_db_request(
            sql_file_name='daily_report.sql',
            args=dict(start_date=start_date_1_day, end_date=end_date)
        )
        report_1_day = self.cursor.select_one(db_request)
        db_request = self._build_db_request(
            sql_file_name='daily_report.sql',
            args=dict(start_date=start_date_15_days, end_date=end_date)
        )
        report_15_days = self.cursor.select_one(db_request)
        db_request = self._build_db_request(
            sql_file_name='daily_report.sql',
            args=dict(start_date=start_date_30_days, end_date=end_date)
        )
        report_30_days = self.cursor.select_one(db_request)

        report_table = [{
            'type': 'User',
            'current': report_1_day.total,
            'oneDay': report_1_day.total - report_1_day.total_new,
            'oneDayDelta': report_1_day.total_new,
            'oneDayMinus': 0,
            'fifteenDays': report_15_days.total - report_15_days.total_new,
            'fifteenDaysDelta': report_15_days.total_new,
            'fifteenDaysMinus': 0,
            'thirtyDays': report_30_days.total - report_30_days.total_new,
            'thirtyDaysDelta': report_30_days.total_new,
            'thirtyDaysMinus': 0
        }, {
            'type': 'Free Account',
            'current': report_1_day.total - report_1_day.paid_total,
            'oneDay': report_1_day.total - report_1_day.paid_total - report_1_day.total_new + report_1_day.paid_new,
            'oneDayDelta': report_1_day.total_new - report_1_day.paid_new,
            'oneDayMinus': 0,
            'fifteenDays': report_15_days.total - report_15_days.paid_total - report_15_days.total_new +
                           report_15_days.paid_new,
            'fifteenDaysDelta': report_15_days.total_new - report_15_days.paid_new,
            'fifteenDaysMinus': 0,
            'thirtyDays': report_30_days.total - report_30_days.paid_total - report_30_days.total_new +
                          report_30_days.paid_new,
            'thirtyDaysDelta': report_30_days.total_new - report_30_days.paid_new,
            'thirtyDaysMinus': 0
        }, {
            'type': 'Monthly Account',
            'current': report_1_day.monthly_total,
            'oneDay': report_1_day.monthly_total - report_1_day.monthly_new + report_1_day.monthly_minus,
            'oneDayDelta': report_1_day.monthly_new,
            'oneDayMinus': report_1_day.monthly_minus,
            'fifteenDays': report_15_days.monthly_total - report_15_days.monthly_new +
                           report_15_days.monthly_minus,
            'fifteenDaysDelta': report_15_days.monthly_new,
            'fifteenDaysMinus': report_15_days.monthly_minus,
            'thirtyDays': report_30_days.monthly_total - report_30_days.monthly_new +
                          report_30_days.monthly_minus,
            'thirtyDaysDelta': report_30_days.monthly_new,
            'thirtyDaysMinus': report_30_days.monthly_minus
        }, {
            'type': 'Yearly Account',
            'current': report_1_day.yearly_total,
            'oneDay': report_1_day.yearly_total - report_1_day.yearly_new + report_1_day.yearly_minus,
            'oneDayDelta': report_1_day.yearly_new,
            'oneDayMinus': report_1_day.yearly_minus,
            'fifteenDays': report_15_days.yearly_total - report_15_days.yearly_new +
                           report_15_days.yearly_minus,
            'fifteenDaysDelta': report_15_days.yearly_new,
            'fifteenDaysMinus': report_15_days.yearly_minus,
            'thirtyDays': report_30_days.yearly_total - report_30_days.yearly_new +
                          report_30_days.yearly_minus,
            'thirtyDaysDelta': report_30_days.yearly_new,
            'thirtyDaysMinus': report_30_days.yearly_minus
        }, {
            'type': 'Paid Account',
            'current': report_1_day.paid_total,
            'oneDay': report_1_day.paid_total - report_1_day.paid_new + report_1_day.paid_minus,
            'oneDayDelta': report_1_day.paid_new,
            'oneDayMinus': report_1_day.paid_minus,
            'fifteenDays': report_15_days.paid_total - report_15_days.paid_new +
                           report_15_days.paid_minus,
            'fifteenDaysDelta': report_15_days.paid_new,
            'fifteenDaysMinus': report_15_days.paid_minus,
            'thirtyDays': report_30_days.paid_total - report_30_days.paid_new +
                          report_30_days.paid_minus,
            'thirtyDaysDelta': report_30_days.paid_new,
            'thirtyDaysMinus': report_30_days.paid_minus
        }]
        return report_table

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

    def end_membership(self, membership: AccountMembership):
        db_request = self._build_db_request(
            sql_file_name='end_membership.sql',
            args=dict(
                id=membership.id,
                membership_ts_range='[{start},{end}]'.format(
                    start=membership.start_date,
                    end=membership.end_date
                )
            )
        )
        self.cursor.update(db_request)

    def end_active_membership(self, customer_id):
        db_request = self._build_db_request(
            sql_file_name='get_active_membership_by_payment_account_id.sql',
            args=dict(payment_account_id=customer_id)
        )
        db_result = self.cursor.select_one(db_request)
        if db_result is not None:
            account_membership = AccountMembership(**db_result)
            account_membership.end_date = datetime.utcnow()
            self.end_membership(account_membership)

    def get_active_account_membership(self, account_id) -> AccountMembership:
        account_membership = None
        db_request = self._build_db_request(
            sql_file_name='get_active_membership_by_account_id.sql',
            args=dict(account_id=account_id)
        )
        db_result = self.cursor.select_one(db_request)
        if db_result:
            account_membership = AccountMembership(**db_result)

        return account_membership
