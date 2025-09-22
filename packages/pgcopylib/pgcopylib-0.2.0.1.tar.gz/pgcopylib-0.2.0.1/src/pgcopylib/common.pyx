from cpython cimport PyBytes_AsString
from struct import pack


cdef bytes HEADER = b"PGCOPY\n\xff\r\n\x00\x00\x00\x00\x00\x00\x00\x00\x00"
cdef bytes FINALIZE = b"\xff\xff"
cdef bytes NULLABLE = b"\xff\xff\xff\xff"


cpdef int read_num_columns(object file, int column_length):
    """Read one record to bytes."""

    cdef bytes _bytes = file.read(column_length)
    cdef const unsigned char *buf = <const unsigned char*>PyBytes_AsString(_bytes)
    return (buf[0] << 8) | buf[1]


cpdef object read_record(object file, object reader, object array_function, object buffer, long pgoid):
    """Read one record to bytes."""

    cdef bytes _bytes = file.read(4)
    cdef const unsigned char *buf = <const unsigned char*>PyBytes_AsString(_bytes)
    cdef int length = (buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]

    if length == 0xffffffff:
        return

    return reader(file.read(length), array_function, buffer, pgoid)


cpdef int skip_all(object file, int column_length, int num_columns, int num_rows):
    """Skip all records."""

    cdef int columns = num_columns

    while columns != 0xffff:

        for _ in range(num_columns):
            skip_record(file)

        num_rows += 1
        columns = read_num_columns(file, column_length)

    return num_rows


cdef skip_record(object file):
    """Skip one record."""

    cdef bytes _bytes = file.read(4)
    cdef const unsigned char *buf = <const unsigned char*>PyBytes_AsString(_bytes)
    cdef int length = (buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]
    file.read(length)


def make_rows(object write_row, object dtype_values, int num_columns):
    """Make pgcopy rows."""

    cdef bytes num_columns_bytes = bytes([
        (num_columns >> 8) & 0xFF,
        num_columns & 0xFF
    ])

    yield HEADER

    for dtype_value in dtype_values:
        yield num_columns_bytes

        for row in write_row(dtype_value):
            yield row

    yield FINALIZE


cpdef int writer(object file, object write_row, object dtype_values, int num_columns):
    """Write pgcopy into file."""

    cdef int pos = 0

    for buffer in make_rows(write_row, dtype_values, num_columns):
        pos += file.write(buffer)

    return pos


cpdef bytes nullable_writer(object write_dtype, object dtype_value, object array_function, object buffer, long pgoid):
    """Function for write None value and data with length."""

    if dtype_value is None:
        return NULLABLE

    cdef bytes binary_data = write_dtype(dtype_value, array_function, buffer, pgoid)
    cdef int len_data = len(binary_data)
    return pack(f"!I{len_data}s", len_data, binary_data)
