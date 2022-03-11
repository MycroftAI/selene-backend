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

from dataclasses import is_dataclass, asdict
import re

from flask import jsonify, Response

snake_pattern = re.compile(r"_([a-z])")


def snake_to_camel(name):
    """Converts a string from snake case to camel case"""
    return snake_pattern.sub(lambda x: x.group(1).upper(), name)


def coerce_response(response_data):
    """Coerce response data to JSON serializable object with camelCase keys

    Recursively walk through the response object in case there are things
    like nested dataclasses that need to be reformatted

    :param response_data: data returned from the API request
    :returns: the same data but with keys in camelCase
    """
    if is_dataclass(response_data):
        coerced = {
            snake_to_camel(key): coerce_response(value)
            for key, value in asdict(response_data).items()
        }
    elif isinstance(response_data, dict):
        coerced = {
            snake_to_camel(key): coerce_response(value)
            for key, value in response_data.items()
        }
    elif isinstance(response_data, list):
        coerced = [coerce_response(item) for item in response_data]
    else:
        coerced = response_data

    return coerced


class SeleneResponse(Response):
    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict) or isinstance(rv, list) or is_dataclass(rv):
            reformat = coerce_response(rv)
            rv = jsonify(reformat)
        return super(SeleneResponse, cls).force_type(rv, environ)
