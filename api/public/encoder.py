import dataclasses

from flask.json import JSONEncoder


class DataClassJsonEncoder(JSONEncoder):
    """Json Encoder to deal with python data classes"""
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return JSONEncoder.default(self, o)
