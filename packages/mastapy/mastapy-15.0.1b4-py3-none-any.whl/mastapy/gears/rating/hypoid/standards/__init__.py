"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.hypoid.standards._534 import (
        GleasonHypoidGearSingleFlankRating,
    )
    from mastapy._private.gears.rating.hypoid.standards._535 import (
        GleasonHypoidMeshSingleFlankRating,
    )
    from mastapy._private.gears.rating.hypoid.standards._536 import HypoidRateableMesh
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.hypoid.standards._534": [
            "GleasonHypoidGearSingleFlankRating"
        ],
        "_private.gears.rating.hypoid.standards._535": [
            "GleasonHypoidMeshSingleFlankRating"
        ],
        "_private.gears.rating.hypoid.standards._536": ["HypoidRateableMesh"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "GleasonHypoidGearSingleFlankRating",
    "GleasonHypoidMeshSingleFlankRating",
    "HypoidRateableMesh",
)
