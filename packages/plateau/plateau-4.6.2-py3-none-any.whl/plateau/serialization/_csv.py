#!/usr/bin/env python
"""This module contains functionality for persisting/serialising DataFrames."""

import gzip
from collections.abc import Iterable
from io import BufferedIOBase, BytesIO, StringIO
from typing import Any

import pandas as pd
import pyarrow as pa
from minimalkv import KeyValueStore
from pandas.errors import EmptyDataError

from ._generic import (
    DataFrameSerializer,
    PredicatesType,
    check_predicates,
    filter_df,
    filter_df_from_predicates,
)


class CsvSerializer(DataFrameSerializer):
    def __init__(self, compress=True):
        self.compress = compress

    def __eq__(self, other):
        return isinstance(other, CsvSerializer) and (self.compress == other.compress)

    def __repr__(self):
        return f"CsvSerializer(compress={self.compress!r})"

    @staticmethod
    def restore_dataframe(
        store: KeyValueStore,
        key: str,
        filter_query: str | None = None,
        columns: Iterable[str] | None = None,
        predicate_pushdown_to_io: Any = None,
        categories: Iterable[str] | None = None,
        predicates: PredicatesType | None = None,
        date_as_object: Any = None,
        **kwargs,
    ):
        check_predicates(predicates)
        compression: str | None
        if key.endswith(".csv.gz"):
            compression = "gzip"
        elif key.endswith(".csv"):
            compression = None

        if (not columns) and (columns is not None):
            # pd.read_csv does not seem to support proper reads w/o columns (it returns a DF w/o any row)
            columns = None
            project_to_no_cols = True
        else:
            project_to_no_cols = False

        dtype: dict[str, str] | None
        if categories:
            dtype = dict.fromkeys(categories, "category")
        else:
            dtype = None

        try:
            df = pd.read_csv(
                BytesIO(store.get(key)),
                compression=compression,
                sep=";",
                encoding="utf-8",
                usecols=columns,
                dtype=dtype,
            )
            if project_to_no_cols:
                df = df[[]]
            if len(df) == 0:
                # in that case, Pandas decided to use a weird index type, let's fix that
                df.index = pd.RangeIndex(start=0, stop=0, step=1)
        except EmptyDataError:
            df = pd.DataFrame()

        if predicates:
            return filter_df_from_predicates(df, predicates)
        else:
            return filter_df(df, filter_query)

    def store(self, store, key_prefix, df):
        if isinstance(df, pa.Table):
            # Prior to pyarrow 13.0.0 coerce_temporal_nanoseconds didn't exist
            # as it was introduced for backwards compatibility with pandas 1.x
            _coerce = {"coerce_temporal_nanoseconds": True}
            df = df.to_pandas(**_coerce)

        key = f"{key_prefix}.csv"
        result_stream = BytesIO()
        iostream: BufferedIOBase
        if self.compress:
            iostream = gzip.GzipFile(fileobj=result_stream, mode="wb")
            key += ".gz"
        else:
            iostream = result_stream

        # It seems that df.to_csv always writes default str, and thus
        # needs a StringIO in and a BytesIO in Python 2.
        # if someone finds a neat solution to do this in a compatible way,
        # please go ahead:

        unicode_stream = StringIO()
        if "0.23" <= pd.__version__ < "0.24":
            unicode_stream.write(df.to_csv(index=False, sep=";"))
        else:
            df.to_csv(unicode_stream, index=False, sep=";")
        iostream.write(unicode_stream.getvalue().encode("utf-8"))

        if self.compress:
            iostream.close()
        store.put(key, result_stream.getvalue())
        return key
