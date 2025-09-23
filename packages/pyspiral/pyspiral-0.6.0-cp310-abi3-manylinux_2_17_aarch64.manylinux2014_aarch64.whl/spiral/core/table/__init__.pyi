from typing import Any

import pyarrow as pa
from spiral.expressions import Expr

from .manifests import FragmentManifest
from .metastore import PyMetastore
from .spec import ColumnGroup, Key, Schema, WriteAheadLog

class KeyRange:
    """A right-exclusive range of keys."""

    def __init__(self, *, begin: Key, end: Key): ...

    begin: Key
    end: Key

    def union(self, other: KeyRange) -> KeyRange: ...
    def __or__(self, other: KeyRange) -> KeyRange: ...
    def intersection(self, key_extent: KeyRange) -> KeyRange | None: ...
    def __and__(self, other: KeyRange) -> KeyRange | None: ...
    def contains(self, item: Key) -> bool: ...
    def __contains__(self, item: Key) -> bool: ...
    def is_disjoint(self, key_range: KeyRange) -> bool:
        return self.end <= key_range.begin or self.begin >= key_range.end

    @staticmethod
    def beginning_with(begin: Key) -> KeyRange: ...
    @staticmethod
    def ending_with(end: Key) -> KeyRange: ...
    @staticmethod
    def full() -> KeyRange: ...

class Table:
    def __init__(self, metastore: PyMetastore): ...

    id: str
    root_uri: str
    mount_id: str | None
    key_schema: Schema
    metastore: PyMetastore

    def get_wal(self, *, asof: int | None) -> WriteAheadLog: ...
    def get_schema(self, *, asof: int | None) -> Schema: ...
    def get_snapshot(self, *, asof: int | None) -> Snapshot: ...

class Snapshot:
    """A snapshot of a table at a specific point in time."""

    asof: int
    table: Table
    wal: WriteAheadLog

class Scan:
    def key_schema(self) -> Schema: ...
    def schema(self) -> Schema: ...
    def is_empty(self) -> bool: ...
    def splits(self) -> list[KeyRange]: ...
    def table_ids(self) -> list[str]: ...
    def column_groups(self) -> list[ColumnGroup]: ...
    def column_group_state(self, column_group: ColumnGroup) -> ColumnGroupState: ...
    def key_space_state(self, table_id: str) -> KeySpaceState: ...
    def to_record_batches(
        self,
        key_table: pa.Table | pa.RecordBatch | None = None,
        batch_readahead: int | None = None,
    ) -> pa.RecordBatchReader: ...
    def to_shuffled_record_batches(
        self,
        strategy: ShuffleStrategy | None = None,
        batch_readahead: int | None = None,
    ) -> pa.RecordBatchReader: ...
    def metrics(self) -> dict[str, Any]: ...
    def _prepare_shard(
        self,
        output_path: str,
        key_range: KeyRange,
        expected_cardinality: int | None = None,
    ) -> None: ...

class KeySpaceState:
    manifest: FragmentManifest

    def key_schema(self) -> Schema: ...

class ColumnGroupState:
    manifest: FragmentManifest
    column_group: ColumnGroup

    def schema(self) -> Schema: ...

class Transaction:
    status: str

    def write(self, expr: Expr, *, partition_size_bytes: int | None = None): ...
    def commit(self): ...
    def abort(self): ...
    def metrics(self) -> dict[str, Any]: ...

class ShuffleStrategy:
    # Results are buffered in a pool of `buffer_size` rows and shuffled again.
    shuffle_buffer_size: int

    # All randomness is derived from this seed. If None, a random seed is generated from the OS.
    seed: int | None

    # `approximate_batch_size` controls the maximum approximate size of each shard. Shards that
    # are larger than this size are further split assuming uniform distribution of keys. Note
    # that this is a best-effort and can be widely off. The purpose of this is to improve
    # shuffling, rather than to support sharding. If not present, splits derived from the table
    # are used in the attempt to minimize wasted reads.
    approximate_buffer_size: int | None

    def __init__(
        self,
        seed: int | None = None,
        shard_size: int | None = None,
        buffer_size: int | None = None,
    ): ...
