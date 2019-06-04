import json
from os import environ

from base import SeleneScript
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
        self.log.info(
            "Updating skill display data for core version " +
            self.args.core_version
        )
        self._get_skill_display_data()
        self._update_skill_display_table()

    def _get_skill_display_data(self):
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


SkillDisplayUpdater().run()
