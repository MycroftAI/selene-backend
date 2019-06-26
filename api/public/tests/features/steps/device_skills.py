import json
from http import HTTPStatus

from behave import when, then, given
from hamcrest import assert_that, equal_to, not_none, is_not, has_key

from selene.api.etag import ETagManager, device_skill_etag_key
from selene.data.skill import AccountSkillSetting, SkillSettingRepository
from selene.util.db import connect_to_db

skill = {
    'skill_gid': 'wolfram-alpha|19.02',
    'identifier': 'wolfram-alpha-123456',
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

skill_empty_settings = {
    'skill_gid': 'mycroft-alarm|19.02',
    'identifier': 'mycroft-alarm|19.02'
}

new_settings = {
    'user': 'this name is a test',
    'password': 'this is a new password'
}

skill_updated = {
    'skill_gid': 'wolfram-alpha|19.02',
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
    # Same request being done twice to simulate a bug related to uniqueness violation
    context.client.put(
        '/v1/device/{uuid}/skill'.format(uuid=device_id),
        data=json.dumps(skill),
        content_type='application_json',
        headers=headers
    )
    context.upload_device_response = context.client.put(
        '/v1/device/{uuid}/skill'.format(uuid=device_id),
        data=json.dumps(skill),
        content_type='application_json',
        headers=headers
    )
    context.get_skill_response = context.client.get(
        '/v1/device/{uuid}/skill'.format(uuid=device_id),
        headers=headers
    )


@when('the skill settings are updated')
def update_skill(context):
    response = json.loads(context.upload_device_response.data)
    update_settings = AccountSkillSetting(
        settings_display={},
        settings_values=new_settings,
        device_names=[context.device_name]
    )
    skill_ids = [response['uuid']]
    db = connect_to_db(context.client_config['DB_CONNECTION_CONFIG'])
    skill_setting_repo = SkillSettingRepository(db, context.account.id)
    skill_setting_repo.update_skill_settings(update_settings, skill_ids)


@when('the skill settings is fetched')
def retrieve_skill_updated(context):
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers=dict(Authorization='Bearer {token}'.format(token=access_token))
    context.get_skill_updated_response = context.client.get(
        '/v1/device/{uuid}/skill'.format(uuid=device_id),
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
    assert_that(response, has_key('uuid'))
    assert_that(response['skill_gid'], equal_to(skill['skill_gid']))
    assert_that(response['identifier'], equal_to(skill['identifier']))
    assert_that(response['skillMetadata'], equal_to(skill['skillMetadata']))

    # Then we validate if the skill was properly updated
    response = context.get_skill_updated_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    response_data = json.loads(response.data)
    assert_that(len(response_data), equal_to(1))
    response_data = response_data[0]
    assert_that(response_data['skill_gid'], equal_to(skill_updated['skill_gid']))
    assert_that(response_data['skillMetadata'], equal_to(skill_updated['skillMetadata']))


@when('the skill settings are fetched using a valid etag')
def get_skills_etag(context):
    etag_manager: ETagManager = context.etag_manager
    login = context.device_login
    device_id = login['uuid']
    skill_etag = etag_manager.get(device_skill_etag_key(device_id))
    access_token = login['accessToken']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'If-None-Match': skill_etag
    }
    context.get_skill_response = context.client.get(
        '/v1/device/{uuid}/skill'.format(uuid=device_id),
        headers=headers
    )


@then('the skill setting endpoint should return 304')
def validate_etag(context):
    response = context.get_skill_response
    assert_that(response.status_code, HTTPStatus.NOT_MODIFIED)


@when('the skill settings are fetched using an expired etag')
def get_skills_expired_etag(context):
    etag_manager: ETagManager = context.etag_manager
    login = context.device_login
    device_id = login['uuid']
    context.old_skill_etag = etag_manager.get(device_skill_etag_key(device_id))
    etag_manager.expire_skill_etag_by_device_id(device_id)
    access_token = login['accessToken']
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'If-None-Match': context.old_skill_etag
    }
    context.get_skill_response = context.client.get(
        '/v1/device/{uuid}/skill'.format(uuid=device_id),
        headers=headers
    )


@then('the skill settings endpoint should return a new etag')
def validate_expired_etag(context):
    response = context.get_skill_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    new_etag = response.headers.get('ETag')
    assert_that(new_etag, not_none())
    assert_that(context.old_skill_etag, is_not(new_etag))


@when('a skill with empty settings is uploaded')
def upload_empty_skill(context):
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.upload_device_response = context.client.put(
        '/v1/device/{uuid}/skill'.format(uuid=device_id),
        data=json.dumps(skill_empty_settings),
        content_type='application_json',
        headers=headers
    )
    context.get_skill_response = context.client.get(
        '/v1/device/{uuid}/skill'.format(uuid=device_id),
        headers=headers
    )


@then('the endpoint to retrieve the skill should return 200')
def validate_empty_skill_uploading(context):
    response = context.upload_device_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))

    response = context.get_skill_response
    assert_that(response.status_code, equal_to(HTTPStatus.OK))
    new_etag = response.headers.get('ETag')
    assert_that(new_etag, not_none())
    retrieved_skill = json.loads(context.get_skill_response.data)[0]
    assert_that(skill_empty_settings['skill_gid'], retrieved_skill['skill_gid'])
    assert_that(skill_empty_settings['identifier'], retrieved_skill['identifier'])


@when('the skill settings is deleted')
def delete_skill(context):
    skills = json.loads(context.get_skill_response.data)
    skill_fetched = skills[0]
    skill_uuid = skill_fetched['uuid']
    login = context.device_login
    device_id = login['uuid']
    access_token = login['accessToken']
    headers = dict(Authorization='Bearer {token}'.format(token=access_token))
    context.delete_skill_response = context.client.delete(
        '/v1/device/{device_uuid}/skill/{skill_uuid}'.format(device_uuid=device_id, skill_uuid=skill_uuid),
        headers=headers
    )
    context.get_skill_after_delete_response = context.client.get(
        '/v1/device/{uuid}/skill'.format(uuid=device_id),
        headers=headers
    )


@then('the endpoint to delete the skills settings should return 200')
def validate_delete_skill(context):
    # Validating that the deletion happened successfully
    response = context.delete_skill_response
    assert_that(response.status_code, HTTPStatus.OK)

    # Validating that the skill is not listed after we fetch the device's skills
    response = context.get_skill_after_delete_response
    assert_that(response.status_code, equal_to(HTTPStatus.NO_CONTENT))
