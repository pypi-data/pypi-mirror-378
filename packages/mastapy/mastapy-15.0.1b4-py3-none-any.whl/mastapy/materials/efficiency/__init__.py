"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.materials.efficiency._383 import BearingEfficiencyRatingMethod
    from mastapy._private.materials.efficiency._384 import CombinedResistiveTorque
    from mastapy._private.materials.efficiency._385 import IndependentPowerLoss
    from mastapy._private.materials.efficiency._386 import IndependentResistiveTorque
    from mastapy._private.materials.efficiency._387 import LoadAndSpeedCombinedPowerLoss
    from mastapy._private.materials.efficiency._388 import OilPumpDetail
    from mastapy._private.materials.efficiency._389 import OilPumpDriveType
    from mastapy._private.materials.efficiency._390 import OilSealLossCalculationMethod
    from mastapy._private.materials.efficiency._391 import OilSealMaterialType
    from mastapy._private.materials.efficiency._392 import PowerLoss
    from mastapy._private.materials.efficiency._393 import ResistiveTorque
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.materials.efficiency._383": ["BearingEfficiencyRatingMethod"],
        "_private.materials.efficiency._384": ["CombinedResistiveTorque"],
        "_private.materials.efficiency._385": ["IndependentPowerLoss"],
        "_private.materials.efficiency._386": ["IndependentResistiveTorque"],
        "_private.materials.efficiency._387": ["LoadAndSpeedCombinedPowerLoss"],
        "_private.materials.efficiency._388": ["OilPumpDetail"],
        "_private.materials.efficiency._389": ["OilPumpDriveType"],
        "_private.materials.efficiency._390": ["OilSealLossCalculationMethod"],
        "_private.materials.efficiency._391": ["OilSealMaterialType"],
        "_private.materials.efficiency._392": ["PowerLoss"],
        "_private.materials.efficiency._393": ["ResistiveTorque"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BearingEfficiencyRatingMethod",
    "CombinedResistiveTorque",
    "IndependentPowerLoss",
    "IndependentResistiveTorque",
    "LoadAndSpeedCombinedPowerLoss",
    "OilPumpDetail",
    "OilPumpDriveType",
    "OilSealLossCalculationMethod",
    "OilSealMaterialType",
    "PowerLoss",
    "ResistiveTorque",
)
