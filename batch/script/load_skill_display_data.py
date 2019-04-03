import json
from os import environ

from selene.data.skill import (
    SkillDisplay,
    SkillDisplayRepository,
    SkillRepository
)
from selene.util.db import connect_to_db, DatabaseConnectionConfig
from selene.util.github import download_repository_file, log_into_github

GITHUB_USER = environ['GITHUB_USER']
GITHUB_PASSWORD = environ['GITHUB_PASSWORD']
SKILL_DATA_GITHUB_REPO = 'mycroft-skills-data'
SKILL_DATA_FILE_NAME = 'skill-metadata.json'

mycroft_db = DatabaseConnectionConfig(
    host=environ['DB_HOST'],
    db_name=environ['DB_NAME'],
    user=environ['DB_USER'],
    password=environ['DB_PASSWORD'],
    port=environ['DB_PORT'],
    sslmode=environ['DB_SSL_MODE']

)
# TODO figure out a way to paramaterize these
github = log_into_github(GITHUB_USER, GITHUB_PASSWORD)
file_contents = download_repository_file(
    github,
    SKILL_DATA_GITHUB_REPO,
    '19.02',
    SKILL_DATA_FILE_NAME
)
skills_metadata = json.loads(file_contents)
with connect_to_db(mycroft_db) as db:
    skill_repository = SkillRepository(db)
    display_repository = SkillDisplayRepository(db)
    for skill_name, skill_metadata in skills_metadata.items():
        # Ensure the skill exists on the skill table
        skill_id = skill_repository.ensure_skill_exists(
            skill_metadata['skill_gid']
        )

        # add the skill display row
        display_data = SkillDisplay(
            skill_id=skill_id,
            core_version='18.08',
            display_data=json.dumps(skill_metadata)
        )
        display_repository.upsert(display_data)
