"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.cylindrical._713 import (
        CutterFlankSections,
    )
    from mastapy._private.gears.manufacturing.cylindrical._714 import (
        CylindricalCutterDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical._715 import (
        CylindricalGearBlank,
    )
    from mastapy._private.gears.manufacturing.cylindrical._716 import (
        CylindricalGearManufacturingConfig,
    )
    from mastapy._private.gears.manufacturing.cylindrical._717 import (
        CylindricalGearSpecifiedMicroGeometry,
    )
    from mastapy._private.gears.manufacturing.cylindrical._718 import (
        CylindricalGearSpecifiedProfile,
    )
    from mastapy._private.gears.manufacturing.cylindrical._719 import (
        CylindricalHobDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical._720 import (
        CylindricalManufacturedGearDutyCycle,
    )
    from mastapy._private.gears.manufacturing.cylindrical._721 import (
        CylindricalManufacturedGearLoadCase,
    )
    from mastapy._private.gears.manufacturing.cylindrical._722 import (
        CylindricalManufacturedGearMeshDutyCycle,
    )
    from mastapy._private.gears.manufacturing.cylindrical._723 import (
        CylindricalManufacturedGearMeshLoadCase,
    )
    from mastapy._private.gears.manufacturing.cylindrical._724 import (
        CylindricalManufacturedGearSetDutyCycle,
    )
    from mastapy._private.gears.manufacturing.cylindrical._725 import (
        CylindricalManufacturedGearSetLoadCase,
    )
    from mastapy._private.gears.manufacturing.cylindrical._726 import (
        CylindricalMeshManufacturingConfig,
    )
    from mastapy._private.gears.manufacturing.cylindrical._727 import (
        CylindricalMftFinishingMethods,
    )
    from mastapy._private.gears.manufacturing.cylindrical._728 import (
        CylindricalMftRoughingMethods,
    )
    from mastapy._private.gears.manufacturing.cylindrical._729 import (
        CylindricalSetManufacturingConfig,
    )
    from mastapy._private.gears.manufacturing.cylindrical._730 import (
        CylindricalShaperDatabase,
    )
    from mastapy._private.gears.manufacturing.cylindrical._731 import Flank
    from mastapy._private.gears.manufacturing.cylindrical._732 import (
        GearManufacturingConfigurationViewModel,
    )
    from mastapy._private.gears.manufacturing.cylindrical._733 import (
        GearManufacturingConfigurationViewModelPlaceholder,
    )
    from mastapy._private.gears.manufacturing.cylindrical._734 import (
        GearSetConfigViewModel,
    )
    from mastapy._private.gears.manufacturing.cylindrical._735 import HobEdgeTypes
    from mastapy._private.gears.manufacturing.cylindrical._736 import (
        LeadModificationSegment,
    )
    from mastapy._private.gears.manufacturing.cylindrical._737 import (
        MicroGeometryInputs,
    )
    from mastapy._private.gears.manufacturing.cylindrical._738 import (
        MicroGeometryInputsLead,
    )
    from mastapy._private.gears.manufacturing.cylindrical._739 import (
        MicroGeometryInputsProfile,
    )
    from mastapy._private.gears.manufacturing.cylindrical._740 import (
        ModificationSegment,
    )
    from mastapy._private.gears.manufacturing.cylindrical._741 import (
        ProfileModificationSegment,
    )
    from mastapy._private.gears.manufacturing.cylindrical._742 import (
        SuitableCutterSetup,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.cylindrical._713": ["CutterFlankSections"],
        "_private.gears.manufacturing.cylindrical._714": ["CylindricalCutterDatabase"],
        "_private.gears.manufacturing.cylindrical._715": ["CylindricalGearBlank"],
        "_private.gears.manufacturing.cylindrical._716": [
            "CylindricalGearManufacturingConfig"
        ],
        "_private.gears.manufacturing.cylindrical._717": [
            "CylindricalGearSpecifiedMicroGeometry"
        ],
        "_private.gears.manufacturing.cylindrical._718": [
            "CylindricalGearSpecifiedProfile"
        ],
        "_private.gears.manufacturing.cylindrical._719": ["CylindricalHobDatabase"],
        "_private.gears.manufacturing.cylindrical._720": [
            "CylindricalManufacturedGearDutyCycle"
        ],
        "_private.gears.manufacturing.cylindrical._721": [
            "CylindricalManufacturedGearLoadCase"
        ],
        "_private.gears.manufacturing.cylindrical._722": [
            "CylindricalManufacturedGearMeshDutyCycle"
        ],
        "_private.gears.manufacturing.cylindrical._723": [
            "CylindricalManufacturedGearMeshLoadCase"
        ],
        "_private.gears.manufacturing.cylindrical._724": [
            "CylindricalManufacturedGearSetDutyCycle"
        ],
        "_private.gears.manufacturing.cylindrical._725": [
            "CylindricalManufacturedGearSetLoadCase"
        ],
        "_private.gears.manufacturing.cylindrical._726": [
            "CylindricalMeshManufacturingConfig"
        ],
        "_private.gears.manufacturing.cylindrical._727": [
            "CylindricalMftFinishingMethods"
        ],
        "_private.gears.manufacturing.cylindrical._728": [
            "CylindricalMftRoughingMethods"
        ],
        "_private.gears.manufacturing.cylindrical._729": [
            "CylindricalSetManufacturingConfig"
        ],
        "_private.gears.manufacturing.cylindrical._730": ["CylindricalShaperDatabase"],
        "_private.gears.manufacturing.cylindrical._731": ["Flank"],
        "_private.gears.manufacturing.cylindrical._732": [
            "GearManufacturingConfigurationViewModel"
        ],
        "_private.gears.manufacturing.cylindrical._733": [
            "GearManufacturingConfigurationViewModelPlaceholder"
        ],
        "_private.gears.manufacturing.cylindrical._734": ["GearSetConfigViewModel"],
        "_private.gears.manufacturing.cylindrical._735": ["HobEdgeTypes"],
        "_private.gears.manufacturing.cylindrical._736": ["LeadModificationSegment"],
        "_private.gears.manufacturing.cylindrical._737": ["MicroGeometryInputs"],
        "_private.gears.manufacturing.cylindrical._738": ["MicroGeometryInputsLead"],
        "_private.gears.manufacturing.cylindrical._739": ["MicroGeometryInputsProfile"],
        "_private.gears.manufacturing.cylindrical._740": ["ModificationSegment"],
        "_private.gears.manufacturing.cylindrical._741": ["ProfileModificationSegment"],
        "_private.gears.manufacturing.cylindrical._742": ["SuitableCutterSetup"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CutterFlankSections",
    "CylindricalCutterDatabase",
    "CylindricalGearBlank",
    "CylindricalGearManufacturingConfig",
    "CylindricalGearSpecifiedMicroGeometry",
    "CylindricalGearSpecifiedProfile",
    "CylindricalHobDatabase",
    "CylindricalManufacturedGearDutyCycle",
    "CylindricalManufacturedGearLoadCase",
    "CylindricalManufacturedGearMeshDutyCycle",
    "CylindricalManufacturedGearMeshLoadCase",
    "CylindricalManufacturedGearSetDutyCycle",
    "CylindricalManufacturedGearSetLoadCase",
    "CylindricalMeshManufacturingConfig",
    "CylindricalMftFinishingMethods",
    "CylindricalMftRoughingMethods",
    "CylindricalSetManufacturingConfig",
    "CylindricalShaperDatabase",
    "Flank",
    "GearManufacturingConfigurationViewModel",
    "GearManufacturingConfigurationViewModelPlaceholder",
    "GearSetConfigViewModel",
    "HobEdgeTypes",
    "LeadModificationSegment",
    "MicroGeometryInputs",
    "MicroGeometryInputsLead",
    "MicroGeometryInputsProfile",
    "ModificationSegment",
    "ProfileModificationSegment",
    "SuitableCutterSetup",
)
