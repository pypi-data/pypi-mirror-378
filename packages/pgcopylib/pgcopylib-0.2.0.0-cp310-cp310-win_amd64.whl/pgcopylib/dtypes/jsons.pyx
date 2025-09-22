from json import (
    dumps,
    loads,
)


cpdef object read_json(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack json value."""

    return loads(binary_data)


cpdef bytes write_json(dtype_value, object array_function, object buffer, long pgoid):
    """Pack json value."""

    return dumps(dtype_value, ensure_ascii=False).encode("utf-8")
