"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.projections._2724 import (
        SpecifiedConcentricPartGroupDrawingOrder,
    )
    from mastapy._private.system_model.part_model.projections._2725 import (
        SpecifiedParallelPartGroupDrawingOrder,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.projections._2724": [
            "SpecifiedConcentricPartGroupDrawingOrder"
        ],
        "_private.system_model.part_model.projections._2725": [
            "SpecifiedParallelPartGroupDrawingOrder"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "SpecifiedConcentricPartGroupDrawingOrder",
    "SpecifiedParallelPartGroupDrawingOrder",
)
