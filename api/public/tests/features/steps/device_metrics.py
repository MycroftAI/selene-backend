import json
import uuid

from behave import given, then, when
from hamcrest import assert_that, equal_to

from selene.data.metrics import CoreMetricRepository

METRIC_TYPE_TIMING = 'timing'
metric_value = dict(
    type='timing',
    start='123'
)


@given('an existing device')
def define_authorized_device(context):
    context.metric_device_id = context.device_login['uuid']


@given('a non-existent device')
def define_unauthorized_device(context):
    context.metric_device_id = str(uuid.uuid4())


@when('the metrics endpoint is called')
def call_metrics_endpoint(context):
    headers = dict(Authorization='Bearer {token}'.format(
        token=context.device_login['accessToken'])
    )
    url = '/v1/device/{device_id}/metric/{metric}'.format(
        device_id=context.metric_device_id, metric='timing'
    )
    context.client.content_type = 'application/json'
    context.response = context.client.post(
        url,
        data=json.dumps(metric_value),
        content_type='application/json',
        headers=headers
    )


@then('the metric is saved to the database')
def validate_metric_in_db(context):
    core_metric_repo = CoreMetricRepository(context.db)
    device_metrics = core_metric_repo.get_metrics_by_device(
        context.device_login['uuid']
    )
    device_metric = device_metrics[0]
    assert_that(device_metric.metric_type, equal_to(METRIC_TYPE_TIMING))
    assert_that(device_metric.metric_value, equal_to(metric_value))
