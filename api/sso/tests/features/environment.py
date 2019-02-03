from behave import fixture, use_fixture

from sso_api.api import sso


@fixture
def sso_client(context):
    sso.testing = True
    context.client = sso.test_client()

    yield context.client


def before_feature(context, _):
    use_fixture(sso_client, context)
