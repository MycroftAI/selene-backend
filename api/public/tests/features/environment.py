from behave import fixture, use_fixture

from public_api.api import public
from selene.api import generate_device_login
from selene.api.etag import ETagManager
from selene.testing.account import add_account, remove_account
from selene.testing.agreement import add_agreements, remove_agreements
from selene.testing.account_geography import add_account_geography
from selene.testing.account_preference import add_account_preference
from selene.testing.device import add_device
from selene.testing.device_skill import (
    add_skill_to_manifest,
    remove_manifest_skill
)
from selene.testing.skill import add_skill, remove_skill
from selene.testing.text_to_speech import (
    add_text_to_speech,
    remove_text_to_speech
)
from selene.testing.wake_word import add_wake_word, remove_wake_word
from selene.util.cache import SeleneCache
from selene.util.db import connect_to_db


@fixture
def public_api_client(context):
    public.testing = True
    context.client_config = public.config
    context.client = public.test_client()
    yield context.client


def before_all(context):
    use_fixture(public_api_client, context)
    context.cache = SeleneCache()
    context.db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    agreements = add_agreements(context.db)
    context.terms_of_use = agreements[0]
    context.privacy_policy = agreements[1]
    context.open_dataset = agreements[2]


def after_all(context):
    remove_agreements(
        context.db,
        [context.privacy_policy, context.terms_of_use, context.open_dataset]
    )


def before_scenario(context, _):
    context.etag_manager = ETagManager(context.cache, context.client_config)
    try:
        context.account = add_account(context.db)
        add_account_preference(context.db, context.account.id)
        context.geography_id = add_account_geography(
            context.db,
            context.account
        )
        context.wake_word = add_wake_word(context.db)
        context.voice = add_text_to_speech(context.db)
        _add_device(context)
        context.skill = add_skill(
            context.db,
            skill_global_id='selene-test-skill|19.02'
        )
        context.manifest_skill = add_skill_to_manifest(
            context.db,
            context.device_id,
            context.skill
        )
    except:
        import traceback
        print(traceback.print_exc())


def after_scenario(context, _):
    remove_account(context.db, context.account)
    remove_wake_word(context.db, context.wake_word)
    remove_text_to_speech(context.db, context.voice)
    remove_skill(context.db, skill_global_id=context.skill.skill_gid)


def _add_device(context):
    device_id = add_device(context.db, context.account.id, context.geography_id)
    context.device_id = device_id
    context.device_name = 'Selene Test Device'
    context.device_login = generate_device_login(device_id, context.cache)
    context.access_token = context.device_login['accessToken']


def before_tag(context, tag):
    if tag == 'device_specific_skill':
        _add_device_specific_skil(context)


def _add_device_specific_skil(context):
    context.device_specific_skill = add_skill(
        context.db,
        skill_global_id='@{device_id}|device-specific-skill|19.02'.format(
            device_id=context.device_id
        )
    )
    context.device_specific_manifest = add_skill_to_manifest(
        context.db,
        context.device_id,
        context.skill
    )


def after_tag(context, tag):
    if tag == 'new_skill':
        remove_manifest_skill(context.db, context.new_manifest_skill)
        remove_skill(context.db, context.new_skill.skill_gid)
