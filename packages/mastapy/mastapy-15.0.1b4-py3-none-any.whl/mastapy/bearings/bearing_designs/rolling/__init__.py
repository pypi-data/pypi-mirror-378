"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.bearings.bearing_designs.rolling._2350 import (
        AngularContactBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2351 import (
        AngularContactThrustBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2352 import (
        AsymmetricSphericalRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2353 import (
        AxialThrustCylindricalRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2354 import (
        AxialThrustNeedleRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2355 import BallBearing
    from mastapy._private.bearings.bearing_designs.rolling._2356 import (
        BallBearingShoulderDefinition,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2357 import (
        BarrelRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2358 import (
        BearingProtection,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2359 import (
        BearingProtectionDetailsModifier,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2360 import (
        BearingProtectionLevel,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2361 import (
        BearingTypeExtraInformation,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2362 import CageBridgeShape
    from mastapy._private.bearings.bearing_designs.rolling._2363 import (
        CrossedRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2364 import (
        CylindricalRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2365 import (
        DeepGrooveBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2366 import DiameterSeries
    from mastapy._private.bearings.bearing_designs.rolling._2367 import (
        FatigueLoadLimitCalculationMethodEnum,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2368 import (
        FourPointContactAngleDefinition,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2369 import (
        FourPointContactBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2370 import (
        GeometricConstants,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2371 import (
        GeometricConstantsForRollingFrictionalMoments,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2372 import (
        GeometricConstantsForSlidingFrictionalMoments,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2373 import HeightSeries
    from mastapy._private.bearings.bearing_designs.rolling._2374 import (
        MultiPointContactBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2375 import (
        NeedleRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2376 import (
        NonBarrelRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2377 import RollerBearing
    from mastapy._private.bearings.bearing_designs.rolling._2378 import RollerEndShape
    from mastapy._private.bearings.bearing_designs.rolling._2379 import RollerRibDetail
    from mastapy._private.bearings.bearing_designs.rolling._2380 import RollingBearing
    from mastapy._private.bearings.bearing_designs.rolling._2381 import (
        RollingBearingElement,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2382 import (
        SelfAligningBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2383 import (
        SKFSealFrictionalMomentConstants,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2384 import SleeveType
    from mastapy._private.bearings.bearing_designs.rolling._2385 import (
        SphericalRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2386 import (
        SphericalRollerThrustBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2387 import (
        TaperRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2388 import (
        ThreePointContactBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2389 import (
        ThrustBallBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2390 import (
        ToroidalRollerBearing,
    )
    from mastapy._private.bearings.bearing_designs.rolling._2391 import WidthSeries
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.bearings.bearing_designs.rolling._2350": [
            "AngularContactBallBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2351": [
            "AngularContactThrustBallBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2352": [
            "AsymmetricSphericalRollerBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2353": [
            "AxialThrustCylindricalRollerBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2354": [
            "AxialThrustNeedleRollerBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2355": ["BallBearing"],
        "_private.bearings.bearing_designs.rolling._2356": [
            "BallBearingShoulderDefinition"
        ],
        "_private.bearings.bearing_designs.rolling._2357": ["BarrelRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2358": ["BearingProtection"],
        "_private.bearings.bearing_designs.rolling._2359": [
            "BearingProtectionDetailsModifier"
        ],
        "_private.bearings.bearing_designs.rolling._2360": ["BearingProtectionLevel"],
        "_private.bearings.bearing_designs.rolling._2361": [
            "BearingTypeExtraInformation"
        ],
        "_private.bearings.bearing_designs.rolling._2362": ["CageBridgeShape"],
        "_private.bearings.bearing_designs.rolling._2363": ["CrossedRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2364": ["CylindricalRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2365": ["DeepGrooveBallBearing"],
        "_private.bearings.bearing_designs.rolling._2366": ["DiameterSeries"],
        "_private.bearings.bearing_designs.rolling._2367": [
            "FatigueLoadLimitCalculationMethodEnum"
        ],
        "_private.bearings.bearing_designs.rolling._2368": [
            "FourPointContactAngleDefinition"
        ],
        "_private.bearings.bearing_designs.rolling._2369": [
            "FourPointContactBallBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2370": ["GeometricConstants"],
        "_private.bearings.bearing_designs.rolling._2371": [
            "GeometricConstantsForRollingFrictionalMoments"
        ],
        "_private.bearings.bearing_designs.rolling._2372": [
            "GeometricConstantsForSlidingFrictionalMoments"
        ],
        "_private.bearings.bearing_designs.rolling._2373": ["HeightSeries"],
        "_private.bearings.bearing_designs.rolling._2374": [
            "MultiPointContactBallBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2375": ["NeedleRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2376": ["NonBarrelRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2377": ["RollerBearing"],
        "_private.bearings.bearing_designs.rolling._2378": ["RollerEndShape"],
        "_private.bearings.bearing_designs.rolling._2379": ["RollerRibDetail"],
        "_private.bearings.bearing_designs.rolling._2380": ["RollingBearing"],
        "_private.bearings.bearing_designs.rolling._2381": ["RollingBearingElement"],
        "_private.bearings.bearing_designs.rolling._2382": ["SelfAligningBallBearing"],
        "_private.bearings.bearing_designs.rolling._2383": [
            "SKFSealFrictionalMomentConstants"
        ],
        "_private.bearings.bearing_designs.rolling._2384": ["SleeveType"],
        "_private.bearings.bearing_designs.rolling._2385": ["SphericalRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2386": [
            "SphericalRollerThrustBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2387": ["TaperRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2388": [
            "ThreePointContactBallBearing"
        ],
        "_private.bearings.bearing_designs.rolling._2389": ["ThrustBallBearing"],
        "_private.bearings.bearing_designs.rolling._2390": ["ToroidalRollerBearing"],
        "_private.bearings.bearing_designs.rolling._2391": ["WidthSeries"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AngularContactBallBearing",
    "AngularContactThrustBallBearing",
    "AsymmetricSphericalRollerBearing",
    "AxialThrustCylindricalRollerBearing",
    "AxialThrustNeedleRollerBearing",
    "BallBearing",
    "BallBearingShoulderDefinition",
    "BarrelRollerBearing",
    "BearingProtection",
    "BearingProtectionDetailsModifier",
    "BearingProtectionLevel",
    "BearingTypeExtraInformation",
    "CageBridgeShape",
    "CrossedRollerBearing",
    "CylindricalRollerBearing",
    "DeepGrooveBallBearing",
    "DiameterSeries",
    "FatigueLoadLimitCalculationMethodEnum",
    "FourPointContactAngleDefinition",
    "FourPointContactBallBearing",
    "GeometricConstants",
    "GeometricConstantsForRollingFrictionalMoments",
    "GeometricConstantsForSlidingFrictionalMoments",
    "HeightSeries",
    "MultiPointContactBallBearing",
    "NeedleRollerBearing",
    "NonBarrelRollerBearing",
    "RollerBearing",
    "RollerEndShape",
    "RollerRibDetail",
    "RollingBearing",
    "RollingBearingElement",
    "SelfAligningBallBearing",
    "SKFSealFrictionalMomentConstants",
    "SleeveType",
    "SphericalRollerBearing",
    "SphericalRollerThrustBearing",
    "TaperRollerBearing",
    "ThreePointContactBallBearing",
    "ThrustBallBearing",
    "ToroidalRollerBearing",
    "WidthSeries",
)
