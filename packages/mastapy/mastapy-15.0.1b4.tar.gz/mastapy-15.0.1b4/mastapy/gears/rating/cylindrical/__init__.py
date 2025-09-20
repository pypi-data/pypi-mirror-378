"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.rating.cylindrical._543 import AGMAScuffingResultsRow
    from mastapy._private.gears.rating.cylindrical._544 import (
        CylindricalGearDesignAndRatingSettings,
    )
    from mastapy._private.gears.rating.cylindrical._545 import (
        CylindricalGearDesignAndRatingSettingsDatabase,
    )
    from mastapy._private.gears.rating.cylindrical._546 import (
        CylindricalGearDesignAndRatingSettingsItem,
    )
    from mastapy._private.gears.rating.cylindrical._547 import (
        CylindricalGearDutyCycleRating,
    )
    from mastapy._private.gears.rating.cylindrical._548 import (
        CylindricalGearFlankDutyCycleRating,
    )
    from mastapy._private.gears.rating.cylindrical._549 import (
        CylindricalGearFlankRating,
    )
    from mastapy._private.gears.rating.cylindrical._550 import CylindricalGearMeshRating
    from mastapy._private.gears.rating.cylindrical._551 import (
        CylindricalGearMicroPittingResults,
    )
    from mastapy._private.gears.rating.cylindrical._552 import CylindricalGearRating
    from mastapy._private.gears.rating.cylindrical._553 import (
        CylindricalGearRatingGeometryDataSource,
    )
    from mastapy._private.gears.rating.cylindrical._554 import (
        CylindricalGearScuffingResults,
    )
    from mastapy._private.gears.rating.cylindrical._555 import (
        CylindricalGearSetDutyCycleRating,
    )
    from mastapy._private.gears.rating.cylindrical._556 import CylindricalGearSetRating
    from mastapy._private.gears.rating.cylindrical._557 import (
        CylindricalGearSingleFlankRating,
    )
    from mastapy._private.gears.rating.cylindrical._558 import (
        CylindricalMeshDutyCycleRating,
    )
    from mastapy._private.gears.rating.cylindrical._559 import (
        CylindricalMeshSingleFlankRating,
    )
    from mastapy._private.gears.rating.cylindrical._560 import (
        CylindricalPlasticGearRatingSettings,
    )
    from mastapy._private.gears.rating.cylindrical._561 import (
        CylindricalPlasticGearRatingSettingsDatabase,
    )
    from mastapy._private.gears.rating.cylindrical._562 import (
        CylindricalPlasticGearRatingSettingsItem,
    )
    from mastapy._private.gears.rating.cylindrical._563 import CylindricalRateableMesh
    from mastapy._private.gears.rating.cylindrical._564 import DynamicFactorMethods
    from mastapy._private.gears.rating.cylindrical._565 import (
        GearBlankFactorCalculationOptions,
    )
    from mastapy._private.gears.rating.cylindrical._566 import ISOScuffingResultsRow
    from mastapy._private.gears.rating.cylindrical._567 import MeshRatingForReports
    from mastapy._private.gears.rating.cylindrical._568 import MicropittingRatingMethod
    from mastapy._private.gears.rating.cylindrical._569 import MicroPittingResultsRow
    from mastapy._private.gears.rating.cylindrical._570 import (
        MisalignmentContactPatternEnhancements,
    )
    from mastapy._private.gears.rating.cylindrical._571 import RatingMethod
    from mastapy._private.gears.rating.cylindrical._572 import (
        ReducedCylindricalGearSetDutyCycleRating,
    )
    from mastapy._private.gears.rating.cylindrical._573 import (
        ScuffingFlashTemperatureRatingMethod,
    )
    from mastapy._private.gears.rating.cylindrical._574 import (
        ScuffingIntegralTemperatureRatingMethod,
    )
    from mastapy._private.gears.rating.cylindrical._575 import ScuffingMethods
    from mastapy._private.gears.rating.cylindrical._576 import ScuffingResultsRow
    from mastapy._private.gears.rating.cylindrical._577 import ScuffingResultsRowGear
    from mastapy._private.gears.rating.cylindrical._578 import TipReliefScuffingOptions
    from mastapy._private.gears.rating.cylindrical._579 import ToothThicknesses
    from mastapy._private.gears.rating.cylindrical._580 import (
        VDI2737SafetyFactorReportingObject,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.rating.cylindrical._543": ["AGMAScuffingResultsRow"],
        "_private.gears.rating.cylindrical._544": [
            "CylindricalGearDesignAndRatingSettings"
        ],
        "_private.gears.rating.cylindrical._545": [
            "CylindricalGearDesignAndRatingSettingsDatabase"
        ],
        "_private.gears.rating.cylindrical._546": [
            "CylindricalGearDesignAndRatingSettingsItem"
        ],
        "_private.gears.rating.cylindrical._547": ["CylindricalGearDutyCycleRating"],
        "_private.gears.rating.cylindrical._548": [
            "CylindricalGearFlankDutyCycleRating"
        ],
        "_private.gears.rating.cylindrical._549": ["CylindricalGearFlankRating"],
        "_private.gears.rating.cylindrical._550": ["CylindricalGearMeshRating"],
        "_private.gears.rating.cylindrical._551": [
            "CylindricalGearMicroPittingResults"
        ],
        "_private.gears.rating.cylindrical._552": ["CylindricalGearRating"],
        "_private.gears.rating.cylindrical._553": [
            "CylindricalGearRatingGeometryDataSource"
        ],
        "_private.gears.rating.cylindrical._554": ["CylindricalGearScuffingResults"],
        "_private.gears.rating.cylindrical._555": ["CylindricalGearSetDutyCycleRating"],
        "_private.gears.rating.cylindrical._556": ["CylindricalGearSetRating"],
        "_private.gears.rating.cylindrical._557": ["CylindricalGearSingleFlankRating"],
        "_private.gears.rating.cylindrical._558": ["CylindricalMeshDutyCycleRating"],
        "_private.gears.rating.cylindrical._559": ["CylindricalMeshSingleFlankRating"],
        "_private.gears.rating.cylindrical._560": [
            "CylindricalPlasticGearRatingSettings"
        ],
        "_private.gears.rating.cylindrical._561": [
            "CylindricalPlasticGearRatingSettingsDatabase"
        ],
        "_private.gears.rating.cylindrical._562": [
            "CylindricalPlasticGearRatingSettingsItem"
        ],
        "_private.gears.rating.cylindrical._563": ["CylindricalRateableMesh"],
        "_private.gears.rating.cylindrical._564": ["DynamicFactorMethods"],
        "_private.gears.rating.cylindrical._565": ["GearBlankFactorCalculationOptions"],
        "_private.gears.rating.cylindrical._566": ["ISOScuffingResultsRow"],
        "_private.gears.rating.cylindrical._567": ["MeshRatingForReports"],
        "_private.gears.rating.cylindrical._568": ["MicropittingRatingMethod"],
        "_private.gears.rating.cylindrical._569": ["MicroPittingResultsRow"],
        "_private.gears.rating.cylindrical._570": [
            "MisalignmentContactPatternEnhancements"
        ],
        "_private.gears.rating.cylindrical._571": ["RatingMethod"],
        "_private.gears.rating.cylindrical._572": [
            "ReducedCylindricalGearSetDutyCycleRating"
        ],
        "_private.gears.rating.cylindrical._573": [
            "ScuffingFlashTemperatureRatingMethod"
        ],
        "_private.gears.rating.cylindrical._574": [
            "ScuffingIntegralTemperatureRatingMethod"
        ],
        "_private.gears.rating.cylindrical._575": ["ScuffingMethods"],
        "_private.gears.rating.cylindrical._576": ["ScuffingResultsRow"],
        "_private.gears.rating.cylindrical._577": ["ScuffingResultsRowGear"],
        "_private.gears.rating.cylindrical._578": ["TipReliefScuffingOptions"],
        "_private.gears.rating.cylindrical._579": ["ToothThicknesses"],
        "_private.gears.rating.cylindrical._580": [
            "VDI2737SafetyFactorReportingObject"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AGMAScuffingResultsRow",
    "CylindricalGearDesignAndRatingSettings",
    "CylindricalGearDesignAndRatingSettingsDatabase",
    "CylindricalGearDesignAndRatingSettingsItem",
    "CylindricalGearDutyCycleRating",
    "CylindricalGearFlankDutyCycleRating",
    "CylindricalGearFlankRating",
    "CylindricalGearMeshRating",
    "CylindricalGearMicroPittingResults",
    "CylindricalGearRating",
    "CylindricalGearRatingGeometryDataSource",
    "CylindricalGearScuffingResults",
    "CylindricalGearSetDutyCycleRating",
    "CylindricalGearSetRating",
    "CylindricalGearSingleFlankRating",
    "CylindricalMeshDutyCycleRating",
    "CylindricalMeshSingleFlankRating",
    "CylindricalPlasticGearRatingSettings",
    "CylindricalPlasticGearRatingSettingsDatabase",
    "CylindricalPlasticGearRatingSettingsItem",
    "CylindricalRateableMesh",
    "DynamicFactorMethods",
    "GearBlankFactorCalculationOptions",
    "ISOScuffingResultsRow",
    "MeshRatingForReports",
    "MicropittingRatingMethod",
    "MicroPittingResultsRow",
    "MisalignmentContactPatternEnhancements",
    "RatingMethod",
    "ReducedCylindricalGearSetDutyCycleRating",
    "ScuffingFlashTemperatureRatingMethod",
    "ScuffingIntegralTemperatureRatingMethod",
    "ScuffingMethods",
    "ScuffingResultsRow",
    "ScuffingResultsRowGear",
    "TipReliefScuffingOptions",
    "ToothThicknesses",
    "VDI2737SafetyFactorReportingObject",
)
