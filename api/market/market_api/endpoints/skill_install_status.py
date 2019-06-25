from collections import defaultdict
from dataclasses import asdict
from http import HTTPStatus
from typing import List

from selene.api import SeleneEndpoint
from selene.data.device import DeviceSkillRepository, ManifestSkill
from selene.util.auth import AuthenticationError

VALID_STATUS_VALUES = (
    'failed',
    'installed',
    'installing',
    'uninstalling'
)


class SkillInstallStatusEndpoint(SeleneEndpoint):
    authentication_required = False

    def __init__(self):
        super(SkillInstallStatusEndpoint, self).__init__()
        self.installed_skills = defaultdict(list)

    def get(self):
        try:
            self._authenticate()
        except AuthenticationError:
            self.response = ('', HTTPStatus.NO_CONTENT)
        else:
            self._get_installed_skills()
            response_data = self._build_response_data()
            self.response = (response_data, HTTPStatus.OK)

        return self.response

    def _get_installed_skills(self):
        skill_repo = DeviceSkillRepository(self.db)
        installed_skills = skill_repo.get_skill_manifest_for_account(
            self.account.id
        )
        for skill in installed_skills:
            self.installed_skills[skill.skill_id].append(skill)

    def _build_response_data(self) -> dict:
        install_statuses = {}
        failure_reasons = {}
        for skill_id, skills in self.installed_skills.items():
            skill_aggregator = SkillManifestAggregator(skills)
            skill_aggregator.aggregate_skill_status()
            if skill_aggregator.aggregate_skill.install_status == 'failed':
                failure_reasons[skill_id] = (
                    skill_aggregator.aggregate_skill.install_failure_reason
                )
            install_statuses[skill_id] = (
                skill_aggregator.aggregate_skill.install_status
            )

        return dict(
            installStatuses=install_statuses,
            failureReasons=failure_reasons
        )


class SkillManifestAggregator(object):
    """Base class containing functionality shared by summary and detail"""

    def __init__(self, installed_skills: List[ManifestSkill]):
        self.installed_skills = installed_skills
        self.aggregate_skill = ManifestSkill(**asdict(installed_skills[0]))

    def aggregate_skill_status(self):
        """Aggregate skill data on all devices into a single skill.

        Each skill is represented once on the Marketplace, even though it can
        be present on multiple devices.
        """
        self._validate_install_status()
        self._determine_install_status()
        if self.aggregate_skill.install_status == 'failed':
            self._determine_failure_reason()

    def _validate_install_status(self):
        for skill in self.installed_skills:
            if skill.install_status not in VALID_STATUS_VALUES:
                raise ValueError(
                    '"{install_status}" is not a supported value of the '
                    'installation field in the skill manifest'.format(
                        install_status=skill.install_status
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
        failed = [
            skill.install_status == 'failed' for skill in self.installed_skills
        ]
        installing = [
            s.install_status == 'installing' for s in self.installed_skills
        ]
        uninstalling = [
            skill.install_status == 'uninstalling' for skill in
            self.installed_skills
        ]
        installed = [
            s.install_status == 'installed' for s in self.installed_skills
        ]
        if any(failed):
            self.aggregate_skill.install_status = 'failed'
        elif any(installing):
            self.aggregate_skill.install_status = 'installing'
        elif any(uninstalling):
            self.aggregate_skill.install_status = 'uninstalling'
        elif all(installed):
            self.aggregate_skill.install_status = 'installed'

    def _determine_failure_reason(self):
        """When a skill fails to install, determine the reason"""
        for skill in self.installed_skills:
            if skill.install_status == 'failed':
                self.aggregate_skill.failure_reason = (
                    skill.install_failure_reason
                )
                break
