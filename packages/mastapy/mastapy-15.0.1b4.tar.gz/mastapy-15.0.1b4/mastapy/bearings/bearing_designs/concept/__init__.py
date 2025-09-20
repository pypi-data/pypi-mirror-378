"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.bearings.bearing_designs.concept._2412 import (
        BearingNodePosition,
    )
    from mastapy._private.bearings.bearing_designs.concept._2413 import (
        ConceptAxialClearanceBearing,
    )
    from mastapy._private.bearings.bearing_designs.concept._2414 import (
        ConceptClearanceBearing,
    )
    from mastapy._private.bearings.bearing_designs.concept._2415 import (
        ConceptRadialClearanceBearing,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.bearings.bearing_designs.concept._2412": ["BearingNodePosition"],
        "_private.bearings.bearing_designs.concept._2413": [
            "ConceptAxialClearanceBearing"
        ],
        "_private.bearings.bearing_designs.concept._2414": ["ConceptClearanceBearing"],
        "_private.bearings.bearing_designs.concept._2415": [
            "ConceptRadialClearanceBearing"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BearingNodePosition",
    "ConceptAxialClearanceBearing",
    "ConceptClearanceBearing",
    "ConceptRadialClearanceBearing",
)
