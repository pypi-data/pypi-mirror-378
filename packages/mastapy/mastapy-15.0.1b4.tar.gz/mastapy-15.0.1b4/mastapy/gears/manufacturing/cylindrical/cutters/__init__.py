"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.cylindrical.cutters._807 import (
        CurveInLinkedList,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._808 import (
        CustomisableEdgeProfile,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._809 import (
        CylindricalFormedWheelGrinderDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._810 import (
        CylindricalGearAbstractCutterDesign,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._811 import (
        CylindricalGearFormGrindingWheel,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._812 import (
        CylindricalGearGrindingWorm,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._813 import (
        CylindricalGearHobDesign,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._814 import (
        CylindricalGearPlungeShaver,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._815 import (
        CylindricalGearPlungeShaverDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._816 import (
        CylindricalGearRackDesign,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._817 import (
        CylindricalGearRealCutterDesign,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._818 import (
        CylindricalGearShaper,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._819 import (
        CylindricalGearShaver,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._820 import (
        CylindricalGearShaverDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._821 import (
        CylindricalWormGrinderDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._822 import (
        InvoluteCutterDesign,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._823 import (
        MutableCommon,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._824 import (
        MutableCurve,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._825 import (
        MutableFillet,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutters._826 import (
        RoughCutterCreationSettings,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.cylindrical.cutters._807": ["CurveInLinkedList"],
        "_private.gears.manufacturing.cylindrical.cutters._808": [
            "CustomisableEdgeProfile"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._809": [
            "CylindricalFormedWheelGrinderDatabase"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._810": [
            "CylindricalGearAbstractCutterDesign"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._811": [
            "CylindricalGearFormGrindingWheel"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._812": [
            "CylindricalGearGrindingWorm"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._813": [
            "CylindricalGearHobDesign"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._814": [
            "CylindricalGearPlungeShaver"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._815": [
            "CylindricalGearPlungeShaverDatabase"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._816": [
            "CylindricalGearRackDesign"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._817": [
            "CylindricalGearRealCutterDesign"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._818": [
            "CylindricalGearShaper"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._819": [
            "CylindricalGearShaver"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._820": [
            "CylindricalGearShaverDatabase"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._821": [
            "CylindricalWormGrinderDatabase"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._822": [
            "InvoluteCutterDesign"
        ],
        "_private.gears.manufacturing.cylindrical.cutters._823": ["MutableCommon"],
        "_private.gears.manufacturing.cylindrical.cutters._824": ["MutableCurve"],
        "_private.gears.manufacturing.cylindrical.cutters._825": ["MutableFillet"],
        "_private.gears.manufacturing.cylindrical.cutters._826": [
            "RoughCutterCreationSettings"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CurveInLinkedList",
    "CustomisableEdgeProfile",
    "CylindricalFormedWheelGrinderDatabase",
    "CylindricalGearAbstractCutterDesign",
    "CylindricalGearFormGrindingWheel",
    "CylindricalGearGrindingWorm",
    "CylindricalGearHobDesign",
    "CylindricalGearPlungeShaver",
    "CylindricalGearPlungeShaverDatabase",
    "CylindricalGearRackDesign",
    "CylindricalGearRealCutterDesign",
    "CylindricalGearShaper",
    "CylindricalGearShaver",
    "CylindricalGearShaverDatabase",
    "CylindricalWormGrinderDatabase",
    "InvoluteCutterDesign",
    "MutableCommon",
    "MutableCurve",
    "MutableFillet",
    "RoughCutterCreationSettings",
)
