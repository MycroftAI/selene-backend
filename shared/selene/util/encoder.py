import dataclasses
import re

from flask import make_response, json
from flask.json import JSONEncoder

snake_pattern = re.compile(r'_([a-z])')


class DataClassJsonEncoder(JSONEncoder):
    """Json Encoder to deal with python data classes"""
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return JSONEncoder.default(self, o)


def snake_to_camel(name):
    """Converts a string from snake case to camel case"""
    return snake_pattern.sub(lambda x: x.group(1).upper(), name)


def serialize(obj):
    """Serialize a possible complex object trying to convert its keys from snake case to camel case"""
    if hasattr(obj, '__dict__'):
        return {snake_to_camel(k): serialize(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, dict):
        return {snake_to_camel(k): serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    else:
        return obj


def output_json(data, code, headers=None):
    """Renders a response using the custom JsonDecoder and pre-converting from snake case to camel case"""
    resp = make_response(json.dumps(serialize(data), cls=DataClassJsonEncoder), code)
    resp.headers.extend(headers or {})
    return resp

