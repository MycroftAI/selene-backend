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
from pathlib import Path

from paramiko import Transport, RSAKey
from paramiko.sftp_client import SFTPClient

from .ssh import SshClientConfig


def get_remote_file(ssh_config: SshClientConfig, local_path: Path, remote_path: Path):
    """Use SFTP to copy a file from a remote server to the local server.

    :param ssh_config: Configuration of the SSH session used for SFTP
    :param local_path: Destination path of the file being transferred
    :param remote_path: Source path of the file being transferred
    """
    ssh_transport = Transport((ssh_config.remote_server, int(ssh_config.ssh_port)))
    ssh_key = RSAKey.from_private_key_file("/home/mycroft/.ssh/id_rsa")
    ssh_transport.connect(hostkey=None, username=ssh_config.remote_user, pkey=ssh_key)
    sftp_client = SFTPClient.from_transport(ssh_transport)
    sftp_client.get(str(remote_path), str(local_path))
    sftp_client.close()
    ssh_transport.close()
