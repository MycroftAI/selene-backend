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

"""Delete wake word files for accounts that have been deleted."""
import shlex
from os import environ, listdir, remove, rmdir
from pathlib import Path
from subprocess import run, CalledProcessError

from selene.batch import SeleneScript
from selene.data.tagging import (
    DELETED_STATUS,
    WakeWordFileRepository,
)


class WakeWordFileRemover(SeleneScript):
    precise_server = environ["PRECISE_SERVER"]
    precise_ssh_port = environ.get("PRECISE_SSH_PORT")
    _file_repository = None

    def __init__(self):
        super(WakeWordFileRemover, self).__init__(__file__)

    @property
    def file_repository(self):
        """Lazily instantiate the wake word file repository."""
        if self._file_repository is None:
            self._file_repository = WakeWordFileRepository(self.db)

        return self._file_repository

    def _run(self):
        """Make it so."""
        wake_word_files = self.file_repository.get_pending_delete()
        if not wake_word_files:
            self.log.info('No wake word files in "pending delete" status found.')
        for account_id, files_to_delete in wake_word_files.items():
            self._delete_files_for_account(account_id, files_to_delete)

    def _delete_files_for_account(self, account_id, files_to_delete):
        file_counter = 0
        for file_to_delete in files_to_delete:
            success = self._remove_from_file_system(file_to_delete)
            if success:
                self.file_repository.change_file_status(file_to_delete, DELETED_STATUS)
                empty = self._check_for_empty_directory(file_to_delete.location)
                if empty:
                    self._delete_empty_directory(file_to_delete.location)
                file_counter += 1
        self.log.info(
            f"Deleted {file_counter} wake word files for account {account_id}"
        )

    def _remove_from_file_system(self, file_to_delete):
        file_dir = Path(file_to_delete.location.directory)
        file_path = file_dir.joinpath(file_to_delete.name)
        if file_to_delete.location.server == self.precise_server:
            success = self._remove_from_precise_file_system(file_path)
        else:
            success = self._remove_from_local_file_system(file_path)
        return success

    def _remove_from_precise_file_system(self, file_path):
        delete_command = f'"rm {file_path}"'
        success, stdout, stderr = self._run_on_precise_server(delete_command)
        if not success:
            self.log.error(
                f"Failed to delete file {file_path} from file system on "
                f"{self.precise_server}\n\tstdout: {stdout}\n\tstderr: {stderr}"
            )

        return success

    def _remove_from_local_file_system(self, file_path):
        try:
            remove(file_path)
            success = True
        except FileNotFoundError:
            success = False
            self.log.error(
                f"Failed to delete file {file_path} from local file system - "
                f"file not found"
            )

        return success

    def _check_for_empty_directory(self, file_location):
        directory_empty = False
        if file_location.server == self.precise_server:
            list_command = f'"ls {file_location.directory}"'
            success, stdout, stderr = self._run_on_precise_server(list_command)
            if success:
                if not stdout:
                    directory_empty = True
            else:
                self.log.error(
                    f"Failed to list contents of {file_location.directory} from "
                    f"file system on {file_location.server}\n\tstdout: "
                    f"{stdout}\n\tstderr: {stderr}"
                )
        else:
            if not listdir(file_location.directory):
                directory_empty = True

        return directory_empty

    def _delete_empty_directory(self, file_location):
        if file_location.server == self.precise_server:
            delete_command = f'"rmdir {file_location.directory}"'
            success, stdout, stderr = self._run_on_precise_server(delete_command)
            if success:
                self.log.info(
                    f"Deleted Directory {file_location.directory} "
                    f"on {self.precise_server}"
                )
            else:
                self.log.error(
                    f"Failed to delete directory {file_location.directory} from file "
                    f"system on {file_location.server}\n\tstdout: {stdout}\n\t"
                    f"stderr: {stderr}"
                )
        else:
            rmdir(file_location.directory)

    def _run_on_precise_server(self, command):
        ssh_cmd = f"ssh -p {self.precise_ssh_port} precise@{self.precise_server} "
        ssh_cmd += command
        try:
            result = run(shlex.split(ssh_cmd), check=True, capture_output=True)
            stdout = result.stdout
            stderr = result.stderr
            success = True
        except CalledProcessError as cpe:
            stdout = cpe.stdout
            stderr = cpe.stderr
            success = False

        return success, stdout.decode(), stderr.decode()


if __name__ == "__main__":
    WakeWordFileRemover().run()
