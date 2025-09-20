"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.property._2044 import DeletableCollectionMember
    from mastapy._private.utility.property._2045 import DutyCyclePropertySummary
    from mastapy._private.utility.property._2046 import DutyCyclePropertySummaryForce
    from mastapy._private.utility.property._2047 import (
        DutyCyclePropertySummaryPercentage,
    )
    from mastapy._private.utility.property._2048 import (
        DutyCyclePropertySummarySmallAngle,
    )
    from mastapy._private.utility.property._2049 import DutyCyclePropertySummaryStress
    from mastapy._private.utility.property._2050 import (
        DutyCyclePropertySummaryVeryShortLength,
    )
    from mastapy._private.utility.property._2051 import EnumWithBoolean
    from mastapy._private.utility.property._2052 import (
        NamedRangeWithOverridableMinAndMax,
    )
    from mastapy._private.utility.property._2053 import TypedObjectsWithOption
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.property._2044": ["DeletableCollectionMember"],
        "_private.utility.property._2045": ["DutyCyclePropertySummary"],
        "_private.utility.property._2046": ["DutyCyclePropertySummaryForce"],
        "_private.utility.property._2047": ["DutyCyclePropertySummaryPercentage"],
        "_private.utility.property._2048": ["DutyCyclePropertySummarySmallAngle"],
        "_private.utility.property._2049": ["DutyCyclePropertySummaryStress"],
        "_private.utility.property._2050": ["DutyCyclePropertySummaryVeryShortLength"],
        "_private.utility.property._2051": ["EnumWithBoolean"],
        "_private.utility.property._2052": ["NamedRangeWithOverridableMinAndMax"],
        "_private.utility.property._2053": ["TypedObjectsWithOption"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "DeletableCollectionMember",
    "DutyCyclePropertySummary",
    "DutyCyclePropertySummaryForce",
    "DutyCyclePropertySummaryPercentage",
    "DutyCyclePropertySummarySmallAngle",
    "DutyCyclePropertySummaryStress",
    "DutyCyclePropertySummaryVeryShortLength",
    "EnumWithBoolean",
    "NamedRangeWithOverridableMinAndMax",
    "TypedObjectsWithOption",
)
