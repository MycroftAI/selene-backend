import json
from http import HTTPStatus

from behave import given, when, then
from hamcrest import assert_that, equal_to

skill_manifest = {
    'skills': [
        {
            'name': 'skill-name-1',
            'origin': 'voice',
            'installation': 'installed',
            'failure_message': '',
            'status': 'active',
            'installed': 1553610007,
            'updated': 1553610007
        }
    ]
}

skill = {
    'name': 'skill-name-1',
    'identifier': 'skill-name-13-123',
    'skillMetadata': {
        'sections': [
            {
                'name': 'section1',
                'fields': [
                    {
                        'label': 'test'
                    }
                ]
            }
        ]
    }
}


@given('a device with a skill')
def device_skill(context):
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.client.put(
        '/v1/device/{uuid}/skill'.format(uuid=device_id),
        data=json.dumps(skill),
        content_type='application_json',
        headers=headers
    )


@when('a skill manifest is uploaded')
def device_skill_manifest(context):
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.upload_skill_manifest_response = context.client.put(
        '/v1/device/{uuid}/skillJson'.format(uuid=device_id),
        data=json.dumps(skill_manifest),
        content_type='application_json',
        headers=headers
    )


@then('the skill manifest endpoint should return 200 status code')
def validate_skill_manifest_upload(context):
    response = context.upload_skill_manifest_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
