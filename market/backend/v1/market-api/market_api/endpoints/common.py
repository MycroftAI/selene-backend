from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import List

from markdown import markdown

import requests as service_request

DEFAULT_ICON_COLOR = '#6C7A89'
DEFAULT_ICON_NAME = 'comment-alt'
SYSTEM_CATEGORY = 'System'
UNDEFINED_CATEGORY = 'Not Categorized'
VALID_INSTALLATION_VALUES = ('failed', 'installed', 'installing', 'uninstalled')


@dataclass
class RepositorySkill(object):
    """Represents a single skill defined in the Mycroft Skills repository."""
    branch: str
    categories: List[str]
    created: str
    credits: List[dict]
    description: str
    icon: dict
    id: str
    is_mycroft_made: bool = field(init=False)
    is_system_skill: bool = field(init=False)
    last_update: str
    market_category: str = field(init=False)
    platforms: List[str]
    repository_owner: str
    repository_url: str
    skill_name: str
    summary: str
    tags: List[str]
    title: str
    triggers: List[str]
    icon_image: str = field(default=None)

    def __post_init__(self):
        self.is_system_skill = False
        if 'system' in self.tags:
            self.is_system_skill = True
            self.market_category = SYSTEM_CATEGORY
        elif self.categories:
            # a skill may have many categories.  the first one in the
            # list is considered the "primary" category.  This is the
            # category the marketplace will use to group the skill.
            self.market_category = self.categories[0]
        else:
            self.market_category = UNDEFINED_CATEGORY

        if not self.icon:
            self.icon = dict(icon=DEFAULT_ICON_NAME, color=DEFAULT_ICON_COLOR)

        self.is_mycroft_made = self.credits[0].get('name') == 'Mycroft AI'
        self.summary = markdown(self.summary, output_format='html5')


@dataclass
class ManifestSkill(object):
    """Represents a single skill on a device's skill manifest.

    Mycroft core keeps a manifest off all skills associated with a device.
    This manifest shows the status of each skill as it relates to the device.
    """
    beta: bool
    failure_message: str
    installation: str
    installed_on: int
    name: str
    origin: str
    status: str
    updated: int


def call_skill_manifest_endpoint(token: str, base_url: str, user_uuid: str):
    """Get the skill manifests from each of a user's devices

    The skill manifests will be used to determine the status of each
    skill as it relates to the marketplace.
    """
    service_request_headers = {'Authorization': 'Bearer ' + token}
    service_url = base_url + '/user/' + user_uuid + '/skillJson'
    response = service_request.get(
        service_url,
        headers=service_request_headers
    )

    return response


def parse_skill_manifest_response(response) -> defaultdict:
    skills_in_manifests = defaultdict(list)
    response_skills = response.json()
    for device in response_skills.get('devices', []):
        for skill in device['skills']:
            manifest_skill = ManifestSkill(**skill)
            skills_in_manifests[manifest_skill.name].append(
                manifest_skill
            )

    return skills_in_manifests


class SkillManifestAggregator(object):
    """Base class containing functionality shared by summary and detail"""

    def __init__(self, manifest_skills: List[ManifestSkill]):
        self.manifest_skills = manifest_skills
        self.aggregate_skill = ManifestSkill(**asdict(manifest_skills[0]))

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
        failed = [s.installation == 'failed' for s in self.manifest_skills]
        installing = [
            s.installation == 'installing' for s in self.manifest_skills
        ]
        uninstalling = [
            s.installation == 'uninstalling' for s in self.manifest_skills
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


def aggregate_manifest_skills(
        manifest_skills: List[ManifestSkill]
) -> ManifestSkill:
    skill_aggregator = SkillManifestAggregator(manifest_skills)
    skill_aggregator.aggregate_manifest_skills()

    return skill_aggregator.aggregate_skill
