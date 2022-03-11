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
"""Library for re-usable SFTP functions"""
from base64 import b64decode
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from struct import unpack
from typing import Tuple

from paramiko import AutoAddPolicy, RSAKey, SSHClient
from paramiko.auth_handler import AuthenticationException, SSHException

BIG_ENDIAN_UNSIGNED_INT = ">I"
INTEGER_BYTES = 4

_log = getLogger(__name__)


@dataclass()
class SshClientConfig:
    """Represents the configuration parameters needed to establish a SSH connection"""

    remote_server: str
    remote_user: str
    local_user: str
    ssh_port: int = 22
    ssh_key_directory: Path = None
    ssh_key_file_name: str = None

    def __post_init__(self):
        """Set defaults for the key file directory and name if they are not supplied."""
        if self.ssh_key_directory is None:
            self.ssh_key_directory = Path(f"/home/{self.local_user}/.ssh")
        if self.ssh_key_file_name is None:
            self.ssh_key_file_name = "id_rsa"


class SeleneSshClient:
    """Leverage the paramiko library to establish a connection over SSH."""

    _client = None

    def __init__(self, config: SshClientConfig):
        self.config = config
        self.ssh_key_file_path = self.config.ssh_key_directory.joinpath(
            self.config.ssh_key_file_name
        )
        self._check_ssh_key()

    def _check_ssh_key(self):
        """Fetch locally stored SSH key."""
        try:
            RSAKey.from_private_key_file(str(self.ssh_key_file_path))
            _log.info(f"Found valid SSH key at {self.ssh_key_file_path}")
        except SSHException:
            _log.exception(
                f"The file at {self.ssh_key_file_path} does not contain a valid ssh key"
            )

    @property
    def client(self):
        """Open connection to remote host."""
        if self._client is None:
            self._client = SSHClient()
            self._client.load_system_host_keys()
            self._client.set_missing_host_key_policy(AutoAddPolicy())

        return self._client

    def connect(self):
        """Establish an SSH connection to the remote server."""
        try:
            self.client.connect(
                self.config.remote_server,
                port=self.config.ssh_port,
                username=self.config.remote_user,
                key_filename=str(self.ssh_key_file_path),
                look_for_keys=True,
                timeout=5,
            )
        except AuthenticationException:
            _log.exception(
                f"SSH authentication failed for {self.config.remote_user}@"
                f"{self.config.remote_server} did you remember to put the SSH key "
                f"in the authorized_keys file?"
            )
            raise

    def disconnect(self):
        """Close ssh connection."""
        self.client.close()


def validate_rsa_public_key(public_key: str) -> bool:
    """Check the specified public key to determine if it is a well-formed RSA key.

    According to the the specification, the first part of the key is a length-prefixed
    string. The length is packed as a big-endian unsigned integer.  The expected value
    is 7 because the following string, 'ssh-rsa', is 7 bytes long.

    :param public_key: key to validate
    :return: boolean indicating if validation check passed.
    """
    is_valid = False
    key_type, key = _parse_public_key(public_key)
    if key_type is not None and key is not None:
        decoded_key = b64decode(key)
        try:
            unpack_result = unpack(BIG_ENDIAN_UNSIGNED_INT, decoded_key[:INTEGER_BYTES])
        except Exception:
            _log.exception("Failed to unpack first four bytes of public key")
        else:
            length_of_subsequent_string = unpack_result[0]
            if length_of_subsequent_string == 7:
                is_valid = decoded_key[4:11].decode() == key_type

    return is_valid


def _parse_public_key(public_key: str) -> Tuple[str, str]:
    """Assign the parts of the public key to variables.

    An RSA key can have a comment at the end of it or not.  Both ways are valid.

    :param public_key: key to validate
    :return: they key type (e.g. ssh-rsa) and the key value
    """
    key_type = None
    key = None
    public_key_parts = public_key.split()
    if len(public_key_parts) == 3:
        key_type, key, _ = public_key.split()
    elif len(public_key_parts) == 2:
        key_type, key = public_key.split()
    else:
        _log.error("Public key malformed")

    return key_type, key
