"""Convert between bytes and data types functions."""

from typing import NamedTuple
from types import FunctionType

from ..enums import PGDataType

from .arrays import (
    read_array,
    write_array,
)
from .dates import (
    read_date,
    read_interval,
    read_time,
    read_timestamp,
    read_timestamptz,
    read_timetz,
    write_date,
    write_interval,
    write_time,
    write_timestamp,
    write_timestamptz,
    write_timetz,
)
from .digits import (
    read_bool,
    read_float4,
    read_float8,
    read_int2,
    read_int4,
    read_int8,
    read_money,
    read_numeric,
    read_oid,
    read_serial2,
    read_serial4,
    read_serial8,
    write_bool,
    write_float4,
    write_float8,
    write_int2,
    write_int4,
    write_int8,
    write_money,
    write_numeric,
    write_oid,
    write_serial2,
    write_serial4,
    write_serial8,
)
from .geometrics import (
    read_box,
    read_line,
    read_lseg,
    read_path,
    read_point,
    read_polygon,
    write_box,
    write_line,
    write_lseg,
    write_path,
    write_point,
    write_polygon,
)
from .ipaddrs import (
    read_network,
    write_network,
)
from .jsons import (
    read_json,
    write_json,
)
from .strings import (
    read_bits,
    read_bytea,
    read_macaddr,
    read_text,
    write_bits,
    write_bytea,
    write_macaddr,
    write_text,
)
from .uuids import (
    read_uuid,
    write_uuid,
)


__all__ = (
    "AssociateDtypes",
)


class DTypeFunc(NamedTuple):
    """Class for associate read and write functions."""

    read: FunctionType
    write: FunctionType


AssociateDtypes: dict[PGDataType, DTypeFunc] = {
    PGDataType.Array: DTypeFunc(read_array, write_array),
    PGDataType.Bit: DTypeFunc(read_bits, write_bits),
    PGDataType.Bool: DTypeFunc(read_bool, write_bool),
    PGDataType.Box: DTypeFunc(read_box, write_box),
    PGDataType.Bytes: DTypeFunc(read_bytea, write_bytea),
    PGDataType.Cidr: DTypeFunc(read_network, write_network),
    PGDataType.Circle: DTypeFunc(read_line, write_line),
    PGDataType.Date: DTypeFunc(read_date, write_date),
    PGDataType.Float4: DTypeFunc(read_float4, write_float4),
    PGDataType.Float8: DTypeFunc(read_float8, write_float8),
    PGDataType.Inet: DTypeFunc(read_network, write_network),
    PGDataType.Int2: DTypeFunc(read_int2, write_int2),
    PGDataType.Int4: DTypeFunc(read_int4, write_int4),
    PGDataType.Int8: DTypeFunc(read_int8, write_int8),
    PGDataType.Interval: DTypeFunc(read_interval, write_interval),
    PGDataType.Json: DTypeFunc(read_json, write_json),
    PGDataType.Line: DTypeFunc(read_line, write_line),
    PGDataType.Lseg: DTypeFunc(read_lseg, write_lseg),
    PGDataType.Macaddr8: DTypeFunc(read_macaddr, write_macaddr),
    PGDataType.Macaddr: DTypeFunc(read_macaddr, write_macaddr),
    PGDataType.Money: DTypeFunc(read_money, write_money),
    PGDataType.Numeric: DTypeFunc(read_numeric, write_numeric),
    PGDataType.Oid: DTypeFunc(read_oid, write_oid),
    PGDataType.Path: DTypeFunc(read_path, write_path),
    PGDataType.Point: DTypeFunc(read_point, write_point),
    PGDataType.Polygon: DTypeFunc(read_polygon, write_polygon),
    PGDataType.Serial2: DTypeFunc(read_serial2, write_serial2),
    PGDataType.Serial4: DTypeFunc(read_serial4, write_serial4),
    PGDataType.Serial8: DTypeFunc(read_serial8, write_serial8),
    PGDataType.Text: DTypeFunc(read_text, write_text),
    PGDataType.Time: DTypeFunc(read_time, write_time),
    PGDataType.Timestamp: DTypeFunc(read_timestamp, write_timestamp),
    PGDataType.Timestamptz: DTypeFunc(read_timestamptz, write_timestamptz),
    PGDataType.Timetz: DTypeFunc(read_timetz, write_timetz),
    PGDataType.Uuid: DTypeFunc(read_uuid, write_uuid),
}
