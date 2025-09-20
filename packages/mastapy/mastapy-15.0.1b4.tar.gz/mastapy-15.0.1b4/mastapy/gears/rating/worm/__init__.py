"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.worm._464 import WormGearDutyCycleRating
    from mastapy._private.gears.rating.worm._465 import WormGearMeshRating
    from mastapy._private.gears.rating.worm._466 import WormGearRating
    from mastapy._private.gears.rating.worm._467 import WormGearSetDutyCycleRating
    from mastapy._private.gears.rating.worm._468 import WormGearSetRating
    from mastapy._private.gears.rating.worm._469 import WormMeshDutyCycleRating
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.worm._464": ["WormGearDutyCycleRating"],
        "_private.gears.rating.worm._465": ["WormGearMeshRating"],
        "_private.gears.rating.worm._466": ["WormGearRating"],
        "_private.gears.rating.worm._467": ["WormGearSetDutyCycleRating"],
        "_private.gears.rating.worm._468": ["WormGearSetRating"],
        "_private.gears.rating.worm._469": ["WormMeshDutyCycleRating"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "WormGearDutyCycleRating",
    "WormGearMeshRating",
    "WormGearRating",
    "WormGearSetDutyCycleRating",
    "WormGearSetRating",
    "WormMeshDutyCycleRating",
)
