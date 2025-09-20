"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.geometry.two_d._400 import CADFace
    from mastapy._private.geometry.two_d._401 import CADFaceGroup
    from mastapy._private.geometry.two_d._402 import InternalExternalType
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.geometry.two_d._400": ["CADFace"],
        "_private.geometry.two_d._401": ["CADFaceGroup"],
        "_private.geometry.two_d._402": ["InternalExternalType"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CADFace",
    "CADFaceGroup",
    "InternalExternalType",
)
