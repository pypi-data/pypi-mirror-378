"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.conical._630 import ConicalGearDutyCycleRating
    from mastapy._private.gears.rating.conical._631 import ConicalGearMeshRating
    from mastapy._private.gears.rating.conical._632 import ConicalGearRating
    from mastapy._private.gears.rating.conical._633 import ConicalGearSetDutyCycleRating
    from mastapy._private.gears.rating.conical._634 import ConicalGearSetRating
    from mastapy._private.gears.rating.conical._635 import ConicalGearSingleFlankRating
    from mastapy._private.gears.rating.conical._636 import ConicalMeshDutyCycleRating
    from mastapy._private.gears.rating.conical._637 import ConicalMeshedGearRating
    from mastapy._private.gears.rating.conical._638 import ConicalMeshSingleFlankRating
    from mastapy._private.gears.rating.conical._639 import ConicalRateableMesh
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.conical._630": ["ConicalGearDutyCycleRating"],
        "_private.gears.rating.conical._631": ["ConicalGearMeshRating"],
        "_private.gears.rating.conical._632": ["ConicalGearRating"],
        "_private.gears.rating.conical._633": ["ConicalGearSetDutyCycleRating"],
        "_private.gears.rating.conical._634": ["ConicalGearSetRating"],
        "_private.gears.rating.conical._635": ["ConicalGearSingleFlankRating"],
        "_private.gears.rating.conical._636": ["ConicalMeshDutyCycleRating"],
        "_private.gears.rating.conical._637": ["ConicalMeshedGearRating"],
        "_private.gears.rating.conical._638": ["ConicalMeshSingleFlankRating"],
        "_private.gears.rating.conical._639": ["ConicalRateableMesh"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConicalGearDutyCycleRating",
    "ConicalGearMeshRating",
    "ConicalGearRating",
    "ConicalGearSetDutyCycleRating",
    "ConicalGearSetRating",
    "ConicalGearSingleFlankRating",
    "ConicalMeshDutyCycleRating",
    "ConicalMeshedGearRating",
    "ConicalMeshSingleFlankRating",
    "ConicalRateableMesh",
)
