# Mycroft Server - Backend
# Copyright (C) 2020 Mycroft AI Inc
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
"""Data access and manipulation functions for the tagging.tag table."""
from typing import List
from ..entity.tag import Tag
from ..entity.tag_value import TagValue
from ...repository_base import RepositoryBase


class TagRepository(RepositoryBase):
    """Data access and manipulation functions for the tagging.tag table."""

    def __init__(self, db):
        super(TagRepository, self).__init__(db, __file__)

    def get_all(self) -> List[Tag]:
        """Return a list of all the tags."""
        tags = []
        db_request = self._build_db_request(sql_file_name="get_tags.sql")
        for row in self.cursor.select_all(db_request):
            tag_values = []
            for tag_value in row["values"]:
                tag_values.append(
                    TagValue(
                        id=tag_value["id"],
                        value=tag_value["value"],
                        display=tag_value["display"],
                    )
                )
                row.update(values=tag_values)
            tags.append(Tag(**row))

        return tags
