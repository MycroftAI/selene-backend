from datetime import datetime
import json
from os import environ

from skill_service.repository import (
    connect_to_skill_db,
    select_all_skills,
    Skill,
    upsert_skill
)
from selene_util.github import download_repository_file, log_into_github


class SkillRefresher(object):
    """
    Reconcile a skill repository's README.md with the database
    """
    def __init__(self, skill: Skill, github_metadata):
        self.skill = skill
        self.skill_metadata = github_metadata

    def _skill_meta_changed(self) -> bool:
        """
        Determine if any of the skill metadata fields will be updated.

        This is important to know whether or not the last update timestamp
        needs a new value. Changes in the metadata will result in an update
        of the timestamp whereas the timestamp will stay the same if nothing
        has changed.
        """
        return (
            self.skill.categories != self.skill_metadata.get('categories', []) or
            self.skill.credits != self.skill_metadata.get('credits', []) or
            self.skill.description != self.skill_metadata['description'] or
            self.skill.icon != self.skill_metadata.get('icon') or
            self.skill.icon_image != self.skill_metadata.get('icon_img') or
            self.skill.platforms != self.skill_metadata['platforms'] or
            self.skill.repository_owner != self.skill_metadata['github_username'] or
            self.skill.repository_url != self.skill_metadata['repo'] or
            self.skill.summary != self.skill_metadata.get('short_desc') or
            self.skill.tags != self.skill_metadata['tags'] or
            self.skill.title != self.skill_metadata['title'] or
            self.skill.triggers != self.skill_metadata.get('examples')
        )

    def refresh(self):
        """
        Refresh the skill database with the repository README.md file
        """
        if self._skill_meta_changed():
            self.skill.branch = environ['SKILL_BRANCH']
            self.skill.categories = self.skill_metadata.get('categories')
            self.skill.credits = self.skill_metadata.get('credits')
            self.skill.description = self.skill_metadata['description']
            self.skill.last_update = datetime.now()
            self.skill.icon = self.skill_metadata.get('icon')
            self.skill.icon_image = self.skill_metadata.get('icon_img')
            self.skill.platforms = self.skill_metadata['platforms']
            self.skill.repository_owner = self.skill_metadata['github_username']
            self.skill.repository_url = self.skill_metadata['repo']
            self.skill.skill_name = self.skill_metadata['name']
            self.skill.summary = self.skill_metadata.get('short_desc')
            self.skill.tags = self.skill_metadata.get('tags')
            self.skill.title = self.skill_metadata['title']
            self.skill.triggers = self.skill_metadata.get('examples')
            upsert_skill(self.skill)


connect_to_skill_db()
skills_in_db = {skill.skill_name: skill for skill in select_all_skills()}

# TODO figure out a way to paramaterize these
github = log_into_github('dev@mycroft.ai', 'pFuG8z5ngmqVDla1aaED2rKl3yke5vZ7')
file_contents = download_repository_file(
    github,
    'mycroft-skills-data',
    '18.08',
    'skill-metadata.json'
)
skills_metadata = json.loads(file_contents)
for skill_identifier, skill_metadata in skills_metadata.items():
    skill_in_db = skills_in_db.get(skill_identifier, Skill())
    skill_refresher = SkillRefresher(skill_in_db, skill_metadata)
    skill_refresher.refresh()
