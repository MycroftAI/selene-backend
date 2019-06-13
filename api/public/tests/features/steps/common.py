from datetime import datetime

from behave import then
from hamcrest import assert_that, equal_to, not_none

from selene.util.cache import DEVICE_LAST_CONTACT_KEY


@then('device last contact timestamp is updated')
def check_device_last_contact(context):
    key = DEVICE_LAST_CONTACT_KEY.format(device_id=context.device_id)
    value = context.cache.get(key).decode()
    assert_that(value, not_none())

    last_contact_ts = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
    assert_that(last_contact_ts.date(), equal_to(datetime.utcnow().date()))
