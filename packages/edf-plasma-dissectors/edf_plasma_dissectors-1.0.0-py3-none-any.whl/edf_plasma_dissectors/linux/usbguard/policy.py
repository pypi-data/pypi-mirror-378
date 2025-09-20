"""Usbguard Policy Dissector"""

from pathlib import Path

from edf_plasma_core.concept import Tag
from edf_plasma_core.dissector import (
    DissectionContext,
    Dissector,
    register_dissector,
)
from edf_plasma_core.helper.datetime import from_unix_timestamp, to_iso_fmt
from edf_plasma_core.helper.matching import regexp
from edf_plasma_core.helper.streaming import lines_from_filepath
from edf_plasma_core.helper.table import Column, DataType
from edf_plasma_core.helper.typing import PathIterator, RecordIterator

_GLOB_PATTERN = 'usbguard*.log*'
_PATTERN = regexp(
    r'\[(?P<timestamp>[\d\.]+)[^\(]+(?P<level>\(.\)) uid=(?P<uid>[\d]+) pid=(?P<pid>[\d]+) result=\'(?P<result>[^\']+)\' device\.system_name=\'(?P<devicename>[^\']+)\' target\.new=\'(?P<targetnew>[^\']+)\' device.rule=\'(?P<devicerule>[^\']+)\' target\.old=\'(?P<targetold>[^\']+)\' type=\'(?P<type>[^\']+).*'
)


def _select_impl(directory: Path) -> PathIterator:
    for filepath in directory.rglob(_GLOB_PATTERN):
        if not filepath.is_file():
            continue
        yield filepath


def _dissect_impl(ctx: DissectionContext) -> RecordIterator:
    for line in lines_from_filepath(ctx.filepath):
        line = line.rstrip()
        match = _PATTERN.search(line)
        if not match:
            continue
        usbguard_timestamp = float(match.group('timestamp'))
        usbguard_timestamp = from_unix_timestamp(
            usbguard_timestamp * 1000 * 1000
        )
        yield {
            'usbguard_timestamp': to_iso_fmt(usbguard_timestamp),
            'usbguard_level': match.group('level'),
            'usbguard_uid': match.group('uid'),
            'usbguard_pid': match.group('pid'),
            'usbguard_result': match.group('result'),
            'usbguard_devicename': match.group('devicename'),
            'usbguard_targetnew': match.group('targetnew'),
            'usbguard_devicerule': match.group('devicerule'),
            'usbguard_targetold': match.group('targetold'),
            'usbguard_type': match.group('type'),
        }


DISSECTOR = Dissector(
    slug='linux_usbguard_policy',
    tags={Tag.LINUX},
    columns=[
        Column('usbguard_timestamp', DataType.STR),
        Column('usbguard_level', DataType.STR),
        Column('usbguard_uid', DataType.INT),
        Column('usbguard_pid', DataType.INT),
        Column('usbguard_result', DataType.STR),
        Column('usbguard_devicename', DataType.STR),
        Column('usbguard_targetnew', DataType.STR),
        Column('usbguard_devicerule', DataType.STR),
        Column('usbguard_targetold', DataType.STR),
        Column('usbguard_type', DataType.STR),
    ],
    description="usbguard log (policy events)",
    select_impl=_select_impl,
    dissect_impl=_dissect_impl,
)
register_dissector(DISSECTOR)
