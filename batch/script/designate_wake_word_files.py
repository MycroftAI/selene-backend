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

"""Convert tags to designations if the criteria for becoming a designation is met."""
from typing import List

from selene.batch import SeleneScript
from selene.data.tagging import (
    FileDesignation,
    FileDesignationRepository,
    FileTag,
    FileTagRepository,
    TagRepository,
)


class WakeWordFileDesignator(SeleneScript):
    """Batch script to convert tags to designations."""

    _tag_names = None

    def __init__(self):
        super().__init__(__file__)
        self.prev_file_tag_id = None
        self.designation_stats = dict()
        self.value_counts = dict()
        self.file_tags = 0
        self.wake_word_tags = 0

    @property
    def tag_names(self):
        """Get the names related to the tag IDs and their values for logging."""
        if self._tag_names is None:
            self._tag_names = dict()
            tag_repo = TagRepository(self.db)
            tags = tag_repo.get_all()
            for tag in tags:
                tag_values = dict()
                for tag_value in tag.values:
                    tag_values[tag_value.id] = tag_value.value
                self._tag_names[tag.id] = (tag.name, tag_values)

        return self._tag_names

    def _run(self):
        """Make it so."""
        designation_candidates = self._get_designation_candidates()
        for wake_word, file_tags in designation_candidates.items():
            self.wake_word_tags = len(file_tags)
            self._assign_designations(file_tags)
            self._log_designation_stats(wake_word)

    def _get_designation_candidates(self) -> dict:
        """Get file tags that have not yet been converted to designations

        :return: dictionary keyed by wake word with list of candidates as values.
        """
        file_tag_repo = FileTagRepository(self.db)
        return file_tag_repo.get_designation_candidates()

    def _assign_designations(self, file_tags: List[FileTag]):
        """Evaluate tagging activity to determine if any designations can be derived.

        :param file_tags: List of tagging events for a wake word.
        """
        self._init_tag(file_tags[0])
        for file_tag in file_tags:
            file_tag_id = file_tag.file_id, file_tag.tag_id
            if file_tag_id != self.prev_file_tag_id:
                self._convert_tags_to_designations()
                self._init_tag(file_tag)
            self._increment_value_counts(file_tag.tag_value_id)

    def _init_tag(self, file_tag: FileTag):
        """Initialize file tag level attributes at the beginning of each new tag.

        :param file_tag: The file tag being processed
        """
        self.prev_file_tag_id = file_tag.file_id, file_tag.tag_id
        self.value_counts = dict()
        self.file_tags = 0

    def _increment_value_counts(self, tag_value_id: str):
        """Track how many times each of a tag's values have been assigned to a file.

        :param tag_value_id: the ID of the value assigned in one tag event
        """
        value_count = self.value_counts.get(tag_value_id, 0)
        self.value_counts[tag_value_id] = value_count + 1
        self.file_tags += 1

    def _convert_tags_to_designations(self):
        """Build designations for files with tags that meet the criteria."""
        designation_value = self._apply_designation_criteria()
        if designation_value is not None:
            self._add_designation(designation_value)
            self._increment_designation_stats(designation_value)

    def _apply_designation_criteria(self) -> str:
        """Determine if a file has enough tags to meet the designation criteria.

        :return None if the criteria is not met or the designation if criteria is met
        """
        designation_value = None
        for tag_value, count in self.value_counts.items():
            tag_percent = (count / self.file_tags) * 100
            if count >= 2 and tag_percent > 75:
                designation_value = tag_value
                break

        return designation_value

    def _add_designation(self, designation_value):
        """Add a new file designation to the database

        :param designation_value: The tag value to convert into a designation
        """
        file_id, tag_id = self.prev_file_tag_id
        designation = FileDesignation(
            file_id=file_id, tag_id=tag_id, tag_value_id=designation_value
        )
        file_designation_repo = FileDesignationRepository(self.db)
        file_designation_repo.add(designation)

    def _increment_designation_stats(self, designation_value):
        """Keep track of the designations generated by this script for logging.

        :param designation_value: The tag value to convert into a designation
        """
        _, tag_id = self.prev_file_tag_id
        tag = self.designation_stats.get(tag_id)
        if tag is None:
            self.designation_stats[tag_id] = {designation_value: 1}
        else:
            value_cnt = tag.get(designation_value, 0)
            self.designation_stats[tag_id][designation_value] = value_cnt + 1

    def _log_designation_stats(self, wake_word):
        """Write out log messages regarding the activity for a wake word

        :param wake_word: The wake word for the statistics
        """
        self.log.info(
            "{} tags processed for wake word {}".format(
                str(self.wake_word_tags), wake_word
            )
        )
        log_msg = "Designations applied for wake word: " + wake_word
        for tag_id, tag_values in self.designation_stats.items():
            tag_name, tag_value_names = self.tag_names[tag_id]
            log_msg += "\n\tTag: " + tag_name
            for tag_value_id, tag_value_count in tag_values.items():
                tag_value_name = tag_value_names[tag_value_id]
                log_msg += "\n\t\t{}: {}".format(tag_value_name, tag_value_count)
        if "Tag: " not in log_msg:
            log_msg = log_msg.replace("Designations", "No designations")
        self.log.info(log_msg)


if __name__ == "__main__":
    WakeWordFileDesignator().run()
