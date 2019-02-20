import uuid
from datetime import date, timedelta

from behave import fixture, use_fixture

from public_api.api import public
from selene.data.account import Account, AccountRepository, AccountAgreement, PRIVACY_POLICY, TERMS_OF_USE, Agreement, \
    AgreementRepository
from selene.data.device import DeviceRepository
from selene.data.device.entity.text_to_speech import TextToSpeech
from selene.data.device.entity.wake_word import WakeWord
from selene.util.db import get_db_connection

account = Account(
    email_address='test@test.com',
    display_name='test',
    agreements=[
                AccountAgreement(type=PRIVACY_POLICY, accept_date=date.today()),
                AccountAgreement(type=TERMS_OF_USE, accept_date=date.today())
            ],
    subscription=None
)

wake_word = WakeWord(
    id=str(uuid.uuid4()),
    wake_word='hey mycroft',
    engine='precise'
)

text_to_speech = TextToSpeech(
    id=str(uuid.uuid4()),
    setting_name='test',
    display_name='test',
    engine='mimic'
)


@fixture
def public_api_client(context):
    public.testing = True
    context.client_config = public.config
    context.client = public.test_client()
    yield context.client


def before_feature(context, _):
    use_fixture(public_api_client, context)


def before_scenario(context, _):
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        _add_agreements(context, db)
        _add_account(context, db)


def after_scenario(context, _):
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        _remove_account(context, db)
        _remove_agreements(context, db)


def _add_agreements(context, db):
    context.privacy_policy = Agreement(
        type=PRIVACY_POLICY,
        version='999',
        content='this is Privacy Policy version 999',
        effective_date=date.today() - timedelta(days=5)
    )
    context.terms_of_use = Agreement(
        type=TERMS_OF_USE,
        version='999',
        content='this is Terms of Use version 999',
        effective_date=date.today() - timedelta(days=5)
    )
    agreement_repository = AgreementRepository(db)
    context.privacy_policy.id = agreement_repository.add(context.privacy_policy)
    context.terms_of_use.id = agreement_repository.add(context.terms_of_use)


def _add_account(context, db):
    context.account = account
    account_id = AccountRepository(db).add(account, password='test1234')
    context.account.id = account_id
    device_repository = DeviceRepository(db)
    context.wake_word_id = device_repository.add_wake_word(context.account.id, wake_word)
    context.text_to_speech_id = device_repository.add_text_to_speech(text_to_speech)


def _remove_account(context, db):
    AccountRepository(db).remove(context.account)
    device_repository = DeviceRepository(db)
    device_repository.remove_wake_word(context.wake_word_id)
    device_repository.remove_text_to_speech(context.text_to_speech_id)


def _remove_agreements(context, db):
    agreements_repository = AgreementRepository(db)
    agreements_repository.remove(context.privacy_policy, testing=True)
    agreements_repository.remove(context.terms_of_use, testing=True)