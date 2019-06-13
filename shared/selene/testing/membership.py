from decimal import Decimal

from selene.data.account import (
    Membership,
    MembershipRepository,
    MONTHLY_MEMBERSHIP,
    YEARLY_MEMBERSHIP
)

monthly_membership = dict(
    type=MONTHLY_MEMBERSHIP,
    rate=Decimal('1.99'),
    rate_period='monthly'
)

yearly_membership = dict(
    type=YEARLY_MEMBERSHIP,
    rate=Decimal('19.99'),
    rate_period='yearly'
)


def insert_memberships(db):
    monthly = Membership(**monthly_membership)
    yearly = Membership(**yearly_membership)
    membership_repository = MembershipRepository(db)
    monthly.id = membership_repository.add(monthly)
    yearly.id = membership_repository.add(yearly)

    return monthly, yearly


def delete_memberships(db, memberships):
    membership_repository = MembershipRepository(db)
    for membership in memberships:
        membership_repository.remove(membership)
