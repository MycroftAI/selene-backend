from datetime import date
from selene.data.account import (
    Account,
    AccountAgreement,
    AccountMembership,
    AccountRepository,
    PRIVACY_POLICY,
    TERMS_OF_USE
)


def build_test_membership(**overrides):
    return AccountMembership(
        type=overrides.get('type') or 'Monthly Membership',
        start_date=overrides.get('start_date') or date.today(),
        payment_method=overrides.get('payment_method') or 'Stripe',
        payment_account_id=overrides.get('payment_account_id') or 'foo',
        payment_id=overrides.get('payment_id') or 'bar'
    )


def build_test_account(**overrides):
    test_agreements = [
        AccountAgreement(type=PRIVACY_POLICY, accept_date=date.today()),
        AccountAgreement(type=TERMS_OF_USE, accept_date=date.today())
    ]
    if 'membership' in overrides:
        membership_overrides = overrides['membership']
        if membership_overrides is None:
            # if the membership override is set to None, the assumed intent
            # is to add an account that does not have a membership
            test_membership = None
        else:
            test_membership = build_test_membership(**membership_overrides)
    else:
        test_membership = build_test_membership()

    return Account(
        email_address=overrides.get('email_address') or 'foo@mycroft.ai',
        username=overrides.get('username') or 'foobar',
        membership=test_membership,
        agreements=overrides.get('agreements') or test_agreements
    )


def add_account(db, **overrides):
    acct_repository = AccountRepository(db)
    account = build_test_account(**overrides)
    account.id = acct_repository.add(account, 'foo')
    acct_repository.add_membership(account.id, account.membership)

    return account


def remove_account(db, account):
    account_repository = AccountRepository(db)
    account_repository.remove(account)
