from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Timezone(object):
    id: str
    dst_offset: Decimal
    gmt_offset: Decimal
    name: str
