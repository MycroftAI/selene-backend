import json
from http import HTTPStatus

from behave import when, then, given
from hamcrest import assert_that, equal_to

from selene.data.skill import SkillSettingRepository
from selene.util.db import get_db_connection

skill = {
    "name": "Test",
    'identifier': 'Test-123%',
    "skillMetadata": {
        "sections": [
            {
                "name": "Test-456",
                "fields": [
                    {
                        "type": "label",
                        "label": "label-test"
                    },
                    {
                        "name": "user",
                        "type": "text",
                        "label": "Username",
                        "value": "name test",
                        "placeholder": "this is a test"
                    },
                    {
                        "name": "password",
                        "type": "password",
                        "label": "Password",
                        "value": "123"
                    }
                ]
            }
        ]
    }
}

new_settings = {
    'user': 'this name is a test',
    'password': 'this is a new password'
}

skill_updated = {
    "name": "Test",
    'identifier': 'Test-123%',
    "skillMetadata": {
        "sections": [
            {
                "name": "Test-456",
                "fields": [
                    {
                        "type": "label",
                        "label": "label-test"
                    },
                    {
                        "name": "user",
                        "type": "text",
                        "label": "Username",
                        "value": "this name is a test",
                        "placeholder": "this is a test"
                    },
                    {
                        "name": "password",
                        "type": "password",
                        "label": "Password",
                        "value": "this is a new password"
                    }
                ]
            }
        ]
    }
}


@given('a device with skill settings')
def create_skill_settings(context):
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.upload_device_response = context.client.put(
        '/device/{uuid}/skill'.format(uuid=device_id),
        data=json.dumps(skill),
        content_type='application_json',
        headers=headers
    )
    context.get_skill_response = context.client.get(
        '/device/{uuid}/skill'.format(uuid=device_id),
        headers=headers
    )


@when('the skill settings are updated')
def update_skill(context):
    update_settings = [{
        'settingsValues': new_settings,
        'devices': [context.device_name]
    }]
    response = json.loads(context.upload_device_response.data)
    skill_id = response['uuid']
    with get_db_connection(context.client_config['DB_CONNECTION_POOL']) as db:
        SkillSettingRepository(db).update_device_skill_settings(skill_id, update_settings)


@when('the skill settings is fetched')
def retrieve_skill_updated(context):
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers=dict(Authorization='Bearer {token}'.format(token=access_token))
    context.get_skill_updated_response = context.client.get(
        '/device/{uuid}/skill'.format(uuid=device_id),
        headers=headers
    )


@then('the skill settings should be retrieved with the new values')
def validate_get_skill_updated_response(context):
    # First we validate the skill uploading
    response = context.upload_device_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))

    # Then we validate if the skill we fetch is the same that was uploaded
    response = context.get_skill_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    skills_response = json.loads(response.data)
    assert_that(len(skills_response), equal_to(1))
    response = skills_response[0]
    assert_that(response['name'], equal_to(skill['name']))
    assert_that(response['identifier'], equal_to(skill['identifier']))
    assert_that(response['skillMetadata'], equal_to(skill['skillMetadata']))

    # Then we validate if the skill was properly updated
    response = context.get_skill_updated_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    response_data = json.loads(response.data)
    assert_that(len(response_data), equal_to(1))
    response_data = response_data[0]
    assert_that(response_data['name'], equal_to(skill_updated['name']))
    assert_that(response_data['identifier'], equal_to(skill_updated['identifier']))
    assert_that(response_data['skillMetadata'], equal_to(skill_updated['skillMetadata']))
