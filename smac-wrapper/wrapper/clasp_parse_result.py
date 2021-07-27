import json
import re
import sys
from dataclasses import dataclass
from typing import Callable


@dataclass
class ClaspResult:
    status: str
    running_time: int
    quality: int
    json: any


def clasp_parse_result(clasp_json_result: str, quality_fn: Callable = lambda x: 0.) -> ClaspResult:
    try:
        output_json = json.loads(clasp_json_result)
    except Exception as e:
        raise ClaspParseError(e)

    return ClaspResult(
        status=output_json['Result'],
        running_time=float(output_json['Time']['Total']),
        quality=float(quality_fn(output_json)),
        json=output_json
    )


class ClaspParseError(Exception):
    pass