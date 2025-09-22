from uuid import UUID


cpdef object read_uuid(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack uuid value."""

    return UUID(bytes=binary_data)


cpdef bytes write_uuid(object dtype_value, object array_function, object buffer, long pgoid):
    """Pack uuid value."""

    return dtype_value.bytes
