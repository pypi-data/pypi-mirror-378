"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.bevel._646 import BevelGearMeshRating
    from mastapy._private.gears.rating.bevel._647 import BevelGearRating
    from mastapy._private.gears.rating.bevel._648 import BevelGearSetRating
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.bevel._646": ["BevelGearMeshRating"],
        "_private.gears.rating.bevel._647": ["BevelGearRating"],
        "_private.gears.rating.bevel._648": ["BevelGearSetRating"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BevelGearMeshRating",
    "BevelGearRating",
    "BevelGearSetRating",
)
