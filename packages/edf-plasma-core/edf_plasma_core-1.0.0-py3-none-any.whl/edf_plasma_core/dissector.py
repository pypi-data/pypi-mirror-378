"""Generic Dissector Interface"""

from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from .concept import Tag
from .helper.datetime import datetime, to_iso_fmt, utc_now
from .helper.logging import get_logger
from .helper.perfmeter import PerformanceMeter
from .helper.table import (
    Column,
    ColumnList,
    DataType,
    Table,
)
from .helper.typing import (
    PathIterator,
    RecordIterator,
    StringList,
)

_LOGGER = get_logger('core.dissector')
_DISSECTORS = {}


@dataclass
class DissectionError:
    """A dissection error with a datetime and reason"""

    time: datetime
    reason: str


@dataclass
class DissectionContext:
    """Dissection context"""

    dissector: str
    hostname: str
    source: str
    filepath: Path
    errors: list[DissectionError] = field(default_factory=list)

    def register_error(self, reason: str):
        """Register and log an error"""
        _LOGGER.error("dissection error: %s", reason)
        self.errors.append(DissectionError(time=utc_now(), reason=reason))

    def errors_as_records(self) -> RecordIterator:
        """Generare records for errors"""
        for error in self.errors:
            yield {
                '_dissector': self.dissector,
                '_hostname': self.hostname,
                '_source': self.source,
                '_time': to_iso_fmt(error.time),
                '_reason': error.reason,
            }


DissectionContextList = list[DissectionContext]


@dataclass
class Dissector:
    """Dissector"""

    slug: str
    tags: set[Tag]
    columns: ColumnList
    description: str
    select_impl: Callable[[Path], PathIterator]
    dissect_impl: Callable[[DissectionContext], RecordIterator]

    @property
    def table_schema(self) -> Table:
        """Dissector full table schema"""
        standard_columns = [
            Column('_hostname', DataType.STR),
            Column('_source', DataType.STR),
        ]
        return Table(standard_columns + self.columns)

    @property
    def error_table_schema(self) -> Table:
        """Dissection error table schema"""
        return Table(
            [
                Column('_dissector', DataType.STR),
                Column('_hostname', DataType.STR),
                Column('_source', DataType.STR),
                Column('_time', DataType.STR),
                Column('_reason', DataType.STR),
            ]
        )

    def select(self, directory: Path) -> PathIterator:
        """Artifact selector"""
        for filepath in self.select_impl(directory):
            _LOGGER.info(
                "file selected: %s (filepath=%s)", self.slug, filepath
            )
            yield filepath

    def dissect(self, ctx: DissectionContext) -> RecordIterator:
        """Yield records from dissection context processing"""
        _LOGGER.info(
            "dissection start: %s (filepath=%s)", self.slug, ctx.filepath
        )
        perfmeter = PerformanceMeter()
        with perfmeter:
            for record_data in self.dissect_impl(ctx):
                record = {
                    '_hostname': ctx.hostname,
                    '_source': ctx.source,
                }
                record.update(record_data)
                perfmeter.tick()
                yield record
        _LOGGER.info(
            "dissection complete: %s (records=%d, errors=%d, time=%s)",
            self.slug,
            perfmeter.count,
            len(ctx.errors),
            perfmeter.elapsed,
        )

    def dissect_many(self, ctx_list: DissectionContextList) -> RecordIterator:
        """Yield records from many dissection context"""
        _LOGGER.info(
            "dissect many start: %s (files=%d)",
            self.slug,
            len(ctx_list),
        )
        perfmeter = PerformanceMeter()
        with perfmeter:
            for ctx in ctx_list:
                try:
                    yield from self.dissect(ctx)
                except:
                    _LOGGER.exception("dissector exception: %s", self.slug)
                    ctx.register_error(
                        "dissector raised an unhandled exception, please create an issue!"
                    )
        _LOGGER.info(
            "dissection many complete: %s (files=%d, errors=%d, time=%s)",
            self.slug,
            len(ctx_list),
            sum(len(ctx.errors) for ctx in ctx_list),
            perfmeter.elapsed,
        )

    def process_errors(
        self, ctx_list: DissectionContextList
    ) -> RecordIterator:
        """Yield errors from context list"""
        for ctx in ctx_list:
            yield from ctx.errors_as_records()


DissectorList = list[Dissector]
DissectorMapping = dict[str, Dissector]
DissectorIterator = Iterator[Dissector]


def register_dissector(dissector: Dissector):
    """Register dissector"""
    if dissector.slug in _DISSECTORS:
        _LOGGER.warning("skipped duplicate dissector: %s", dissector.slug)
        return
    _LOGGER.debug("dissector registered: %s", dissector.slug)
    _DISSECTORS[dissector.slug] = dissector


def get_dissector(slug: str) -> Dissector:
    """Retrieve dissector matching given slug"""
    return _DISSECTORS[slug]


def get_dissector_or_none(slug: str) -> Dissector | None:
    """Retrieve dissector matching given slug"""
    return _DISSECTORS.get(slug)


def get_dissectors() -> DissectorList:
    """Iterate dissectors"""
    return list(_DISSECTORS.values())


def get_dissector_slugs() -> StringList:
    """List dissector slugs"""
    return list(_DISSECTORS.keys())
