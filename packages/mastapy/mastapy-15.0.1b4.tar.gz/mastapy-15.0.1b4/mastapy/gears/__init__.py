"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears._404 import AccuracyGrades
    from mastapy._private.gears._405 import AGMAToleranceStandard
    from mastapy._private.gears._406 import BevelHypoidGearDesignSettings
    from mastapy._private.gears._407 import BevelHypoidGearRatingSettings
    from mastapy._private.gears._408 import CentreDistanceChangeMethod
    from mastapy._private.gears._409 import CoefficientOfFrictionCalculationMethod
    from mastapy._private.gears._410 import ConicalGearToothSurface
    from mastapy._private.gears._411 import ContactRatioDataSource
    from mastapy._private.gears._412 import ContactRatioRequirements
    from mastapy._private.gears._413 import CylindricalFlanks
    from mastapy._private.gears._414 import CylindricalMisalignmentDataSource
    from mastapy._private.gears._415 import DeflectionFromBendingOption
    from mastapy._private.gears._416 import GearFlanks
    from mastapy._private.gears._417 import GearNURBSSurface
    from mastapy._private.gears._418 import GearSetDesignGroup
    from mastapy._private.gears._419 import GearSetModes
    from mastapy._private.gears._420 import GearSetOptimisationResult
    from mastapy._private.gears._421 import GearSetOptimisationResults
    from mastapy._private.gears._422 import GearSetOptimiser
    from mastapy._private.gears._423 import GearWindageAndChurningLossCalculationMethod
    from mastapy._private.gears._424 import Hand
    from mastapy._private.gears._425 import ISOToleranceStandard
    from mastapy._private.gears._426 import LubricationMethods
    from mastapy._private.gears._427 import MicroGeometryInputTypes
    from mastapy._private.gears._428 import MicroGeometryModel
    from mastapy._private.gears._429 import (
        MicropittingCoefficientOfFrictionCalculationMethod,
    )
    from mastapy._private.gears._430 import NamedPlanetAngle
    from mastapy._private.gears._431 import PlanetaryDetail
    from mastapy._private.gears._432 import PlanetaryRatingLoadSharingOption
    from mastapy._private.gears._433 import PocketingPowerLossCoefficients
    from mastapy._private.gears._434 import PocketingPowerLossCoefficientsDatabase
    from mastapy._private.gears._435 import QualityGradeTypes
    from mastapy._private.gears._436 import SafetyRequirementsAGMA
    from mastapy._private.gears._437 import (
        SpecificationForTheEffectOfOilKinematicViscosity,
    )
    from mastapy._private.gears._438 import SpiralBevelRootLineTilt
    from mastapy._private.gears._439 import SpiralBevelToothTaper
    from mastapy._private.gears._440 import TESpecificationType
    from mastapy._private.gears._441 import WormAddendumFactor
    from mastapy._private.gears._442 import WormType
    from mastapy._private.gears._443 import ZerolBevelGleasonToothTaperOption
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears._404": ["AccuracyGrades"],
        "_private.gears._405": ["AGMAToleranceStandard"],
        "_private.gears._406": ["BevelHypoidGearDesignSettings"],
        "_private.gears._407": ["BevelHypoidGearRatingSettings"],
        "_private.gears._408": ["CentreDistanceChangeMethod"],
        "_private.gears._409": ["CoefficientOfFrictionCalculationMethod"],
        "_private.gears._410": ["ConicalGearToothSurface"],
        "_private.gears._411": ["ContactRatioDataSource"],
        "_private.gears._412": ["ContactRatioRequirements"],
        "_private.gears._413": ["CylindricalFlanks"],
        "_private.gears._414": ["CylindricalMisalignmentDataSource"],
        "_private.gears._415": ["DeflectionFromBendingOption"],
        "_private.gears._416": ["GearFlanks"],
        "_private.gears._417": ["GearNURBSSurface"],
        "_private.gears._418": ["GearSetDesignGroup"],
        "_private.gears._419": ["GearSetModes"],
        "_private.gears._420": ["GearSetOptimisationResult"],
        "_private.gears._421": ["GearSetOptimisationResults"],
        "_private.gears._422": ["GearSetOptimiser"],
        "_private.gears._423": ["GearWindageAndChurningLossCalculationMethod"],
        "_private.gears._424": ["Hand"],
        "_private.gears._425": ["ISOToleranceStandard"],
        "_private.gears._426": ["LubricationMethods"],
        "_private.gears._427": ["MicroGeometryInputTypes"],
        "_private.gears._428": ["MicroGeometryModel"],
        "_private.gears._429": ["MicropittingCoefficientOfFrictionCalculationMethod"],
        "_private.gears._430": ["NamedPlanetAngle"],
        "_private.gears._431": ["PlanetaryDetail"],
        "_private.gears._432": ["PlanetaryRatingLoadSharingOption"],
        "_private.gears._433": ["PocketingPowerLossCoefficients"],
        "_private.gears._434": ["PocketingPowerLossCoefficientsDatabase"],
        "_private.gears._435": ["QualityGradeTypes"],
        "_private.gears._436": ["SafetyRequirementsAGMA"],
        "_private.gears._437": ["SpecificationForTheEffectOfOilKinematicViscosity"],
        "_private.gears._438": ["SpiralBevelRootLineTilt"],
        "_private.gears._439": ["SpiralBevelToothTaper"],
        "_private.gears._440": ["TESpecificationType"],
        "_private.gears._441": ["WormAddendumFactor"],
        "_private.gears._442": ["WormType"],
        "_private.gears._443": ["ZerolBevelGleasonToothTaperOption"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AccuracyGrades",
    "AGMAToleranceStandard",
    "BevelHypoidGearDesignSettings",
    "BevelHypoidGearRatingSettings",
    "CentreDistanceChangeMethod",
    "CoefficientOfFrictionCalculationMethod",
    "ConicalGearToothSurface",
    "ContactRatioDataSource",
    "ContactRatioRequirements",
    "CylindricalFlanks",
    "CylindricalMisalignmentDataSource",
    "DeflectionFromBendingOption",
    "GearFlanks",
    "GearNURBSSurface",
    "GearSetDesignGroup",
    "GearSetModes",
    "GearSetOptimisationResult",
    "GearSetOptimisationResults",
    "GearSetOptimiser",
    "GearWindageAndChurningLossCalculationMethod",
    "Hand",
    "ISOToleranceStandard",
    "LubricationMethods",
    "MicroGeometryInputTypes",
    "MicroGeometryModel",
    "MicropittingCoefficientOfFrictionCalculationMethod",
    "NamedPlanetAngle",
    "PlanetaryDetail",
    "PlanetaryRatingLoadSharingOption",
    "PocketingPowerLossCoefficients",
    "PocketingPowerLossCoefficientsDatabase",
    "QualityGradeTypes",
    "SafetyRequirementsAGMA",
    "SpecificationForTheEffectOfOilKinematicViscosity",
    "SpiralBevelRootLineTilt",
    "SpiralBevelToothTaper",
    "TESpecificationType",
    "WormAddendumFactor",
    "WormType",
    "ZerolBevelGleasonToothTaperOption",
)
