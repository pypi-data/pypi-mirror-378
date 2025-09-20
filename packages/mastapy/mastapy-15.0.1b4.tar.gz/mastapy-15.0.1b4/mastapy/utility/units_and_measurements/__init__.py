"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.units_and_measurements._1799 import (
        DegreesMinutesSeconds,
    )
    from mastapy._private.utility.units_and_measurements._1800 import EnumUnit
    from mastapy._private.utility.units_and_measurements._1801 import InverseUnit
    from mastapy._private.utility.units_and_measurements._1802 import MeasurementBase
    from mastapy._private.utility.units_and_measurements._1803 import (
        MeasurementSettings,
    )
    from mastapy._private.utility.units_and_measurements._1804 import MeasurementSystem
    from mastapy._private.utility.units_and_measurements._1805 import SafetyFactorUnit
    from mastapy._private.utility.units_and_measurements._1806 import TimeUnit
    from mastapy._private.utility.units_and_measurements._1807 import Unit
    from mastapy._private.utility.units_and_measurements._1808 import UnitGradient
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.units_and_measurements._1799": ["DegreesMinutesSeconds"],
        "_private.utility.units_and_measurements._1800": ["EnumUnit"],
        "_private.utility.units_and_measurements._1801": ["InverseUnit"],
        "_private.utility.units_and_measurements._1802": ["MeasurementBase"],
        "_private.utility.units_and_measurements._1803": ["MeasurementSettings"],
        "_private.utility.units_and_measurements._1804": ["MeasurementSystem"],
        "_private.utility.units_and_measurements._1805": ["SafetyFactorUnit"],
        "_private.utility.units_and_measurements._1806": ["TimeUnit"],
        "_private.utility.units_and_measurements._1807": ["Unit"],
        "_private.utility.units_and_measurements._1808": ["UnitGradient"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "DegreesMinutesSeconds",
    "EnumUnit",
    "InverseUnit",
    "MeasurementBase",
    "MeasurementSettings",
    "MeasurementSystem",
    "SafetyFactorUnit",
    "TimeUnit",
    "Unit",
    "UnitGradient",
)
