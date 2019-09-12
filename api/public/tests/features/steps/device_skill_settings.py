import json

from behave import when, then, given
from hamcrest import assert_that, equal_to, is_not, is_in

from selene.api.etag import ETAG_REQUEST_HEADER_KEY
from selene.data.device import DeviceSkillRepository
from selene.data.skill import SkillSettingRepository
from selene.testing.skill import add_skill, build_label_field, build_text_field
from selene.util.cache import DEVICE_SKILL_ETAG_KEY


@given('skill settings with a new value')
def change_skill_setting_value(context):
    _, bar_settings_display = context.skills['bar']
    section = bar_settings_display.display_data['skillMetadata']['sections'][0]
    field_with_value = section['fields'][1]
    field_with_value['value'] = 'New device text value'


@given('skill settings with a deleted field')
def delete_field_from_settings(context):
    _, bar_settings_display = context.skills['bar']
    section = bar_settings_display.display_data['skillMetadata']['sections'][0]
    context.removed_field = section['fields'].pop(1)


@given('a valid device skill E-tag')
def set_skill_setting_etag(context):
    context.device_skill_etag = context.etag_manager.get(
        DEVICE_SKILL_ETAG_KEY.format(device_id=context.device_id)
    )


@given('an expired device skill E-tag')
def expire_skill_setting_etag(context):
    valid_device_skill_etag = context.etag_manager.get(
        DEVICE_SKILL_ETAG_KEY.format(device_id=context.device_id)
    )
    context.device_skill_etag = context.etag_manager.expire(
        valid_device_skill_etag
    )


@given('settings for a skill not assigned to the device')
def add_skill_not_assigned_to_device(context):
    foobar_skill, foobar_settings_display = add_skill(
        context.db,
        skill_global_id='foobar-skill|19.02',
        settings_fields=[build_label_field(), build_text_field()]
    )
    section = foobar_settings_display.display_data['skillMetadata']['sections'][0]
    field_with_value = section['fields'][1]
    field_with_value['value'] = 'New skill text value'
    context.skills.update(foobar=(foobar_skill, foobar_settings_display))


@when('a device requests the settings for its skills')
def get_device_skill_settings(context):
    if hasattr(context, 'device_skill_etag'):
        context.request_header[ETAG_REQUEST_HEADER_KEY] = (
            context.device_skill_etag
        )
    context.response = context.client.get(
        '/v1/device/{device_id}/skill'.format(device_id=context.device_id),
        content_type='application/json',
        headers=context.request_header
    )


@when('the device sends a request to update the {skill} skill settings')
def update_skill_settings(context, skill):
    _, settings_display = context.skills[skill]
    context.response = context.client.put(
        '/v1/device/{device_id}/skill'.format(device_id=context.device_id),
        data=json.dumps(settings_display.display_data),
        content_type='application/json',
        headers=context.request_header
    )


@when('the device requests a skill to be deleted')
def delete_skill(context):
    foo_skill, _ = context.skills['foo']
    context.response = context.client.delete(
        '/v1/device/{device_id}/skill/{skill_gid}'.format(
            device_id=context.device_id,
            skill_gid=foo_skill.skill_gid
        ),
        headers=context.request_header
    )


@then('the settings are returned')
def validate_response(context):
    response = context.response.json
    assert_that(len(response), equal_to(2))
    foo_skill, foo_settings_display = context.skills['foo']
    foo_skill_expected_result = dict(
        uuid=foo_skill.id,
        skill_gid=foo_skill.skill_gid,
        identifier=foo_settings_display.display_data['identifier']
    )
    assert_that(foo_skill_expected_result, is_in(response))

    bar_skill, bar_settings_display = context.skills['bar']
    section = bar_settings_display.display_data['skillMetadata']['sections'][0]
    field_with_value = section['fields'][1]
    field_with_value['value'] = 'Device text value'
    bar_skill_expected_result = dict(
        uuid=bar_skill.id,
        skill_gid=bar_skill.skill_gid,
        identifier=bar_settings_display.display_data['identifier'],
        skillMetadata=bar_settings_display.display_data['skillMetadata']
    )
    assert_that(bar_skill_expected_result, is_in(response))


@then('the device skill E-tag is expired')
def check_for_expired_etag(context):
    """An E-tag is expired by changing its value."""
    expired_device_skill_etag = context.etag_manager.get(
        DEVICE_SKILL_ETAG_KEY.format(device_id=context.device_id)
    )
    assert_that(
        expired_device_skill_etag.decode(),
        is_not(equal_to(context.device_skill_etag))
    )


@then('the skill settings are updated with the new value')
def validate_updated_skill_setting_value(context):
    settings_repo = SkillSettingRepository(context.db)
    device_skill_settings = settings_repo.get_skill_settings_for_device(
        context.device_id
    )
    device_settings_values = [
        dss.settings_values for dss in device_skill_settings
    ]
    assert_that(len(device_skill_settings), equal_to(2))
    expected_settings_values = dict(textfield='New device text value')
    assert_that(
        expected_settings_values,
        is_in(device_settings_values)
    )


@then('the skill is assigned to the device with the settings populated')
def validate_updated_skill_setting_value(context):
    settings_repo = SkillSettingRepository(context.db)
    device_skill_settings = settings_repo.get_skill_settings_for_device(
        context.device_id
    )
    device_settings_values = [
        dss.settings_values for dss in device_skill_settings
    ]
    assert_that(len(device_skill_settings), equal_to(3))
    expected_settings_values = dict(textfield='New skill text value')
    assert_that(
        expected_settings_values,
        is_in(device_settings_values)
    )


@then('an E-tag is generated for these settings')
def get_skills_etag(context):
    response_headers = context.response.headers
    response_etag = response_headers['ETag']
    skill_etag = context.etag_manager.get(
        DEVICE_SKILL_ETAG_KEY.format(device_id=context.device_id)
    )
    assert_that(skill_etag.decode(), equal_to(response_etag))


@then('the field is no longer in the skill settings')
def validate_skill_setting_field_removed(context):
    settings_repo = SkillSettingRepository(context.db)
    device_skill_settings = settings_repo.get_skill_settings_for_device(
        context.device_id
    )
    device_settings_values = [
        dss.settings_values for dss in device_skill_settings
    ]
    assert_that(len(device_skill_settings), equal_to(2))
    assert_that([None, None], equal_to(device_settings_values))

    new_section = dict(fields=None)
    for device_skill_setting in device_skill_settings:
        skill_gid = device_skill_setting.settings_display['skill_gid']
        if skill_gid.startswith('bar'):
            new_settings_display = device_skill_setting.settings_display
            new_skill_definition = new_settings_display['skillMetadata']
            new_section = new_skill_definition['sections'][0]
    assert_that(context.removed_field, not is_in(new_section['fields']))
