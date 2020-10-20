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
"""Public API into the tagging data repository."""

from .entity.file_location import TaggingFileLocation
from .entity.tag import Tag
from .entity.tagger import Tagger
from .entity.wake_word_file import TaggableFile, WakeWordFile
from .entity.wake_word_file_tag import WakeWordFileTag
from .repository.file_location import TaggingFileLocationRepository
from .repository.session import SessionRepository
from .repository.tag import TagRepository
from .repository.tagger import TaggerRepository
from .repository.wake_word_file import (
    build_tagging_file_name,
    DELETED_STATUS,
    PENDING_DELETE_STATUS,
    UPLOADED_STATUS,
    WakeWordFileRepository,
)
from .repository.wake_word_file_tag import FileTagRepository
