"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.bearings.tolerances._2109 import BearingConnectionComponent
    from mastapy._private.bearings.tolerances._2110 import InternalClearanceClass
    from mastapy._private.bearings.tolerances._2111 import BearingToleranceClass
    from mastapy._private.bearings.tolerances._2112 import (
        BearingToleranceDefinitionOptions,
    )
    from mastapy._private.bearings.tolerances._2113 import FitType
    from mastapy._private.bearings.tolerances._2114 import InnerRingTolerance
    from mastapy._private.bearings.tolerances._2115 import InnerSupportTolerance
    from mastapy._private.bearings.tolerances._2116 import InterferenceDetail
    from mastapy._private.bearings.tolerances._2117 import InterferenceTolerance
    from mastapy._private.bearings.tolerances._2118 import ITDesignation
    from mastapy._private.bearings.tolerances._2119 import MountingSleeveDiameterDetail
    from mastapy._private.bearings.tolerances._2120 import OuterRingTolerance
    from mastapy._private.bearings.tolerances._2121 import OuterSupportTolerance
    from mastapy._private.bearings.tolerances._2122 import RaceRoundnessAtAngle
    from mastapy._private.bearings.tolerances._2123 import RadialSpecificationMethod
    from mastapy._private.bearings.tolerances._2124 import RingDetail
    from mastapy._private.bearings.tolerances._2125 import RingTolerance
    from mastapy._private.bearings.tolerances._2126 import RoundnessSpecification
    from mastapy._private.bearings.tolerances._2127 import RoundnessSpecificationType
    from mastapy._private.bearings.tolerances._2128 import SupportDetail
    from mastapy._private.bearings.tolerances._2129 import SupportMaterialSource
    from mastapy._private.bearings.tolerances._2130 import SupportTolerance
    from mastapy._private.bearings.tolerances._2131 import (
        SupportToleranceLocationDesignation,
    )
    from mastapy._private.bearings.tolerances._2132 import ToleranceCombination
    from mastapy._private.bearings.tolerances._2133 import TypeOfFit
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.bearings.tolerances._2109": ["BearingConnectionComponent"],
        "_private.bearings.tolerances._2110": ["InternalClearanceClass"],
        "_private.bearings.tolerances._2111": ["BearingToleranceClass"],
        "_private.bearings.tolerances._2112": ["BearingToleranceDefinitionOptions"],
        "_private.bearings.tolerances._2113": ["FitType"],
        "_private.bearings.tolerances._2114": ["InnerRingTolerance"],
        "_private.bearings.tolerances._2115": ["InnerSupportTolerance"],
        "_private.bearings.tolerances._2116": ["InterferenceDetail"],
        "_private.bearings.tolerances._2117": ["InterferenceTolerance"],
        "_private.bearings.tolerances._2118": ["ITDesignation"],
        "_private.bearings.tolerances._2119": ["MountingSleeveDiameterDetail"],
        "_private.bearings.tolerances._2120": ["OuterRingTolerance"],
        "_private.bearings.tolerances._2121": ["OuterSupportTolerance"],
        "_private.bearings.tolerances._2122": ["RaceRoundnessAtAngle"],
        "_private.bearings.tolerances._2123": ["RadialSpecificationMethod"],
        "_private.bearings.tolerances._2124": ["RingDetail"],
        "_private.bearings.tolerances._2125": ["RingTolerance"],
        "_private.bearings.tolerances._2126": ["RoundnessSpecification"],
        "_private.bearings.tolerances._2127": ["RoundnessSpecificationType"],
        "_private.bearings.tolerances._2128": ["SupportDetail"],
        "_private.bearings.tolerances._2129": ["SupportMaterialSource"],
        "_private.bearings.tolerances._2130": ["SupportTolerance"],
        "_private.bearings.tolerances._2131": ["SupportToleranceLocationDesignation"],
        "_private.bearings.tolerances._2132": ["ToleranceCombination"],
        "_private.bearings.tolerances._2133": ["TypeOfFit"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BearingConnectionComponent",
    "InternalClearanceClass",
    "BearingToleranceClass",
    "BearingToleranceDefinitionOptions",
    "FitType",
    "InnerRingTolerance",
    "InnerSupportTolerance",
    "InterferenceDetail",
    "InterferenceTolerance",
    "ITDesignation",
    "MountingSleeveDiameterDetail",
    "OuterRingTolerance",
    "OuterSupportTolerance",
    "RaceRoundnessAtAngle",
    "RadialSpecificationMethod",
    "RingDetail",
    "RingTolerance",
    "RoundnessSpecification",
    "RoundnessSpecificationType",
    "SupportDetail",
    "SupportMaterialSource",
    "SupportTolerance",
    "SupportToleranceLocationDesignation",
    "ToleranceCombination",
    "TypeOfFit",
)
