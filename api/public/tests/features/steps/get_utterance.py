import json
from http import HTTPStatus
from io import BytesIO
from os import path

from behave import When, Then
from hamcrest import assert_that, equal_to


@When('A flac audio with the utterance "tell me a joke" is passed')
def call_google_stt_endpoint(context):
    with open(path.join(path.dirname(__file__), 'resources/test_stt.flac'), 'rb') as flac:
        audio = BytesIO(flac.read())
        context.response = context.client.post('/stt?lang=en-US&limit=1', data=audio)


@Then('return the utterance "tell me a joke"')
def validate_response(context):
    assert_that(context.response.status_code, equal_to(HTTPStatus.OK))
    response_data = json.loads(context.response.data)
    expected_response = ['tell me a joke']
    assert_that(response_data, equal_to(expected_response))
