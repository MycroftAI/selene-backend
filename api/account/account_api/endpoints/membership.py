from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.account import MembershipRepository
from selene.util.db import get_db_connection


class MembershipEndpoint(SeleneEndpoint):
    def get(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            membership_repository = MembershipRepository(db)
            membership_types = membership_repository.get_membership_types()

        for membership_type in membership_types:
            membership_type.rate = float(membership_type.rate)
        return membership_types, HTTPStatus.OK
