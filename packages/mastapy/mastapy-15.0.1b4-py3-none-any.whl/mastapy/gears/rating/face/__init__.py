"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.face._537 import FaceGearDutyCycleRating
    from mastapy._private.gears.rating.face._538 import FaceGearMeshDutyCycleRating
    from mastapy._private.gears.rating.face._539 import FaceGearMeshRating
    from mastapy._private.gears.rating.face._540 import FaceGearRating
    from mastapy._private.gears.rating.face._541 import FaceGearSetDutyCycleRating
    from mastapy._private.gears.rating.face._542 import FaceGearSetRating
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.face._537": ["FaceGearDutyCycleRating"],
        "_private.gears.rating.face._538": ["FaceGearMeshDutyCycleRating"],
        "_private.gears.rating.face._539": ["FaceGearMeshRating"],
        "_private.gears.rating.face._540": ["FaceGearRating"],
        "_private.gears.rating.face._541": ["FaceGearSetDutyCycleRating"],
        "_private.gears.rating.face._542": ["FaceGearSetRating"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "FaceGearDutyCycleRating",
    "FaceGearMeshDutyCycleRating",
    "FaceGearMeshRating",
    "FaceGearRating",
    "FaceGearSetDutyCycleRating",
    "FaceGearSetRating",
)
