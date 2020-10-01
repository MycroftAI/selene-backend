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

"""Move wake word samples from public API host to long-term storage."""
import shlex
from os import environ, remove
from pathlib import Path
from subprocess import run

from selene.batch import SeleneScript
from selene.data.tagging import (
    TaggingFileLocationRepository,
    WakeWordFileRepository,
)


class WakeWordSampleMover(SeleneScript):
    dest_base_dir = Path(environ["PRECISE_WAKE_WORD_DIR"])
    precise_server = environ["PRECISE_SERVER"]
    precise_ssh_port = environ.get("PRECISE_SSH_PORT")
    _file_repository = None

    def __init__(self):
        super(WakeWordSampleMover, self).__init__(__file__)
        self.new_directories = dict()

    def _run(self):
        wake_word_files = self._get_wake_word_file_info()
        self._move_files(wake_word_files)

    @property
    def file_repository(self):
        if self._file_repository is None:
            self._file_repository = WakeWordFileRepository(self.db)

        return self._file_repository

    def _get_wake_word_file_info(self):
        wake_word_files = self.file_repository.get_by_submission_date(self.args.date)
        self.log.info(f"{len(wake_word_files)} wake word samples will be moved")

        return wake_word_files

    def _move_files(self, wake_word_file_info):
        self.log.info(f"moving wake word sample files to {self.precise_server}")
        for file_info in wake_word_file_info:
            destination_dir = self._ensure_remote_directory_exists(file_info)
            self._copy_file(file_info, destination_dir)
            self.file_repository.change_file_location(
                file_info.id, self.new_directories[destination_dir]
            )
            remove(str(Path(file_info.location.directory).joinpath(file_info.name)))

    def _ensure_remote_directory_exists(self, file_info) -> Path:
        remote_directory = self.dest_base_dir.joinpath(
            file_info.wake_word.name.replace(" ", "-"), str(file_info.submission_date)
        )
        self._ensure_directory_exists_on_server(remote_directory)
        self._ensure_directory_exists_on_db(remote_directory)

        return remote_directory

    def _ensure_directory_exists_on_server(self, directory):
        cmd = f"ssh precise@{self.precise_server} "
        if self.precise_ssh_port:
            cmd += f"-p {self.precise_ssh_port} "
        cmd += f'"mkdir -p {directory}"'
        run(shlex.split(cmd), check=True)

    def _ensure_directory_exists_on_db(self, new_directory):
        file_location_repository = TaggingFileLocationRepository(self.db)
        if new_directory not in self.new_directories:
            new_location = file_location_repository.ensure_location_exists(
                server=self.precise_server, directory=new_directory
            )
            self.new_directories[new_directory] = new_location.id

    def _copy_file(self, file_info, destination_dir):
        source_path = Path(file_info.location.directory).joinpath(file_info.name)
        destination_path = destination_dir.joinpath(file_info.name)
        cmd = f"scp "
        if self.precise_ssh_port:
            cmd += f"-P {self.precise_ssh_port} "
        cmd += f"{source_path} precise@{self.precise_server}:{destination_path}"
        run(shlex.split(cmd), check=True)


if __name__ == "__main__":
    WakeWordSampleMover().run()
