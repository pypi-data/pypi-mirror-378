"""PGCopy bynary dump parser."""

from .enums import PGOid
from .errors import (
    PGCopyRecordError,
    PGCopySignatureError,
)
from .reader import PGCopyReader
from .writer import PGCopyWriter


__all__ = (
    "PGCopyReader",
    "PGCopyRecordError",
    "PGCopySignatureError",
    "PGCopyWriter",
    "PGOid",
)
__author__ = "0xMihalich"
__version__ = "0.2.0.1"
