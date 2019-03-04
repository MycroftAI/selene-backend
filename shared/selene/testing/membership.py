from decimal import Decimal

from selene.data.account import Membership, MembershipRepository

monthly_membership = dict(
    type='Monthly Supporter',
    rate=Decimal('1.99'),
    rate_period='monthly'
)

yearly_membership = dict(
    type='Yearly Supporter',
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
