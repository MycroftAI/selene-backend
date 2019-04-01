import json
from http import HTTPStatus

from behave import given, when, then
from hamcrest import assert_that, equal_to

skill_manifest = {
    'skills': [
        {
            'skill_gid': 'wolfram-alpha|19.02',
            'origin': 'voice',
            'installation': 'installed',
            'failure_message': '',
            'status': 'active',
            'installed': 1553610007.0,
            'updated': 1553610007.0
        }
    ]
}

skill = {
    'skill_gid': 'wolfram-alpha|19.02',
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


@then('the skill manifest should be added')
def get_skill_manifest(context):
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    response = context.client.get(
        '/v1/device/{uuid}/skillJson'.format(uuid=device_id),
        headers=headers
    )
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    skill_manifest_from_db = json.loads(response.data)
    skill = skill_manifest_from_db['skills'][0]
    expected_skill = skill_manifest['skills'][0]
    assert_that(skill['skill_gid'], equal_to(expected_skill['skill_gid']))
    assert_that(skill['origin'], equal_to(expected_skill['origin']))
    assert_that(skill['installation'], equal_to(expected_skill['installation']))
    assert_that(skill['failure_message'], equal_to(expected_skill['failure_message']))
    assert_that(skill['installed'], equal_to(expected_skill['installed']))
    assert_that(skill['updated'], equal_to(expected_skill['updated']))
