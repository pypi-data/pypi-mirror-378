from decimal import Decimal, ROUND_HALF_UP
from libc.math cimport round
from struct import (
    pack,
    unpack,
    unpack_from,
)


cpdef object read_bool(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack bool value."""

    return unpack("!?", binary_data)[0]


cpdef bytes write_bool(object dtype_value, object array_function, object buffer, long pgoid):
    """Pack bool value."""

    return pack("!?", dtype_value)


cpdef unsigned int read_oid(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack oid value."""

    return unpack("!I", binary_data)[0]


cpdef bytes write_oid(unsigned int dtype_value, object array_function, object buffer, long pgoid):
    """Pack oid value."""

    return pack("!I", dtype_value)


cpdef unsigned short read_serial2(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack serial2 value."""

    return unpack("!H", binary_data)[0]


cpdef bytes write_serial2(unsigned short dtype_value, object array_function, object buffer, long pgoid):
    """Pack serial2 value."""

    return pack("!H", dtype_value)


cpdef unsigned long read_serial4(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack serial4 value."""

    return unpack("!L", binary_data)[0]


cpdef bytes write_serial4(unsigned long dtype_value, object array_function, object buffer, long pgoid):
    """Pack serial4 value."""

    return pack("!L", dtype_value)


cpdef unsigned long long read_serial8(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack serial8 value."""

    return unpack("!Q", binary_data)[0]


cpdef bytes write_serial8(unsigned long long dtype_value, object array_function, object buffer, long pgoid):
    """Pack serial8 value."""

    return pack("!Q", dtype_value)


cpdef short read_int2(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack int2 value."""

    return unpack("!h", binary_data)[0]


cpdef bytes write_int2(short dtype_value, object array_function, object buffer, long pgoid):
    """Pack int2 value."""

    return pack("!h", dtype_value)


cpdef long read_int4(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack int4 value."""

    return unpack("!l", binary_data)[0]


cpdef bytes write_int4(long dtype_value, object array_function, object buffer, long pgoid):
    """Pack int4 value."""

    return pack("!l", dtype_value)


cpdef long long read_int8(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack int8 value."""

    return unpack("!q", binary_data)[0]


cpdef bytes write_int8(long long dtype_value, object array_function, object buffer, long pgoid):
    """Pack int8 value."""

    return pack("!q", dtype_value)


cpdef double read_money(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack money value."""

    return read_int8(binary_data, array_function, buffer, pgoid) * 0.01


cpdef bytes write_money(double dtype_value, object array_function, object buffer, long pgoid):
    """Pack money value."""

    return write_int8(<long long>round(dtype_value / 0.01), array_function, buffer, pgoid)


cpdef float read_float4(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack float4 value."""

    return unpack("!f", binary_data)[0]


cpdef bytes write_float4(float dtype_value, object array_function, object buffer, long pgoid):
    """Pack float4 value."""

    return pack("!f", dtype_value)


cpdef double read_float8(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack float8 value."""

    return unpack("!d", binary_data)[0]


cpdef bytes write_float8(double dtype_value, object array_function, object buffer, long pgoid):
    """Pack float8 value."""

    return pack("!d", dtype_value)


cpdef object read_numeric(bytes binary_data, object array_function, object buffer, long pgoid):
    """Unpack numeric value."""

    cdef:
        int ndigits, weight, sign, dscale
        int i, pos
        bint is_negative
        list digits = []
        object numeric, scale, power, term
        short digit

    ndigits, weight, sign, dscale = unpack_from("!hhhh", binary_data)

    if sign == 0xc000:
        return Decimal("nan")

    is_negative = (sign == 0x4000)

    cdef int data_len = len(binary_data)

    for i in range(8, 8 + ndigits * 2, 2):
        if i + 1 < data_len:
            digit = unpack_from("!h", binary_data, i)[0]
            digits.append(digit)

    numeric = Decimal(0)
    scale = Decimal(10) ** -dscale

    cdef object weight_dec = Decimal(weight)
    cdef object ten = Decimal(10)
    cdef object four = Decimal(4)

    for pos, digit in enumerate(digits):
        power = four * (weight_dec - Decimal(pos))
        term = Decimal(digit) * (ten ** power)
        numeric += term

    if is_negative:
        numeric *= -1

    return numeric.quantize(scale)


def write_numeric(object dtype_value, object array_function, object buffer, long pgoid):
    """Pack numeric value."""

    cdef bint is_negative
    cdef int sign, dscale, ndigits, weight, base, temp, digit
    cdef object abs_value, scaled_value, int_value, as_tuple
    cdef list digits
    cdef bytes header, digits_data, result

    if dtype_value.is_nan():
        return pack("!hhhh", 0, 0, 0xC000, 0)

    is_negative = dtype_value < 0
    sign = 0x4000 if is_negative else 0x0000

    if dtype_value == 0:
        return pack("!hhhh", 0, 0, sign, 0)

    abs_value = abs(dtype_value)
    as_tuple = abs_value.as_tuple()
    dscale = abs(as_tuple.exponent) if as_tuple.exponent < 0 else 0
    scaled_value = abs_value * (Decimal(10) ** dscale)
    int_value = int(scaled_value.to_integral_value(rounding=ROUND_HALF_UP))

    base = 10000
    digits = []
    temp = int_value

    while temp > 0:
        digits.append(temp % base)
        temp //= base

    if not digits:
        digits = [0]

    digits.reverse()
    ndigits = len(digits)
    weight = (len(str(int_value)) - 1) // 4
    header = pack("!hhhh", ndigits, weight, sign, dscale)
    digits_data = b''.join(pack("!h", digit) for digit in digits)

    return header + digits_data
