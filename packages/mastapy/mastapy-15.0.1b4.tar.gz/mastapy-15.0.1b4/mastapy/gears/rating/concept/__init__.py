"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.concept._640 import ConceptGearDutyCycleRating
    from mastapy._private.gears.rating.concept._641 import (
        ConceptGearMeshDutyCycleRating,
    )
    from mastapy._private.gears.rating.concept._642 import ConceptGearMeshRating
    from mastapy._private.gears.rating.concept._643 import ConceptGearRating
    from mastapy._private.gears.rating.concept._644 import ConceptGearSetDutyCycleRating
    from mastapy._private.gears.rating.concept._645 import ConceptGearSetRating
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.concept._640": ["ConceptGearDutyCycleRating"],
        "_private.gears.rating.concept._641": ["ConceptGearMeshDutyCycleRating"],
        "_private.gears.rating.concept._642": ["ConceptGearMeshRating"],
        "_private.gears.rating.concept._643": ["ConceptGearRating"],
        "_private.gears.rating.concept._644": ["ConceptGearSetDutyCycleRating"],
        "_private.gears.rating.concept._645": ["ConceptGearSetRating"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConceptGearDutyCycleRating",
    "ConceptGearMeshDutyCycleRating",
    "ConceptGearMeshRating",
    "ConceptGearRating",
    "ConceptGearSetDutyCycleRating",
    "ConceptGearSetRating",
)
