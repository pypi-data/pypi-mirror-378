"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.materials._324 import (
        AbstractStressCyclesDataForAnSNCurveOfAPlasticMaterial,
    )
    from mastapy._private.materials._325 import AcousticRadiationEfficiency
    from mastapy._private.materials._326 import AcousticRadiationEfficiencyInputType
    from mastapy._private.materials._327 import AGMALubricantType
    from mastapy._private.materials._328 import AGMAMaterialApplications
    from mastapy._private.materials._329 import AGMAMaterialClasses
    from mastapy._private.materials._330 import AGMAMaterialGrade
    from mastapy._private.materials._331 import AirProperties
    from mastapy._private.materials._332 import BearingLubricationCondition
    from mastapy._private.materials._333 import BearingMaterial
    from mastapy._private.materials._334 import BearingMaterialDatabase
    from mastapy._private.materials._335 import BHCurveExtrapolationMethod
    from mastapy._private.materials._336 import BHCurveSpecification
    from mastapy._private.materials._337 import ComponentMaterialDatabase
    from mastapy._private.materials._338 import CompositeFatigueSafetyFactorItem
    from mastapy._private.materials._339 import CylindricalGearRatingMethods
    from mastapy._private.materials._340 import DensitySpecificationMethod
    from mastapy._private.materials._341 import FatigueSafetyFactorItem
    from mastapy._private.materials._342 import FatigueSafetyFactorItemBase
    from mastapy._private.materials._343 import Fluid
    from mastapy._private.materials._344 import FluidDatabase
    from mastapy._private.materials._345 import GearingTypes
    from mastapy._private.materials._346 import GeneralTransmissionProperties
    from mastapy._private.materials._347 import GreaseContaminationOptions
    from mastapy._private.materials._348 import HardnessType
    from mastapy._private.materials._349 import ISO76StaticSafetyFactorLimits
    from mastapy._private.materials._350 import ISOLubricantType
    from mastapy._private.materials._351 import LubricantDefinition
    from mastapy._private.materials._352 import LubricantDelivery
    from mastapy._private.materials._353 import LubricantViscosityClassAGMA
    from mastapy._private.materials._354 import LubricantViscosityClassification
    from mastapy._private.materials._355 import LubricantViscosityClassISO
    from mastapy._private.materials._356 import LubricantViscosityClassSAE
    from mastapy._private.materials._357 import LubricationDetail
    from mastapy._private.materials._358 import LubricationDetailDatabase
    from mastapy._private.materials._359 import Material
    from mastapy._private.materials._360 import MaterialDatabase
    from mastapy._private.materials._361 import MaterialsSettings
    from mastapy._private.materials._362 import MaterialsSettingsDatabase
    from mastapy._private.materials._363 import MaterialsSettingsItem
    from mastapy._private.materials._364 import MaterialStandards
    from mastapy._private.materials._365 import MetalPlasticType
    from mastapy._private.materials._366 import OilFiltrationOptions
    from mastapy._private.materials._367 import PressureViscosityCoefficientMethod
    from mastapy._private.materials._368 import QualityGrade
    from mastapy._private.materials._369 import SafetyFactorGroup
    from mastapy._private.materials._370 import SafetyFactorItem
    from mastapy._private.materials._371 import SNCurve
    from mastapy._private.materials._372 import SNCurvePoint
    from mastapy._private.materials._373 import SoundPressureEnclosure
    from mastapy._private.materials._374 import SoundPressureEnclosureType
    from mastapy._private.materials._375 import (
        StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial,
    )
    from mastapy._private.materials._376 import (
        StressCyclesDataForTheContactSNCurveOfAPlasticMaterial,
    )
    from mastapy._private.materials._377 import TemperatureDependentProperty
    from mastapy._private.materials._378 import TransmissionApplications
    from mastapy._private.materials._379 import VDI2736LubricantType
    from mastapy._private.materials._380 import VehicleDynamicsProperties
    from mastapy._private.materials._381 import WindTurbineStandards
    from mastapy._private.materials._382 import WorkingCharacteristics
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.materials._324": [
            "AbstractStressCyclesDataForAnSNCurveOfAPlasticMaterial"
        ],
        "_private.materials._325": ["AcousticRadiationEfficiency"],
        "_private.materials._326": ["AcousticRadiationEfficiencyInputType"],
        "_private.materials._327": ["AGMALubricantType"],
        "_private.materials._328": ["AGMAMaterialApplications"],
        "_private.materials._329": ["AGMAMaterialClasses"],
        "_private.materials._330": ["AGMAMaterialGrade"],
        "_private.materials._331": ["AirProperties"],
        "_private.materials._332": ["BearingLubricationCondition"],
        "_private.materials._333": ["BearingMaterial"],
        "_private.materials._334": ["BearingMaterialDatabase"],
        "_private.materials._335": ["BHCurveExtrapolationMethod"],
        "_private.materials._336": ["BHCurveSpecification"],
        "_private.materials._337": ["ComponentMaterialDatabase"],
        "_private.materials._338": ["CompositeFatigueSafetyFactorItem"],
        "_private.materials._339": ["CylindricalGearRatingMethods"],
        "_private.materials._340": ["DensitySpecificationMethod"],
        "_private.materials._341": ["FatigueSafetyFactorItem"],
        "_private.materials._342": ["FatigueSafetyFactorItemBase"],
        "_private.materials._343": ["Fluid"],
        "_private.materials._344": ["FluidDatabase"],
        "_private.materials._345": ["GearingTypes"],
        "_private.materials._346": ["GeneralTransmissionProperties"],
        "_private.materials._347": ["GreaseContaminationOptions"],
        "_private.materials._348": ["HardnessType"],
        "_private.materials._349": ["ISO76StaticSafetyFactorLimits"],
        "_private.materials._350": ["ISOLubricantType"],
        "_private.materials._351": ["LubricantDefinition"],
        "_private.materials._352": ["LubricantDelivery"],
        "_private.materials._353": ["LubricantViscosityClassAGMA"],
        "_private.materials._354": ["LubricantViscosityClassification"],
        "_private.materials._355": ["LubricantViscosityClassISO"],
        "_private.materials._356": ["LubricantViscosityClassSAE"],
        "_private.materials._357": ["LubricationDetail"],
        "_private.materials._358": ["LubricationDetailDatabase"],
        "_private.materials._359": ["Material"],
        "_private.materials._360": ["MaterialDatabase"],
        "_private.materials._361": ["MaterialsSettings"],
        "_private.materials._362": ["MaterialsSettingsDatabase"],
        "_private.materials._363": ["MaterialsSettingsItem"],
        "_private.materials._364": ["MaterialStandards"],
        "_private.materials._365": ["MetalPlasticType"],
        "_private.materials._366": ["OilFiltrationOptions"],
        "_private.materials._367": ["PressureViscosityCoefficientMethod"],
        "_private.materials._368": ["QualityGrade"],
        "_private.materials._369": ["SafetyFactorGroup"],
        "_private.materials._370": ["SafetyFactorItem"],
        "_private.materials._371": ["SNCurve"],
        "_private.materials._372": ["SNCurvePoint"],
        "_private.materials._373": ["SoundPressureEnclosure"],
        "_private.materials._374": ["SoundPressureEnclosureType"],
        "_private.materials._375": [
            "StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial"
        ],
        "_private.materials._376": [
            "StressCyclesDataForTheContactSNCurveOfAPlasticMaterial"
        ],
        "_private.materials._377": ["TemperatureDependentProperty"],
        "_private.materials._378": ["TransmissionApplications"],
        "_private.materials._379": ["VDI2736LubricantType"],
        "_private.materials._380": ["VehicleDynamicsProperties"],
        "_private.materials._381": ["WindTurbineStandards"],
        "_private.materials._382": ["WorkingCharacteristics"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractStressCyclesDataForAnSNCurveOfAPlasticMaterial",
    "AcousticRadiationEfficiency",
    "AcousticRadiationEfficiencyInputType",
    "AGMALubricantType",
    "AGMAMaterialApplications",
    "AGMAMaterialClasses",
    "AGMAMaterialGrade",
    "AirProperties",
    "BearingLubricationCondition",
    "BearingMaterial",
    "BearingMaterialDatabase",
    "BHCurveExtrapolationMethod",
    "BHCurveSpecification",
    "ComponentMaterialDatabase",
    "CompositeFatigueSafetyFactorItem",
    "CylindricalGearRatingMethods",
    "DensitySpecificationMethod",
    "FatigueSafetyFactorItem",
    "FatigueSafetyFactorItemBase",
    "Fluid",
    "FluidDatabase",
    "GearingTypes",
    "GeneralTransmissionProperties",
    "GreaseContaminationOptions",
    "HardnessType",
    "ISO76StaticSafetyFactorLimits",
    "ISOLubricantType",
    "LubricantDefinition",
    "LubricantDelivery",
    "LubricantViscosityClassAGMA",
    "LubricantViscosityClassification",
    "LubricantViscosityClassISO",
    "LubricantViscosityClassSAE",
    "LubricationDetail",
    "LubricationDetailDatabase",
    "Material",
    "MaterialDatabase",
    "MaterialsSettings",
    "MaterialsSettingsDatabase",
    "MaterialsSettingsItem",
    "MaterialStandards",
    "MetalPlasticType",
    "OilFiltrationOptions",
    "PressureViscosityCoefficientMethod",
    "QualityGrade",
    "SafetyFactorGroup",
    "SafetyFactorItem",
    "SNCurve",
    "SNCurvePoint",
    "SoundPressureEnclosure",
    "SoundPressureEnclosureType",
    "StressCyclesDataForTheBendingSNCurveOfAPlasticMaterial",
    "StressCyclesDataForTheContactSNCurveOfAPlasticMaterial",
    "TemperatureDependentProperty",
    "TransmissionApplications",
    "VDI2736LubricantType",
    "VehicleDynamicsProperties",
    "WindTurbineStandards",
    "WorkingCharacteristics",
)
