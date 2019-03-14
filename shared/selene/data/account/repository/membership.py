from selene.data.account import AccountMembership
from ..entity.membership import Membership
from ...repository_base import RepositoryBase


class MembershipRepository(RepositoryBase):
    def __init__(self, db):
        super(MembershipRepository, self).__init__(db, __file__)

    def get_membership_types(self):
        db_request = self._build_db_request(
            sql_file_name='get_membership_types.sql'
        )
        db_result = self.cursor.select_all(db_request)

        return [Membership(**row) for row in db_result]

    def get_membership_by_type(self, type: str):
        db_request = self._build_db_request(
            sql_file_name='get_membership_by_type.sql',
            args=dict(type=type)
        )
        db_result = self.cursor.select_one(db_request)
        return Membership(**db_result)

    def get_active_membership_by_account_id(self, account_id) -> AccountMembership:
        db_request = self._build_db_request(
            sql_file_name='get_active_membership_by_account_id.sql',
            args=dict(account_id=account_id)
        )
        db_result = self.cursor.select_one(db_request)
        if db_result:
            return AccountMembership(**db_result)

    def add(self, membership: Membership):
        db_request = self._build_db_request(
            'add_membership.sql',
            args=dict(
                membership_type=membership.type,
                rate=membership.rate,
                rate_period=membership.rate_period
            )
        )
        result = self.cursor.insert_returning(db_request)

        return result['id']

    def remove(self, membership: Membership):
        db_request = self._build_db_request(
            sql_file_name='delete_membership.sql',
            args=dict(membership_id=membership.id)
        )
        self.cursor.delete(db_request)

    def finish_membership(self, membership: AccountMembership):
        db_request = self._build_db_request(
            sql_file_name='finish_membership.sql',
            args=dict(
                id=membership.id,
                membership_ts_range='[{start},{end}]'.format(
                    start=membership.start_date,
                    end=membership.end_date
                )
            )
        )
        self.cursor.update(db_request)
