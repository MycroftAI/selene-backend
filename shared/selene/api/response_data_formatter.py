from dataclasses import is_dataclass, asdict
import re

from flask import make_response, json

JSON_MIMETYPE = 'application/json'


def snake_to_camel(name):
    """Converts a string from snake case to camel case"""
    snake_pattern = re.compile(r'_([a-z])')
    return snake_pattern.sub(lambda x: x.group(1).upper(), name)


def reformat_response(response_data):
    """Convert response to JSON serializable object with camelCase keys

    :param response_data: data returned from the API request
    :returns: the same data but with keys in camelCase
    """
    if is_dataclass(response_data):
        reformatted = {
            snake_to_camel(k): reformat_response(v)
            for k, v in asdict(response_data).items()
        }
    elif isinstance(response_data, dict):
        reformatted = {
            snake_to_camel(k): reformat_response(v)
            for k, v in response_data.items()
        }
    elif isinstance(response_data, list):
        reformatted = [reformat_response(item) for item in response_data]
    else:
        reformatted = response_data

    return reformatted


def output_json(data, code, headers=None):
    """Used to override the default JSON representation

    Our APIs mostly serve Typescript front-ends.  Typescript uses camelCase
    instead of snake_case.  To address this, use reformat_response() to convert
    all the keys to camelCase.

    :param data: object representing the data to convert to JSON
    :param code: HTTP response code
    :param headers: any headers to add to what was already there.
    :returns: a API response object
    """
    response = make_response(json.dumps(reformat_response(data)), code)
    response.headers.extend(headers or {})

    return response
