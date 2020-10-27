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
"""Testing helper functions for the tagging schema."""
from datetime import datetime
from selene.data.tagging import (
    WakeWordFile,
    WakeWordFileRepository,
    TaggingFileLocationRepository,
    UPLOADED_STATUS,
)


def remove_wake_word_files(db, wake_word_file):
    """Remove a wake word files by wake word and their associated data."""
    file_repository = WakeWordFileRepository(db)
    file_repository.remove(wake_word_file)


def add_wake_word_file(context, file_name):
    """Add a row to the tagging.file table for testing."""
    location_repository = TaggingFileLocationRepository(context.db)
    file_location = location_repository.ensure_location_exists(
        server="127.0.0.1", directory="some/dummy/file/directory"
    )
    wake_word_file = WakeWordFile(
        wake_word=context.wake_words["hey selene"],
        name=file_name,
        origin="mycroft",
        submission_date=datetime.utcnow().date(),
        location=file_location,
        status=UPLOADED_STATUS,
        account_id=context.account.id,
    )
    file_repository = WakeWordFileRepository(context.db)
    file_repository.add(wake_word_file)
