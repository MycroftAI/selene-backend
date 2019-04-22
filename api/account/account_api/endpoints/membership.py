from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.account import MembershipRepository


class MembershipEndpoint(SeleneEndpoint):
    def get(self):
        membership_repository = MembershipRepository(self.db)
        membership_types = membership_repository.get_membership_types()
        for membership_type in membership_types:
            membership_type.rate = float(membership_type.rate)

        return membership_types, HTTPStatus.OK
