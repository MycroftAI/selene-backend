from collections import defaultdict
from dataclasses import asdict, dataclass
from http import HTTPStatus
from typing import List

import requests as service_request

from selene_util.api import APIError, SeleneEndpoint

VALID_INSTALLATION_VALUES = (
    'failed',
    'installed',
    'installing',
    'uninstalling'
)


@dataclass
class ManifestSkill(object):
    """Represents a single skill on a device's skill manifest.

    Mycroft core keeps a manifest off all skills associated with a device.
    This manifest shows the status of each skill as it relates to the device.
    """
    failure_message: str
    installation: str
    name: str


class SkillInstallationsEndpoint(SeleneEndpoint):
    authentication_required = False

    def __init__(self):
        super(SkillInstallationsEndpoint, self).__init__()
        self.skills_in_manifests = defaultdict(list)

    def get(self):
        try:
            self._get_install_statuses()
        except APIError:
            pass
        else:
            response_data = self._build_response_data()
            self.response = (response_data, HTTPStatus.OK)

        return self.response

    def _get_install_statuses(self):
        self._authenticate()
        if self.authenticated:
            skill_manifests = self._get_skill_manifests()
            self._parse_skill_manifests(skill_manifests)
        else:
            self.response = (
                dict(installStatuses=[], failureReasons=[]),
                HTTPStatus.OK
            )

    def _get_skill_manifests(self) -> dict:
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
        response = service_request.get(
            service_url,
            headers=service_request_headers
        )

        self._check_for_service_errors(response)

        return response.json()

    def _parse_skill_manifests(self, skill_manifests: dict):
        for device in skill_manifests.get('devices', []):
            for skill in device['skills']:
                manifest_skill = ManifestSkill(
                    failure_message=skill['failure_message'],
                    installation=skill['installation'],
                    name=skill['name']
                )
                self.skills_in_manifests[manifest_skill.name].append(
                    manifest_skill
                )
            self.skills_in_manifests['mycroft-audio-record'].append(ManifestSkill(
                failure_message='',
                installation='installed',
                name='mycroft-audio-record'
            ))

    def _build_response_data(self) -> dict:
        install_statuses = {}
        failure_reasons = {}
        for skill_name, manifest_skills in self.skills_in_manifests.items():
            skill_aggregator = SkillManifestAggregator(manifest_skills)
            skill_aggregator.aggregate_manifest_skills()
            if skill_aggregator.aggregate_skill.installation == 'failed':
                failure_reasons[skill_name] = (
                    skill_aggregator.aggregate_skill.failure_message
                )
            install_statuses[skill_name] = (
                skill_aggregator.aggregate_skill.installation
            )

        return dict(
            installStatuses=install_statuses,
            failureReasons=failure_reasons
        )


class SkillManifestAggregator(object):
    """Base class containing functionality shared by summary and detail"""

    def __init__(self, manifest_skills: List[ManifestSkill]):
        self.manifest_skills = manifest_skills
        self.aggregate_skill = ManifestSkill(
            **asdict(manifest_skills[0]))

    def aggregate_manifest_skills(self):
        """Aggregate skill data on all devices into a single skill.

        Each skill is represented once on the Marketplace, even though it can
        be present on multiple devices.
        """
        self._validate_install_status()
        self._determine_install_status()
        if self.aggregate_skill.installation == 'failed':
            self._determine_failure_reason()

    def _validate_install_status(self):
        for manifest_skill in self.manifest_skills:
            if manifest_skill.installation not in VALID_INSTALLATION_VALUES:
                raise ValueError(
                    '"{install_status}" is not a supported value of the '
                    'installation field in the skill manifest'.format(
                        install_status=manifest_skill.installation
                    )
                )

    def _determine_install_status(self):
        """Use skill data from all devices to determine install status.

        When a skill is installed via the Marketplace, it is installed to all
        devices.  The Marketplace will not mark a skill as "installed" until
        install is complete on all devices.  Until that point, the status will
        be "installing".

        If the install fails on any device, the install will be flagged as a
        failed install in the Marketplace.
        """
        failed = [s.installation == 'failed' for s in
                  self.manifest_skills]
        installing = [
            s.installation == 'installing' for s in self.manifest_skills
        ]
        uninstalling = [
            s.installation == 'uninstalling' for s in
            self.manifest_skills
        ]
        installed = [
            s.installation == 'installed' for s in self.manifest_skills
        ]
        if any(failed):
            self.aggregate_skill.installation = 'failed'
        elif any(installing):
            self.aggregate_skill.installation = 'installing'
        elif any(uninstalling):
            self.aggregate_skill.installation = 'uninstalling'
        elif all(installed):
            self.aggregate_skill.installation = 'installed'

    def _determine_failure_reason(self):
        """When a skill fails to install, determine the reason"""
        for manifest_skill in self.manifest_skills:
            if manifest_skill.installation == 'failed':
                self.aggregate_skill.failure_reason = (
                    manifest_skill.failure_message
                )
                break
