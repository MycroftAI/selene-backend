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

"""
This is used to support pipenv installing the shared code to the virtual
environments used in developement of Selene APIs and services.
"""
from setuptools import setup, find_packages

setup(
    name='selene',
    version='0.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'facebook-sdk',
        'flask',
        'passlib',
        'pygithub',
        'pyhamcrest',
        'pyjwt',
        'psycopg2-binary',
        'redis',
        'sendgrid',
        'schematics',
        'stripe',
        'schedule'
    ]
)
