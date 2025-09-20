"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.couplings._2820 import BeltDrive
    from mastapy._private.system_model.part_model.couplings._2821 import BeltDriveType
    from mastapy._private.system_model.part_model.couplings._2822 import Clutch
    from mastapy._private.system_model.part_model.couplings._2823 import ClutchHalf
    from mastapy._private.system_model.part_model.couplings._2824 import ClutchType
    from mastapy._private.system_model.part_model.couplings._2825 import ConceptCoupling
    from mastapy._private.system_model.part_model.couplings._2826 import (
        ConceptCouplingHalf,
    )
    from mastapy._private.system_model.part_model.couplings._2827 import (
        ConceptCouplingHalfPositioning,
    )
    from mastapy._private.system_model.part_model.couplings._2828 import Coupling
    from mastapy._private.system_model.part_model.couplings._2829 import CouplingHalf
    from mastapy._private.system_model.part_model.couplings._2830 import (
        CrowningSpecification,
    )
    from mastapy._private.system_model.part_model.couplings._2831 import CVT
    from mastapy._private.system_model.part_model.couplings._2832 import CVTPulley
    from mastapy._private.system_model.part_model.couplings._2833 import (
        PartToPartShearCoupling,
    )
    from mastapy._private.system_model.part_model.couplings._2834 import (
        PartToPartShearCouplingHalf,
    )
    from mastapy._private.system_model.part_model.couplings._2835 import (
        PitchErrorFlankOptions,
    )
    from mastapy._private.system_model.part_model.couplings._2836 import Pulley
    from mastapy._private.system_model.part_model.couplings._2837 import (
        RigidConnectorSettings,
    )
    from mastapy._private.system_model.part_model.couplings._2838 import (
        RigidConnectorStiffnessType,
    )
    from mastapy._private.system_model.part_model.couplings._2839 import (
        RigidConnectorTiltStiffnessTypes,
    )
    from mastapy._private.system_model.part_model.couplings._2840 import (
        RigidConnectorToothLocation,
    )
    from mastapy._private.system_model.part_model.couplings._2841 import (
        RigidConnectorToothSpacingType,
    )
    from mastapy._private.system_model.part_model.couplings._2842 import (
        RigidConnectorTypes,
    )
    from mastapy._private.system_model.part_model.couplings._2843 import RollingRing
    from mastapy._private.system_model.part_model.couplings._2844 import (
        RollingRingAssembly,
    )
    from mastapy._private.system_model.part_model.couplings._2845 import (
        ShaftHubConnection,
    )
    from mastapy._private.system_model.part_model.couplings._2846 import (
        SplineFitOptions,
    )
    from mastapy._private.system_model.part_model.couplings._2847 import (
        SplineHalfManufacturingError,
    )
    from mastapy._private.system_model.part_model.couplings._2848 import (
        SplineLeadRelief,
    )
    from mastapy._private.system_model.part_model.couplings._2849 import (
        SplinePitchErrorInputType,
    )
    from mastapy._private.system_model.part_model.couplings._2850 import (
        SplinePitchErrorOptions,
    )
    from mastapy._private.system_model.part_model.couplings._2851 import SpringDamper
    from mastapy._private.system_model.part_model.couplings._2852 import (
        SpringDamperHalf,
    )
    from mastapy._private.system_model.part_model.couplings._2853 import Synchroniser
    from mastapy._private.system_model.part_model.couplings._2854 import (
        SynchroniserCone,
    )
    from mastapy._private.system_model.part_model.couplings._2855 import (
        SynchroniserHalf,
    )
    from mastapy._private.system_model.part_model.couplings._2856 import (
        SynchroniserPart,
    )
    from mastapy._private.system_model.part_model.couplings._2857 import (
        SynchroniserSleeve,
    )
    from mastapy._private.system_model.part_model.couplings._2858 import TorqueConverter
    from mastapy._private.system_model.part_model.couplings._2859 import (
        TorqueConverterPump,
    )
    from mastapy._private.system_model.part_model.couplings._2860 import (
        TorqueConverterSpeedRatio,
    )
    from mastapy._private.system_model.part_model.couplings._2861 import (
        TorqueConverterTurbine,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.couplings._2820": ["BeltDrive"],
        "_private.system_model.part_model.couplings._2821": ["BeltDriveType"],
        "_private.system_model.part_model.couplings._2822": ["Clutch"],
        "_private.system_model.part_model.couplings._2823": ["ClutchHalf"],
        "_private.system_model.part_model.couplings._2824": ["ClutchType"],
        "_private.system_model.part_model.couplings._2825": ["ConceptCoupling"],
        "_private.system_model.part_model.couplings._2826": ["ConceptCouplingHalf"],
        "_private.system_model.part_model.couplings._2827": [
            "ConceptCouplingHalfPositioning"
        ],
        "_private.system_model.part_model.couplings._2828": ["Coupling"],
        "_private.system_model.part_model.couplings._2829": ["CouplingHalf"],
        "_private.system_model.part_model.couplings._2830": ["CrowningSpecification"],
        "_private.system_model.part_model.couplings._2831": ["CVT"],
        "_private.system_model.part_model.couplings._2832": ["CVTPulley"],
        "_private.system_model.part_model.couplings._2833": ["PartToPartShearCoupling"],
        "_private.system_model.part_model.couplings._2834": [
            "PartToPartShearCouplingHalf"
        ],
        "_private.system_model.part_model.couplings._2835": ["PitchErrorFlankOptions"],
        "_private.system_model.part_model.couplings._2836": ["Pulley"],
        "_private.system_model.part_model.couplings._2837": ["RigidConnectorSettings"],
        "_private.system_model.part_model.couplings._2838": [
            "RigidConnectorStiffnessType"
        ],
        "_private.system_model.part_model.couplings._2839": [
            "RigidConnectorTiltStiffnessTypes"
        ],
        "_private.system_model.part_model.couplings._2840": [
            "RigidConnectorToothLocation"
        ],
        "_private.system_model.part_model.couplings._2841": [
            "RigidConnectorToothSpacingType"
        ],
        "_private.system_model.part_model.couplings._2842": ["RigidConnectorTypes"],
        "_private.system_model.part_model.couplings._2843": ["RollingRing"],
        "_private.system_model.part_model.couplings._2844": ["RollingRingAssembly"],
        "_private.system_model.part_model.couplings._2845": ["ShaftHubConnection"],
        "_private.system_model.part_model.couplings._2846": ["SplineFitOptions"],
        "_private.system_model.part_model.couplings._2847": [
            "SplineHalfManufacturingError"
        ],
        "_private.system_model.part_model.couplings._2848": ["SplineLeadRelief"],
        "_private.system_model.part_model.couplings._2849": [
            "SplinePitchErrorInputType"
        ],
        "_private.system_model.part_model.couplings._2850": ["SplinePitchErrorOptions"],
        "_private.system_model.part_model.couplings._2851": ["SpringDamper"],
        "_private.system_model.part_model.couplings._2852": ["SpringDamperHalf"],
        "_private.system_model.part_model.couplings._2853": ["Synchroniser"],
        "_private.system_model.part_model.couplings._2854": ["SynchroniserCone"],
        "_private.system_model.part_model.couplings._2855": ["SynchroniserHalf"],
        "_private.system_model.part_model.couplings._2856": ["SynchroniserPart"],
        "_private.system_model.part_model.couplings._2857": ["SynchroniserSleeve"],
        "_private.system_model.part_model.couplings._2858": ["TorqueConverter"],
        "_private.system_model.part_model.couplings._2859": ["TorqueConverterPump"],
        "_private.system_model.part_model.couplings._2860": [
            "TorqueConverterSpeedRatio"
        ],
        "_private.system_model.part_model.couplings._2861": ["TorqueConverterTurbine"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BeltDrive",
    "BeltDriveType",
    "Clutch",
    "ClutchHalf",
    "ClutchType",
    "ConceptCoupling",
    "ConceptCouplingHalf",
    "ConceptCouplingHalfPositioning",
    "Coupling",
    "CouplingHalf",
    "CrowningSpecification",
    "CVT",
    "CVTPulley",
    "PartToPartShearCoupling",
    "PartToPartShearCouplingHalf",
    "PitchErrorFlankOptions",
    "Pulley",
    "RigidConnectorSettings",
    "RigidConnectorStiffnessType",
    "RigidConnectorTiltStiffnessTypes",
    "RigidConnectorToothLocation",
    "RigidConnectorToothSpacingType",
    "RigidConnectorTypes",
    "RollingRing",
    "RollingRingAssembly",
    "ShaftHubConnection",
    "SplineFitOptions",
    "SplineHalfManufacturingError",
    "SplineLeadRelief",
    "SplinePitchErrorInputType",
    "SplinePitchErrorOptions",
    "SpringDamper",
    "SpringDamperHalf",
    "Synchroniser",
    "SynchroniserCone",
    "SynchroniserHalf",
    "SynchroniserPart",
    "SynchroniserSleeve",
    "TorqueConverter",
    "TorqueConverterPump",
    "TorqueConverterSpeedRatio",
    "TorqueConverterTurbine",
)
