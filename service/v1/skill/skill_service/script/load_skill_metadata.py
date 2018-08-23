from datetime import datetime
import json

from ..repository.skill import select_all_skills, Skill, upsert_skill
from ..repository.db import connect_to_skill_db
from selene_util.github import download_repository_file


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
            self.skill.skill_name != self.skill_metadata['name'] or
            self.skill.title != self.skill_metadata['title'] or
            self.skill.author != self.skill_metadata['author'] or
            self.skill.summary != self.skill_metadata['short_desc'] or
            self.skill.description != self.skill_metadata['description'] or
            self.skill.triggers != self.skill_metadata['examples'] or
            self.skill.repository_url != self.skill_metadata['repo']
        )

    def refresh(self):
        """
        Refresh the skill database with the repository README.md file
        """
        if self._skill_meta_changed():
            self.skill.skill_name = self.skill_metadata['name']
            self.skill.title = self.skill_metadata['title']
            self.skill.author = self.skill_metadata['author']
            self.skill.summary = self.skill_metadata['short_desc']
            self.skill.description = self.skill_metadata['description']
            self.skill.triggers = self.skill_metadata['examples']
            self.skill.repository_url = self.skill_metadata['repo']
            self.skill.last_update = datetime.now()
            upsert_skill(self.skill)


connect_to_skill_db()
skills_in_db = {skill.repository_name: skill for skill in select_all_skills()}
file_contents = download_repository_file(
    'dev@mycroft.ai',
    'pFuG8z5ngmqVDla1aaED2rKl3yke5vZ7',
    'mycroft-skills-data',
    'skill-metadata.json'
)
skills_metadata = json.loads(file_contents)
for skill_identifier, skill_metadata in skills_metadata.items():
    skill_in_db = skills_in_db.get(skill_identifier, Skill())
    skill_refresher = SkillRefresher(skill_in_db, skill_metadata)
    skill_refresher.refresh()
