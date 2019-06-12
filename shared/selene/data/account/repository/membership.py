from selene.data.account import AccountMembership
from ..entity.membership import Membership
from ...repository_base import RepositoryBase

MONTHLY_MEMBERSHIP = 'Monthly Membership'
YEARLY_MEMBERSHIP = 'Yearly Membership'


class MembershipRepository(RepositoryBase):
    def __init__(self, db):
        super(MembershipRepository, self).__init__(db, __file__)

    def get_membership_types(self):
        db_request = self._build_db_request(
            sql_file_name='get_membership_types.sql'
        )
        db_result = self.cursor.select_all(db_request)

        return [Membership(**row) for row in db_result]

    def get_membership_by_type(self, membership_type: str):
        db_request = self._build_db_request(
            sql_file_name='get_membership_by_type.sql',
            args=dict(type=membership_type)
        )
        db_result = self.cursor.select_one(db_request)
        return Membership(**db_result)

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
