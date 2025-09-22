cpdef str read_text(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack text value."""

    return binary_data.decode("utf-8", errors="replace")


cpdef bytes write_text(str dtype_value, object array_function, object buffer, long pgoid):
    """Pack text value."""

    return dtype_value.encode("utf-8")


cpdef str read_macaddr(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack macaddr and macaddr8 value."""

    cdef Py_ssize_t i
    cdef Py_ssize_t data_len = len(binary_data)
    cdef const unsigned char[:] view = binary_data
    cdef list parts = []

    parts.reserve(data_len)

    for i in range(data_len):
        parts.append(f"{view[i]:02x}")

    return ":".join(parts).upper()


cpdef bytes write_macaddr(str dtype_value, object array_function, object buffer, long pgoid):
    """Pack macaddr and macaddr8 value."""

    return bytes.fromhex(dtype_value.replace(":", ""))


cpdef str read_bits(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack bit and varbit value."""

    cdef unsigned int length
    cdef const unsigned char[:] view = binary_data
    cdef Py_ssize_t data_len = len(binary_data)
    cdef Py_ssize_t bit_data_len = data_len - 4
    cdef list bits = []
    cdef Py_ssize_t i, j
    cdef unsigned char byte_val

    length = (view[0] << 24) | (view[1] << 16) | (view[2] << 8) | view[3]
    bits.reserve(bit_data_len * 8)

    for i in range(4, data_len):
        byte_val = view[i]
        for j in range(7, -1, -1):
            bits.append(str((byte_val >> j) & 1))

    return "".join(bits)[:length]


cpdef bytes write_bits(str dtype_value, object array_function, object buffer, long pgoid):
    """Pack bit and varbit value."""
    
    cdef Py_ssize_t bit_length = len(dtype_value)
    cdef Py_ssize_t byte_length = (bit_length + 7) // 8
    cdef int int_value = int(dtype_value, 2)
    
    return int_value.to_bytes(byte_length, "big")


cpdef bytes read_bytea(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack bytea value."""

    return binary_data


cpdef bytes write_bytea(bytes dtype_value, object array_function, object buffer, long pgoid):
    """Pack bytea value."""

    return dtype_value
