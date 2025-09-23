from datetime import datetime
from typing import TYPE_CHECKING

from spiral.core.table import Table as CoreTable
from spiral.core.table.spec import Schema
from spiral.expressions.base import Expr, ExprLike
from spiral.settings import settings
from spiral.snapshot import Snapshot
from spiral.transaction import Transaction

if TYPE_CHECKING:
    import duckdb
    import polars as pl
    import pyarrow.dataset as ds
    import streaming
    import torch.utils.data as torchdata  # noqa

    from spiral.client import Spiral
    from spiral.key_space_index import KeySpaceIndex


class Table(Expr):
    """API for interacting with a SpiralDB's Table.

    Spiral Table is a powerful and flexible way for storing, analyzing,
    and querying massive and/or multimodal datasets. The data model will feel familiar
    to users of SQL- or DataFrame-style systems, yet is designed to be more flexible, more powerful,
    and more useful in the context of modern data processing.

    Tables are stored and queried directly from object storage.
    """

    def __init__(self, spiral: "Spiral", core: CoreTable, *, identifier: str | None = None):
        super().__init__(core.__expr__)

        self.spiral = spiral
        self.core = core

        self._key_schema = core.key_schema
        self._key_columns = set(self._key_schema.names)
        self._identifier = identifier

    @property
    def table_id(self) -> str:
        return self.core.id

    @property
    def identifier(self) -> str:
        """Returns the fully qualified identifier of the table."""
        return self._identifier or self.table_id

    @property
    def dataset(self) -> str | None:
        """Returns the dataset of the table."""
        if self._identifier is None:
            return None
        _, dataset, _ = self._identifier.split(".")
        return dataset

    @property
    def name(self) -> str | None:
        """Returns the name of the table."""
        if self._identifier is None:
            return None
        _, _, name = self._identifier.split(".")
        return name

    def last_modified_at(self) -> int:
        return self.core.get_wal(asof=None).last_modified_at

    def __str__(self):
        return self.identifier

    def __repr__(self):
        return f'Table("{self.identifier}")'

    def __getitem__(self, item: str) -> Expr:
        return super().__getitem__(item)

    def select(self, *paths: str, exclude: list[str] = None) -> "Expr":
        return super().select(*paths, exclude=exclude)

    @property
    def key_schema(self) -> Schema:
        """Returns the key schema of the table."""
        return self._key_schema

    def schema(self) -> Schema:
        """Returns the FULL schema of the table.

        NOTE: This can be expensive for large tables.
        """
        return self.core.get_schema(asof=None)

    def write(
        self,
        expr: ExprLike,
        *,
        partition_size_bytes: int | None = None,
    ) -> None:
        """Write an item to the table inside a single transaction.

        :param expr: The expression to write. Must evaluate to a struct array.
        :param partition_size_bytes: The maximum partition size in bytes.
        """
        with self.txn() as txn:
            txn.write(
                expr,
                partition_size_bytes=partition_size_bytes,
            )

    def snapshot(self, asof: datetime | int | None = None) -> Snapshot:
        """Returns a snapshot of the table at the given timestamp."""
        if isinstance(asof, datetime):
            asof = int(asof.timestamp() * 1_000_000)
        return Snapshot(self, self.core.get_snapshot(asof=asof))

    def txn(self) -> Transaction:
        """Begins a new transaction. Transaction must be committed for writes to become visible.

        IMPORTANT: While transaction can be used to atomically write data to the table,
             it is important that the primary key columns are unique within the transaction.
        """
        return Transaction(self.spiral._core.transaction(self.core, settings().file_format))

    def to_dataset(self) -> "ds.Dataset":
        """Returns a PyArrow Dataset representing the table."""
        return self.snapshot().to_dataset()

    def to_polars(self) -> "pl.LazyFrame":
        """Returns a Polars LazyFrame for the Spiral table."""
        return self.snapshot().to_polars()

    def to_duckdb(self) -> "duckdb.DuckDBPyRelation":
        """Returns a DuckDB relation for the Spiral table."""
        return self.snapshot().to_duckdb()

    def to_data_loader(self, *, index: "KeySpaceIndex", **kwargs) -> "torchdata.DataLoader":
        """Returns a PyTorch DataLoader.

        Requires `torch` and `streaming` package to be installed.

        Args:
            index: See `streaming` method.
            **kwargs: Additional arguments passed to the PyTorch DataLoader constructor.

        """
        from streaming import StreamingDataLoader

        dataset_kwargs = {}
        if "batch_size" in kwargs:
            # Keep it in kwargs for DataLoader
            dataset_kwargs["batch_size"] = kwargs["batch_size"]
        if "cache_limit" in kwargs:
            dataset_kwargs["cache_limit"] = kwargs.pop("cache_limit")
        if "sampling_method" in kwargs:
            dataset_kwargs["sampling_method"] = kwargs.pop("sampling_method")
        if "sampling_granularity" in kwargs:
            dataset_kwargs["sampling_granularity"] = kwargs.pop("sampling_granularity")
        if "partition_algo" in kwargs:
            dataset_kwargs["partition_algo"] = kwargs.pop("partition_algo")
        if "num_canonical_nodes" in kwargs:
            dataset_kwargs["num_canonical_nodes"] = kwargs.pop("num_canonical_nodes")
        if "shuffle" in kwargs:
            dataset_kwargs["shuffle"] = kwargs.pop("shuffle")
        if "shuffle_algo" in kwargs:
            dataset_kwargs["shuffle_algo"] = kwargs.pop("shuffle_algo")
        if "shuffle_seed" in kwargs:
            dataset_kwargs["shuffle_seed"] = kwargs.pop("shuffle_seed")
        if "shuffle_block_size" in kwargs:
            dataset_kwargs["shuffle_block_size"] = kwargs.pop("shuffle_block_size")
        if "batching_method" in kwargs:
            dataset_kwargs["batching_method"] = kwargs.pop("batching_method")
        if "replication" in kwargs:
            dataset_kwargs["replication"] = kwargs.pop("replication")

        dataset = self.to_streaming_dataset(index=index, **dataset_kwargs)

        return StreamingDataLoader(dataset=dataset, **kwargs)

    def to_streaming_dataset(
        self,
        *,
        index: "KeySpaceIndex",
        batch_size: int | None = None,
        cache_limit: int | str | None = None,
        sampling_method: str = "balanced",
        sampling_granularity: int = 1,
        partition_algo: str = "relaxed",
        num_canonical_nodes: int | None = None,
        shuffle: bool = False,
        shuffle_algo: str = "py1e",
        shuffle_seed: int = 9176,
        shuffle_block_size: int | None = None,
        batching_method: str = "random",
        replication: int | None = None,
    ) -> "streaming.StreamingDataset":
        """Returns a MosaicML's StreamingDataset that can be used for distributed training.

        Requires `streaming` package to be installed.

        Args:
            See `streaming` method for `index` arg.
            See MosaicML's `StreamingDataset` for other args.

        This is a helper method to construct a single stream dataset from the scan. When multiple streams are combined,
        use `to_stream` to get the SpiralStream and construct the StreamingDataset manually using a `streams` arg.
        """
        from streaming import StreamingDataset

        stream = self.to_streaming(index=index)

        return StreamingDataset(
            streams=[stream],
            batch_size=batch_size,
            cache_limit=cache_limit,
            sampling_method=sampling_method,
            sampling_granularity=sampling_granularity,
            partition_algo=partition_algo,
            num_canonical_nodes=num_canonical_nodes,
            shuffle=shuffle,
            shuffle_algo=shuffle_algo,
            shuffle_seed=shuffle_seed,
            shuffle_block_size=shuffle_block_size,
            batching_method=batching_method,
            replication=replication,
        )

    def to_streaming(self, index: "KeySpaceIndex") -> "streaming.Stream":
        """Returns a stream to be used with MosaicML's StreamingDataset.

        Requires `streaming` package to be installed.

        Args:
            index: Prebuilt KeysIndex to use when creating the stream. The index's `asof` will be used when scanning.
        """
        from spiral.streaming_ import SpiralStream

        if index.table_id != self.table_id:
            raise ValueError("Index must be built on the same table as the scan.")
        if index.asof == 0:
            raise ValueError("Index have to be synced before it can be used in a stream.")

        # We know table from projection is in the session cause this method is on it.
        scan = self.spiral.scan(
            index.projection,
            where=index.filter,
            asof=index.asof,
            # TODO(marko): This should be configurable?
            exclude_keys=True,
        )

        # TODO(marko): This should happen in prepare_shards in Stream?
        #   We have a world there and can compute shards only on leader.
        shards = self.spiral._core._ops().compute_shards(index=index.core)

        return SpiralStream(scan=scan.core, shards=shards)  # type: ignore[return-value]
