from behave import fixture, use_fixture

from public_api.api import public


@fixture
def public_api_client(context):
    public.testing = True
    context.client_config = public.config
    context.client = public.test_client()
    yield context.client


def before_feature(context, _):
    use_fixture(public_api_client, context)
