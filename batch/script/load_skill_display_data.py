# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Update skill.display table with skill information from repositories.

Download skill-metadata.json from the mycroft-skills-data GitHub repository.
Use the contents of the file to update the skill.display table which is
primarily for displaying skills in the marketplace.

The mycroft-skills-data repository has a branch for each major release of
Mycroft core containing the skills available in that release.
"""
import json
from os import environ

from selene.batch import SeleneScript
from selene.data.skill import (
    SkillDisplay,
    SkillDisplayRepository,
    SkillRepository
)
from selene.util.github import download_repository_file, log_into_github

GITHUB_USER = environ['GITHUB_USER']
GITHUB_PASSWORD = environ['GITHUB_PASSWORD']
SKILL_DATA_GITHUB_REPO = 'mycroft-skills-data'
SKILL_DATA_FILE_NAME = 'skill-metadata.json'


class SkillDisplayUpdater(SeleneScript):
    def __init__(self):
        super(SkillDisplayUpdater, self).__init__(__file__)
        self.skill_display_data = None

    def _define_args(self):
        super(SkillDisplayUpdater, self)._define_args()
        self._arg_parser.add_argument(
            "--core-version",
            help='Version of Mycroft Core related to skill display data',
            required=True,
            type=str
        )

    def _run(self):
        """Make it so."""
        self.log.info(
            "Updating skill display data for core version " +
            self.args.core_version
        )
        self._get_skill_display_data()
        self._update_skill_display_table()

    def _get_skill_display_data(self):
        """Use the GitHub API to retrieve the JSON file."""
        github_api = log_into_github(GITHUB_USER, GITHUB_PASSWORD)
        file_contents = download_repository_file(
            github_api,
            SKILL_DATA_GITHUB_REPO,
            self.args.core_version,
            SKILL_DATA_FILE_NAME
        )
        self.skill_display_data = json.loads(file_contents)

    def _update_skill_display_table(self):
        skill_count = 0
        skill_repository = SkillRepository(self.db)
        display_repository = SkillDisplayRepository(self.db)
        for skill_name, skill_metadata in self.skill_display_data.items():
            skill_count += 1
            skill_id = skill_repository.ensure_skill_exists(
                skill_metadata['skill_gid']
            )

            # add the skill display row
            display_data = SkillDisplay(
                skill_id=skill_id,
                core_version=self.args.core_version,
                display_data=json.dumps(skill_metadata)
            )
            display_repository.upsert(display_data)

        self.log.info("updated {} skills".format(skill_count))


if __name__ == '__main__':
    SkillDisplayUpdater().run()
