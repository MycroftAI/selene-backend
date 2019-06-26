import json
from http import HTTPStatus

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository


class StripeWebHookEndpoint(PublicEndpoint):

    def __init__(self):
        super(StripeWebHookEndpoint, self).__init__()

    def post(self):
        event = json.loads(self.request.data)
        type = event.get('type')
        if type == 'customer.subscription.deleted':
            customer = event['data']['object']['customer']
            AccountRepository(self.db).end_active_membership(customer)
        return '', HTTPStatus.OK
