from dataclasses import asdict
import json

from behave import then, when
from hamcrest import assert_that, equal_to

from selene.data.account import PRIVACY_POLICY, TERMS_OF_USE


@when('API request for {agreement} is made')
def call_agreement_endpoint(context, agreement):
    if agreement == PRIVACY_POLICY:
        url = '/api/agreement/privacy-policy'
    elif agreement == TERMS_OF_USE:
        url = '/api/agreement/terms-of-use'
    else:
        raise ValueError('invalid agreement type')

    context.response = context.client.get(url)


@then('{agreement} version {version} is returned')
def validate_response(context, agreement, version):
    response_data = json.loads(context.response.data)
    if agreement == PRIVACY_POLICY:
        expected_response = asdict(context.privacy_policy)
    elif agreement == TERMS_OF_USE:
        expected_response = asdict(context.terms_of_use)
    else:
        raise ValueError('invalid agreement type')

    del(expected_response['effective_date'])
    assert_that(response_data, equal_to(expected_response))
