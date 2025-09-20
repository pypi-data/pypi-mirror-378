"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.cycloidal._2811 import (
        CycloidalAssembly,
    )
    from mastapy._private.system_model.part_model.cycloidal._2812 import CycloidalDisc
    from mastapy._private.system_model.part_model.cycloidal._2813 import RingPins
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.cycloidal._2811": ["CycloidalAssembly"],
        "_private.system_model.part_model.cycloidal._2812": ["CycloidalDisc"],
        "_private.system_model.part_model.cycloidal._2813": ["RingPins"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CycloidalAssembly",
    "CycloidalDisc",
    "RingPins",
)
