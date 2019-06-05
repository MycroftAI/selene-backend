import os
from http import HTTPStatus

from selene.api import PublicEndpoint
from selene.data.account import AccountRepository


class PremiumVoiceEndpoint(PublicEndpoint):
    def __init__(self):
        super(PremiumVoiceEndpoint, self).__init__()

    def get(self, device_id):
        self._authenticate(device_id)
        arch = self.request.args.get('arch')
        account = AccountRepository(self.db).get_account_by_device_id(device_id)
        if account and account.membership:
            link = self._get_premium_voice_link(arch)
            response = {'link': link}, HTTPStatus.OK
        else:
            response = '', HTTPStatus.NO_CONTENT
        return response

    def _get_premium_voice_link(self, arch):
        if arch == 'arm':
            response = os.environ['URL_VOICE_ARM']
        elif arch == 'x86_64':
            response = os.environ['URL_VOICE_X86_64']
        else:
            response = ''
        return response
