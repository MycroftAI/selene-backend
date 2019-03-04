from datetime import date

from selene.data.account import (
    Account,
    AccountAgreement,
    AccountMembership,
    AccountRepository,
)

_agree_to_terms = AccountAgreement(
    type='Terms of Use',
    accept_date=date(1975, 3, 14)
)

_agree_to_privacy = AccountAgreement(
    type='Privacy Policy',
    accept_date=date.today()
)

_membership = AccountMembership(
    type='Monthly Supporter',
    start_date=date.today(),
    stripe_customer_id='killer_rabbit'
)

arthur = dict(
    email_address='arthur@holy.grail',
    username='kingofthebritons',
    agreements=[_agree_to_terms, _agree_to_privacy],
    membership=_membership
)

black_knight = dict(
    email_address='blackknight@holy.grail',
    username='fleshwound',
    agreements=[_agree_to_terms, _agree_to_privacy]
)


def insert_account(db, account_attrs: dict) -> Account:
    account = Account(**account_attrs)
    account_repository = AccountRepository(db)
    account.id = account_repository.add(account, password='holygrail')

    return account


def delete_account(db, account: Account):
    account_repository = AccountRepository(db)
    account_repository.remove(account)
