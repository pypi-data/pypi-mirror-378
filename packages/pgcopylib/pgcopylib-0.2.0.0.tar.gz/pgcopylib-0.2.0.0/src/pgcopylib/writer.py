from io import (
    BytesIO,
    BufferedWriter,
)
from typing import (
    Any,
    Generator,
    TYPE_CHECKING,
)

from .dtypes import AssociateDtypes
from .enums import (
    ArrayOidToOid,
    PGOid,
    PGOidToDType,
)
from .errors import PGCopyRecordError
from .common import (
    make_rows,
    nullable_writer,
    writer,
)

if TYPE_CHECKING:
    from types import FunctionType


class PGCopyWriter:
    """PGCopy dump writer."""

    def __init__(
        self,
        file: BufferedWriter | None,
        pgtypes: list[PGOid],
    ) -> None:
        """Class initialization."""

        if not pgtypes:
            raise PGCopyRecordError("PGOids not defined!")

        self.file = file
        self.pgtypes = pgtypes
        self.num_columns = len(pgtypes)
        self.num_rows = 0
        self.pos = 0
        self.write_functions: list[FunctionType] = [
            AssociateDtypes[PGOidToDType[pgtype]].write
            for pgtype in pgtypes
        ]
        self.array_functions: list[FunctionType] = [
            AssociateDtypes[
                PGOidToDType[ArrayOidToOid[self.pgtypes[column]]]
            ].read
            if self.pgtypes and ArrayOidToOid.get(
                self.pgtypes[column]
            ) else None
            for column in range(self.num_columns)
        ]
        self.pgoid: list[int] = [
            ArrayOidToOid[self.pgtypes[column]].value
            if self.pgtypes and ArrayOidToOid.get(
                self.pgtypes[column]
            ) else 0
            for column in range(self.num_columns)
        ]
        self.buffer = BytesIO()

    def write_row(self, dtype_values: Any) -> Generator[Any, None, None]:
        """Write single row."""

        for write_dtype, dtype_value, array_function, pgoid in zip(
            self.write_functions,
            dtype_values,
            self.array_functions,
            self.pgoid,
        ):
            yield nullable_writer(
                write_dtype,
                dtype_value,
                array_function,
                self.buffer,
                pgoid,
            )
        self.num_rows += 1

    def from_rows(self, dtype_values: list[Any]) -> Generator[
        bytes,
        None,
        None,
    ]:
        """Write all rows."""

        return make_rows(self.write_row, dtype_values, self.num_columns)

    def write(self, dtype_values: list[Any]) -> None:
        """Write all rows into file."""

        if self.file is None:
            raise PGCopyRecordError("File not defined!")

        self.pos = writer(
            self.file,
            self.write_row,
            dtype_values,
            self.num_columns,
        )

    def tell(self) -> int:
        """Return current position."""

        return self.pos

    def __repr__(self) -> str:
        """PGCopy info in interpreter."""

        return self.__str__()

    def __str__(self) -> str:
        """PGCopy info."""

        return f"""PGCopy dump writer
Total columns: {self.num_columns}
Total rows: {self.num_rows}
Postgres types: {
    [pgtype.name for pgtype in self.pgtypes] or
    ["bytea" for _ in self.write_functions]
}
"""
