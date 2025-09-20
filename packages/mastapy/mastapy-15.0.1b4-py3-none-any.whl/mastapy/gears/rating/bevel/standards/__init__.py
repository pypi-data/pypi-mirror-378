"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.bevel.standards._649 import (
        AGMASpiralBevelGearSingleFlankRating,
    )
    from mastapy._private.gears.rating.bevel.standards._650 import (
        AGMASpiralBevelMeshSingleFlankRating,
    )
    from mastapy._private.gears.rating.bevel.standards._651 import (
        GleasonSpiralBevelGearSingleFlankRating,
    )
    from mastapy._private.gears.rating.bevel.standards._652 import (
        GleasonSpiralBevelMeshSingleFlankRating,
    )
    from mastapy._private.gears.rating.bevel.standards._653 import (
        SpiralBevelGearSingleFlankRating,
    )
    from mastapy._private.gears.rating.bevel.standards._654 import (
        SpiralBevelMeshSingleFlankRating,
    )
    from mastapy._private.gears.rating.bevel.standards._655 import (
        SpiralBevelRateableGear,
    )
    from mastapy._private.gears.rating.bevel.standards._656 import (
        SpiralBevelRateableMesh,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.bevel.standards._649": [
            "AGMASpiralBevelGearSingleFlankRating"
        ],
        "_private.gears.rating.bevel.standards._650": [
            "AGMASpiralBevelMeshSingleFlankRating"
        ],
        "_private.gears.rating.bevel.standards._651": [
            "GleasonSpiralBevelGearSingleFlankRating"
        ],
        "_private.gears.rating.bevel.standards._652": [
            "GleasonSpiralBevelMeshSingleFlankRating"
        ],
        "_private.gears.rating.bevel.standards._653": [
            "SpiralBevelGearSingleFlankRating"
        ],
        "_private.gears.rating.bevel.standards._654": [
            "SpiralBevelMeshSingleFlankRating"
        ],
        "_private.gears.rating.bevel.standards._655": ["SpiralBevelRateableGear"],
        "_private.gears.rating.bevel.standards._656": ["SpiralBevelRateableMesh"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AGMASpiralBevelGearSingleFlankRating",
    "AGMASpiralBevelMeshSingleFlankRating",
    "GleasonSpiralBevelGearSingleFlankRating",
    "GleasonSpiralBevelMeshSingleFlankRating",
    "SpiralBevelGearSingleFlankRating",
    "SpiralBevelMeshSingleFlankRating",
    "SpiralBevelRateableGear",
    "SpiralBevelRateableMesh",
)
