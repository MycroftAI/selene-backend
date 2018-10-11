from collections import defaultdict
from dataclasses import dataclass, field
from http import HTTPStatus

import requests as service_request

from selene_util.api import SeleneEndpoint


@dataclass
class ManifestSkill(object):
    """Represents a single skill on a device's skill manifest.

    Mycroft core keeps a manifest off all skills associated with a device.
    This manifest shows the status of each skill as it relates to the device.
    """
    name: str
    installed: bool
    method: str
    blocked: bool
    status: str
    beta: bool
    installed_on: int
    updated: int
    is_installing: bool = field(init=False)
    install_failed: bool = field(init=False)

    def __post_init__(self):
        if self.method == 'installing':
            self.is_installing = True
        else:
            self.is_installing = False
        if self.method == 'failed':
            self.install_failed = True
        else:
            self.install_failed = False


class SkillEndpointBase(SeleneEndpoint):
    """Base class containing functionality shared by summary and detail"""
    def __init__(self):
        super(SkillEndpointBase, self).__init__()
        self.skills_in_manifests = defaultdict(list)

    def _get_skill_manifests(self):
        """Get the skill manifests from each of a user's devices

        The skill manifests will be used to determine the status of each
        skill as it relates to the marketplace.
        """
        service_request_headers = {
            'Authorization': 'Bearer ' + self.tartarus_token
        }
        service_url = (
            self.config['TARTARUS_BASE_URL'] +
            '/user/' +
            self.user_uuid +
            '/skillJson'
        )
        user_service_response = service_request.get(
            service_url,
            headers=service_request_headers
        )
        if user_service_response.status_code != HTTPStatus.OK:
            self._check_for_service_errors(user_service_response)

        response_skills = user_service_response.json()
        for device in response_skills.get('devices', []):
            for skill in device['skills']:
                manifest_skill = ManifestSkill(**skill)
                self.skills_in_manifests[manifest_skill.name].append(
                    manifest_skill
                )

    def _determine_skill_install_status(self, skill):
        """Use skill data from all devices to determine install status

        When a skill is installed via the Marketplace, it is installed to all
        devices.  The Marketplace will not mark a skill as "installed" until
        install is complete on all devices.  Until that point, the status will
        be "installing".

        If the install fails on any device, the install will be flagged as a
        failed install in the Marketplace.
        """
        manifest_skill_id = skill['name'] + '.' + skill['github_username']
        is_installed = False
        is_installing = False
        install_failed = False
        manifest_skills = self.skills_in_manifests[manifest_skill_id]
        if any([s.install_failed for s in manifest_skills]):
            install_failed = True
        elif any([s.is_installing for s in manifest_skills]):
            is_installing = True
        elif all([s.is_installed for s in manifest_skills]):
            is_installed = True

        return is_installed, is_installing, install_failed
