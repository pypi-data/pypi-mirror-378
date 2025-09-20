"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.ltca._929 import ConicalGearFilletStressResults
    from mastapy._private.gears.ltca._930 import ConicalGearRootFilletStressResults
    from mastapy._private.gears.ltca._931 import ContactResultType
    from mastapy._private.gears.ltca._932 import CylindricalGearFilletNodeStressResults
    from mastapy._private.gears.ltca._933 import (
        CylindricalGearFilletNodeStressResultsColumn,
    )
    from mastapy._private.gears.ltca._934 import (
        CylindricalGearFilletNodeStressResultsRow,
    )
    from mastapy._private.gears.ltca._935 import CylindricalGearRootFilletStressResults
    from mastapy._private.gears.ltca._936 import (
        CylindricalMeshedGearLoadDistributionAnalysis,
    )
    from mastapy._private.gears.ltca._937 import GearBendingStiffness
    from mastapy._private.gears.ltca._938 import GearBendingStiffnessNode
    from mastapy._private.gears.ltca._939 import GearContactStiffness
    from mastapy._private.gears.ltca._940 import GearContactStiffnessNode
    from mastapy._private.gears.ltca._941 import GearFilletNodeStressResults
    from mastapy._private.gears.ltca._942 import GearFilletNodeStressResultsColumn
    from mastapy._private.gears.ltca._943 import GearFilletNodeStressResultsRow
    from mastapy._private.gears.ltca._944 import GearLoadDistributionAnalysis
    from mastapy._private.gears.ltca._945 import GearMeshLoadDistributionAnalysis
    from mastapy._private.gears.ltca._946 import GearMeshLoadDistributionAtRotation
    from mastapy._private.gears.ltca._947 import GearMeshLoadedContactLine
    from mastapy._private.gears.ltca._948 import GearMeshLoadedContactPoint
    from mastapy._private.gears.ltca._949 import GearRootFilletStressResults
    from mastapy._private.gears.ltca._950 import GearSetLoadDistributionAnalysis
    from mastapy._private.gears.ltca._951 import GearStiffness
    from mastapy._private.gears.ltca._952 import GearStiffnessNode
    from mastapy._private.gears.ltca._953 import (
        MeshedGearLoadDistributionAnalysisAtRotation,
    )
    from mastapy._private.gears.ltca._954 import UseAdvancedLTCAOptions
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.ltca._929": ["ConicalGearFilletStressResults"],
        "_private.gears.ltca._930": ["ConicalGearRootFilletStressResults"],
        "_private.gears.ltca._931": ["ContactResultType"],
        "_private.gears.ltca._932": ["CylindricalGearFilletNodeStressResults"],
        "_private.gears.ltca._933": ["CylindricalGearFilletNodeStressResultsColumn"],
        "_private.gears.ltca._934": ["CylindricalGearFilletNodeStressResultsRow"],
        "_private.gears.ltca._935": ["CylindricalGearRootFilletStressResults"],
        "_private.gears.ltca._936": ["CylindricalMeshedGearLoadDistributionAnalysis"],
        "_private.gears.ltca._937": ["GearBendingStiffness"],
        "_private.gears.ltca._938": ["GearBendingStiffnessNode"],
        "_private.gears.ltca._939": ["GearContactStiffness"],
        "_private.gears.ltca._940": ["GearContactStiffnessNode"],
        "_private.gears.ltca._941": ["GearFilletNodeStressResults"],
        "_private.gears.ltca._942": ["GearFilletNodeStressResultsColumn"],
        "_private.gears.ltca._943": ["GearFilletNodeStressResultsRow"],
        "_private.gears.ltca._944": ["GearLoadDistributionAnalysis"],
        "_private.gears.ltca._945": ["GearMeshLoadDistributionAnalysis"],
        "_private.gears.ltca._946": ["GearMeshLoadDistributionAtRotation"],
        "_private.gears.ltca._947": ["GearMeshLoadedContactLine"],
        "_private.gears.ltca._948": ["GearMeshLoadedContactPoint"],
        "_private.gears.ltca._949": ["GearRootFilletStressResults"],
        "_private.gears.ltca._950": ["GearSetLoadDistributionAnalysis"],
        "_private.gears.ltca._951": ["GearStiffness"],
        "_private.gears.ltca._952": ["GearStiffnessNode"],
        "_private.gears.ltca._953": ["MeshedGearLoadDistributionAnalysisAtRotation"],
        "_private.gears.ltca._954": ["UseAdvancedLTCAOptions"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConicalGearFilletStressResults",
    "ConicalGearRootFilletStressResults",
    "ContactResultType",
    "CylindricalGearFilletNodeStressResults",
    "CylindricalGearFilletNodeStressResultsColumn",
    "CylindricalGearFilletNodeStressResultsRow",
    "CylindricalGearRootFilletStressResults",
    "CylindricalMeshedGearLoadDistributionAnalysis",
    "GearBendingStiffness",
    "GearBendingStiffnessNode",
    "GearContactStiffness",
    "GearContactStiffnessNode",
    "GearFilletNodeStressResults",
    "GearFilletNodeStressResultsColumn",
    "GearFilletNodeStressResultsRow",
    "GearLoadDistributionAnalysis",
    "GearMeshLoadDistributionAnalysis",
    "GearMeshLoadDistributionAtRotation",
    "GearMeshLoadedContactLine",
    "GearMeshLoadedContactPoint",
    "GearRootFilletStressResults",
    "GearSetLoadDistributionAnalysis",
    "GearStiffness",
    "GearStiffnessNode",
    "MeshedGearLoadDistributionAnalysisAtRotation",
    "UseAdvancedLTCAOptions",
)
