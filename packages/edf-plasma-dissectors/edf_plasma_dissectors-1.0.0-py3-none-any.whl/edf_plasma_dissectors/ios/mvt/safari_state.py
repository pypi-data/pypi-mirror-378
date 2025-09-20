"""MVT iOS Safari State artifact dissector"""

from pathlib import Path

from edf_plasma_core.concept import Tag
from edf_plasma_core.dissector import (
    DissectionContext,
    Dissector,
    register_dissector,
)
from edf_plasma_core.helper.filtering import unique
from edf_plasma_core.helper.json import read_json
from edf_plasma_core.helper.matching import iter_url_fqdn
from edf_plasma_core.helper.table import Column, DataType
from edf_plasma_core.helper.typing import PathIterator, RecordIterator


def _select_impl(directory: Path) -> PathIterator:
    for filepath in directory.rglob('safari_browser_state.json'):
        if not filepath.is_file():
            continue
        yield filepath


def _dissect_impl(ctx: DissectionContext) -> RecordIterator:
    records = read_json(ctx.filepath)
    if records is None:
        ctx.register_error(f"failed to load JSON data from: {ctx.filepath}")
        return
    for record in records:
        if not isinstance(record, dict):
            ctx.register_error(f"unsupported format: {ctx.filepath}")
            return
        for entry in record['session_data']:
            for fqdn in unique(iter_url_fqdn(entry['entry_url'])):
                yield {
                    'time': record['last_viewed_timestamp'],
                    'fqdn': fqdn,
                }


DISSECTOR = Dissector(
    slug='ios_mvt_safari_state',
    tags={Tag.MVT, Tag.IOS},
    columns=[
        Column('time', DataType.STR),
        Column('fqdn', DataType.STR),
    ],
    description="MVT iOS safari state output",
    select_impl=_select_impl,
    dissect_impl=_dissect_impl,
)
register_dissector(DISSECTOR)
