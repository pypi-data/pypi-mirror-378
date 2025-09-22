from cpython cimport PyBytes_AsString
from struct import (
    pack,
    unpack,
)


cdef bytes NULLABLE = b"\xff\xff\xff\xff"


cdef list recursive_elements(list elements, list array_struct):
    """Recursive unpack array struct."""

    cdef long chunk
    cdef long i
    cdef long elements_len = len(elements)

    if not array_struct:
        return elements

    chunk = array_struct.pop()

    if elements_len == chunk:
        return recursive_elements(elements, array_struct)
    
    cdef long num_chunks = (elements_len + chunk - 1) // chunk
    cdef list result = []
    cdef long start, end

    for i in range(num_chunks):
        start = i * chunk
        end = start + chunk

        if end > elements_len:
            end = elements_len
        result.append(elements[start:end])

    return recursive_elements(result, array_struct)


cdef list get_num_dim(object type_values):
    """Get list of num dim."""

    cdef list num_dim = []
    cdef object current = type_values

    while current.__class__ is list and len(current) > 0:
        num_dim.append(len(current))
        current = current[0]

    return num_dim


cdef long prod(list iterable):
    """Cython math.prod."""

    cdef long result, item

    for item in iterable:
        result *= item

    return result


cdef object _reader(object buffer, object array_function):
    """Read array record."""

    cdef bytes _bytes = buffer.read(4)
    cdef const unsigned char *buf = <const unsigned char*>PyBytes_AsString(_bytes)
    cdef int length = (buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]

    if length == 0xffffffff:
        return

    return array_function(buffer.read(length), None, None)


cpdef list read_array(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack array values."""

    buffer.write(binary_data)
    buffer.seek(0)

    cdef unsigned int num_dim, _, oid
    num_dim, _, oid = unpack("!3I", buffer.read(12))
    cdef list array_struct = []
    cdef list array_elements = []

    for _ in range(num_dim):
        array_struct.append(unpack("!2I", buffer.read(8))[0])

    for _ in range(prod(array_struct)):
        array_elements.append(_reader(buffer, array_function))

    buffer.seek(0)
    buffer.truncate()
    return recursive_elements(array_elements, array_struct)


def write_array(list dtype_value, object array_function, object buffer, long pgoid):
    """Pack array values."""

    cdef list num_dim = get_num_dim(dtype_value)
    cdef short dim_length = len(num_dim)
    cdef list expand_values
    cdef object value

    while any(isinstance(value, list) for value in dtype_value):
        expand_values = []
        for value in dtype_value:
            if isinstance(value, list):
                expand_values.extend(value)
            else:
                expand_values.append(value)
        dtype_value = expand_values

    cdef short is_nullable = None in dtype_value
    cdef list dimensions = []
    cdef short dim

    for dim in num_dim:
        dimensions.extend([dim, 1])

    cdef short length_dimensions = len(dimensions)

    buffer.write(pack("!3I", dim_length, is_nullable, pgoid))
    buffer.write(pack(f"!{length_dimensions}I", *dimensions))

    for value in dtype_value:
        if value is None:
            buffer.write(NULLABLE)
        else:
            buffer.write(array_function(value, None, None))

    cdef bytes binary_data = buffer.getvalue()
    buffer.seek(0)
    buffer.truncate()
    return binary_data
