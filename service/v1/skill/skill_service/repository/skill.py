"""
Queries and manipulations of the skill collection in the marketplaceDB
"""
from datetime import datetime

from mongoengine import Document, DateTimeField, ListField, StringField

from .db import connect_to_skill_db


class Skill(Document):
    """
    Represents the schema of documents in the skill collection
    """
    skill_name = StringField(required=True, unique=True)
    repository_url = StringField(required=True)
    title = StringField(required=True)
    author = StringField()
    summary = StringField()
    description = StringField()
    triggers = ListField(StringField())
    category = StringField()
    last_update = DateTimeField(default=datetime.now(), required=True)


def select_all_skills() -> list:
    """
    Skill repositories in Github must be uniquely named; map the repository name to the skill object

    :return: dictionary of skill objects keyed by the repository name
    """
    connect_to_skill_db()
    return Skill.objects


def select_skill_by_id(skill_id: str) -> Skill:
    """
    Query the database for a specified skill ID

    :return: the Skill object with an ID matching the argument
    """
    connect_to_skill_db()
    return Skill.objects(id=skill_id).first()


def upsert_skill(skill: Skill):
    """
    An upsert will update a document if it exists or insert it if not.

    :param skill:  The skill to update or insert
    """
    connect_to_skill_db()
    skill.save()
