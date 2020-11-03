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
"""Precise API endpoint for presenting a URL to the GUI for the audio file."""

from os import environ

from flask import abort, send_from_directory

from selene.api import SeleneEndpoint


class AudioFileEndpoint(SeleneEndpoint):
    """Precise API endpoint for presenting a URL to the GUI for the audio file."""

    def get(self, file_name):
        """Handle an HTTP GET request."""
        self._authenticate()
        try:
            return send_from_directory(environ["SELENE_DATA_DIR"], file_name)
        except FileNotFoundError:
            abort(404)
