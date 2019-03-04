from ..entity.membership import Membership
from ...repository_base import RepositoryBase


class MembershipRepository(RepositoryBase):
    def __init__(self, db):
        super(MembershipRepository, self).__init__(db, __file__)

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
            'delete_membership.sql',
            args=dict(membership_id=membership.id)
        )
        self.cursor.delete(db_request)
