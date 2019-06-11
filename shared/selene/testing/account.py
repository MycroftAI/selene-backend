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
    return Account(
        email_address=overrides.get('email_address') or 'foo@mycroft.ai',
        username=overrides.get('username') or 'foobar',
        membership=build_test_membership(**overrides),
        agreements=overrides.get('agreements') or test_agreements
    )


def add_account(db, **overrides):
    acct_repository = AccountRepository(db)
    account = build_test_account(**overrides)
    account.id = acct_repository.add(account, 'foo')

    return account


def remove_account(db, account):
    account_repository = AccountRepository(db)
    account_repository.remove(account)
