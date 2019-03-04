"""
Queries and manipulations of the skill collection in the marketplaceDB
"""
from datetime import datetime

from mongoengine import (
    DateTimeField,
    DictField,
    Document,
    ListField,
    StringField
)

from .db import connect_to_skill_db


class Skill(Document):
    """
    Represents the schema of documents in the skill collection
    """
    branch = StringField(required=True)
    categories = ListField(StringField())
    credits = ListField(DictField())
    description = StringField()
    icon = DictField()
    icon_image = StringField()
    last_update = DateTimeField(default=datetime.now(), required=True)
    platforms = ListField(StringField(), required=True, default=['all'])
    repository_owner = StringField(required=True)
    repository_url = StringField(required=True)
    skill_name = StringField(required=True, unique=True)
    summary = StringField()
    tags = ListField(StringField())
    title = StringField(required=True)
    triggers = ListField(StringField())


def select_all_skills() -> list:
    """
    Map the repository name to the skill object

    Skill repositories in Github must be uniquely named

    :return: dictionary of skill objects keyed by the repository name
    """
    connect_to_skill_db()
    return Skill.objects


def select_skill_by_name(skill_name: str) -> Skill:
    """
    Query the database for a specified skill ID

    :return: the Skill object with an ID matching the argument
    """
    connect_to_skill_db()
    return Skill.objects(skill_name=skill_name).first()


def upsert_skill(skill: Skill):
    """
    An upsert will update a document if it exists or insert it if not.

    :param skill:  The skill to update or insert
    """
    connect_to_skill_db()
    skill.save()
