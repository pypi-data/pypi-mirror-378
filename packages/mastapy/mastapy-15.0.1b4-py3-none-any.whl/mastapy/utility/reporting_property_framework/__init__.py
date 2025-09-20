"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.reporting_property_framework._1988 import (
        CellValuePosition,
    )
    from mastapy._private.utility.reporting_property_framework._1989 import (
        CustomChartType,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.reporting_property_framework._1988": ["CellValuePosition"],
        "_private.utility.reporting_property_framework._1989": ["CustomChartType"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CellValuePosition",
    "CustomChartType",
)
