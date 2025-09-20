"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.materials._675 import AGMACylindricalGearMaterial
    from mastapy._private.gears.materials._676 import (
        BenedictAndKelleyCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._677 import BevelGearAbstractMaterialDatabase
    from mastapy._private.gears.materials._678 import BevelGearISOMaterial
    from mastapy._private.gears.materials._679 import BevelGearISOMaterialDatabase
    from mastapy._private.gears.materials._680 import BevelGearMaterial
    from mastapy._private.gears.materials._681 import BevelGearMaterialDatabase
    from mastapy._private.gears.materials._682 import CoefficientOfFrictionCalculator
    from mastapy._private.gears.materials._683 import (
        CylindricalGearAGMAMaterialDatabase,
    )
    from mastapy._private.gears.materials._684 import CylindricalGearISOMaterialDatabase
    from mastapy._private.gears.materials._685 import CylindricalGearMaterial
    from mastapy._private.gears.materials._686 import CylindricalGearMaterialDatabase
    from mastapy._private.gears.materials._687 import (
        CylindricalGearPlasticMaterialDatabase,
    )
    from mastapy._private.gears.materials._688 import (
        DrozdovAndGavrikovCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._689 import GearMaterial
    from mastapy._private.gears.materials._690 import GearMaterialDatabase
    from mastapy._private.gears.materials._691 import (
        GearMaterialExpertSystemFactorSettings,
    )
    from mastapy._private.gears.materials._692 import (
        InstantaneousCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._693 import (
        ISO14179Part1CoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._694 import (
        ISO14179Part2CoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._695 import (
        ISO14179Part2CoefficientOfFrictionCalculatorBase,
    )
    from mastapy._private.gears.materials._696 import (
        ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification,
    )
    from mastapy._private.gears.materials._697 import ISOCylindricalGearMaterial
    from mastapy._private.gears.materials._698 import (
        ISOTC60CoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._699 import (
        ISOTR1417912001CoefficientOfFrictionConstants,
    )
    from mastapy._private.gears.materials._700 import (
        ISOTR1417912001CoefficientOfFrictionConstantsDatabase,
    )
    from mastapy._private.gears.materials._701 import (
        KlingelnbergConicalGearMaterialDatabase,
    )
    from mastapy._private.gears.materials._702 import (
        KlingelnbergCycloPalloidConicalGearMaterial,
    )
    from mastapy._private.gears.materials._703 import ManufactureRating
    from mastapy._private.gears.materials._704 import (
        MisharinCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._705 import (
        ODonoghueAndCameronCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._706 import PlasticCylindricalGearMaterial
    from mastapy._private.gears.materials._707 import PlasticSNCurve
    from mastapy._private.gears.materials._708 import RatingMethods
    from mastapy._private.gears.materials._709 import RawMaterial
    from mastapy._private.gears.materials._710 import RawMaterialDatabase
    from mastapy._private.gears.materials._711 import (
        ScriptCoefficientOfFrictionCalculator,
    )
    from mastapy._private.gears.materials._712 import SNCurveDefinition
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.materials._675": ["AGMACylindricalGearMaterial"],
        "_private.gears.materials._676": [
            "BenedictAndKelleyCoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._677": ["BevelGearAbstractMaterialDatabase"],
        "_private.gears.materials._678": ["BevelGearISOMaterial"],
        "_private.gears.materials._679": ["BevelGearISOMaterialDatabase"],
        "_private.gears.materials._680": ["BevelGearMaterial"],
        "_private.gears.materials._681": ["BevelGearMaterialDatabase"],
        "_private.gears.materials._682": ["CoefficientOfFrictionCalculator"],
        "_private.gears.materials._683": ["CylindricalGearAGMAMaterialDatabase"],
        "_private.gears.materials._684": ["CylindricalGearISOMaterialDatabase"],
        "_private.gears.materials._685": ["CylindricalGearMaterial"],
        "_private.gears.materials._686": ["CylindricalGearMaterialDatabase"],
        "_private.gears.materials._687": ["CylindricalGearPlasticMaterialDatabase"],
        "_private.gears.materials._688": [
            "DrozdovAndGavrikovCoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._689": ["GearMaterial"],
        "_private.gears.materials._690": ["GearMaterialDatabase"],
        "_private.gears.materials._691": ["GearMaterialExpertSystemFactorSettings"],
        "_private.gears.materials._692": [
            "InstantaneousCoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._693": [
            "ISO14179Part1CoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._694": [
            "ISO14179Part2CoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._695": [
            "ISO14179Part2CoefficientOfFrictionCalculatorBase"
        ],
        "_private.gears.materials._696": [
            "ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification"
        ],
        "_private.gears.materials._697": ["ISOCylindricalGearMaterial"],
        "_private.gears.materials._698": ["ISOTC60CoefficientOfFrictionCalculator"],
        "_private.gears.materials._699": [
            "ISOTR1417912001CoefficientOfFrictionConstants"
        ],
        "_private.gears.materials._700": [
            "ISOTR1417912001CoefficientOfFrictionConstantsDatabase"
        ],
        "_private.gears.materials._701": ["KlingelnbergConicalGearMaterialDatabase"],
        "_private.gears.materials._702": [
            "KlingelnbergCycloPalloidConicalGearMaterial"
        ],
        "_private.gears.materials._703": ["ManufactureRating"],
        "_private.gears.materials._704": ["MisharinCoefficientOfFrictionCalculator"],
        "_private.gears.materials._705": [
            "ODonoghueAndCameronCoefficientOfFrictionCalculator"
        ],
        "_private.gears.materials._706": ["PlasticCylindricalGearMaterial"],
        "_private.gears.materials._707": ["PlasticSNCurve"],
        "_private.gears.materials._708": ["RatingMethods"],
        "_private.gears.materials._709": ["RawMaterial"],
        "_private.gears.materials._710": ["RawMaterialDatabase"],
        "_private.gears.materials._711": ["ScriptCoefficientOfFrictionCalculator"],
        "_private.gears.materials._712": ["SNCurveDefinition"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AGMACylindricalGearMaterial",
    "BenedictAndKelleyCoefficientOfFrictionCalculator",
    "BevelGearAbstractMaterialDatabase",
    "BevelGearISOMaterial",
    "BevelGearISOMaterialDatabase",
    "BevelGearMaterial",
    "BevelGearMaterialDatabase",
    "CoefficientOfFrictionCalculator",
    "CylindricalGearAGMAMaterialDatabase",
    "CylindricalGearISOMaterialDatabase",
    "CylindricalGearMaterial",
    "CylindricalGearMaterialDatabase",
    "CylindricalGearPlasticMaterialDatabase",
    "DrozdovAndGavrikovCoefficientOfFrictionCalculator",
    "GearMaterial",
    "GearMaterialDatabase",
    "GearMaterialExpertSystemFactorSettings",
    "InstantaneousCoefficientOfFrictionCalculator",
    "ISO14179Part1CoefficientOfFrictionCalculator",
    "ISO14179Part2CoefficientOfFrictionCalculator",
    "ISO14179Part2CoefficientOfFrictionCalculatorBase",
    "ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification",
    "ISOCylindricalGearMaterial",
    "ISOTC60CoefficientOfFrictionCalculator",
    "ISOTR1417912001CoefficientOfFrictionConstants",
    "ISOTR1417912001CoefficientOfFrictionConstantsDatabase",
    "KlingelnbergConicalGearMaterialDatabase",
    "KlingelnbergCycloPalloidConicalGearMaterial",
    "ManufactureRating",
    "MisharinCoefficientOfFrictionCalculator",
    "ODonoghueAndCameronCoefficientOfFrictionCalculator",
    "PlasticCylindricalGearMaterial",
    "PlasticSNCurve",
    "RatingMethods",
    "RawMaterial",
    "RawMaterialDatabase",
    "ScriptCoefficientOfFrictionCalculator",
    "SNCurveDefinition",
)
