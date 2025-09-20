"""Windows AppX artifact dissector"""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

from edf_plasma_core.concept import Tag
from edf_plasma_core.dissector import (
    DissectionContext,
    Dissector,
    register_dissector,
)
from edf_plasma_core.helper.datetime import to_iso_fmt, with_utc
from edf_plasma_core.helper.glob import ci_glob_pattern
from edf_plasma_core.helper.logging import get_logger
from edf_plasma_core.helper.table import Column, DataType
from edf_plasma_core.helper.typing import PathIterator, RecordIterator
from edf_plasma_core.helper.xml import check_xml_parser_safety

from .xml import AppXManifest

_LOGGER = get_logger('dissectors.microsoft.appx')
_PATTERN = ci_glob_pattern('AppXManifest.xml')


def _select_impl(directory: Path) -> PathIterator:
    if not check_xml_parser_safety():
        _LOGGER.error("XML parser is not safe!")
        return
    for filepath in directory.rglob(_PATTERN):
        if not filepath.is_file():
            continue
        yield filepath


def _dissect_impl(ctx: DissectionContext) -> RecordIterator:
    appx_manifest = AppXManifest.from_filepath(ctx.filepath)
    _LOGGER.warning(
        "appx_manifest.identity.        name: %s", appx_manifest.identity.name
    )
    _LOGGER.warning(
        "appx_manifest.identity.   publisher: %s",
        appx_manifest.identity.publisher,
    )
    _LOGGER.warning(
        "appx_manifest.identity.     version: %s",
        appx_manifest.identity.version,
    )
    _LOGGER.warning(
        "appx_manifest.identity.architecture: %s",
        appx_manifest.identity.architecture,
    )
    yield {
        'todo': '',
    }


DISSECTOR = Dissector(
    slug='windows_appx',
    tags={Tag.WINDOWS},
    columns=[
        Column('todo', DataType.STR),
    ],
    description="AppX manifest files",
    select_impl=_select_impl,
    dissect_impl=_dissect_impl,
)
register_dissector(DISSECTOR)
