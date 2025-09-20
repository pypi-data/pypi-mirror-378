"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.fe._2581 import AlignConnectedComponentOptions
    from mastapy._private.system_model.fe._2582 import AlignmentMethod
    from mastapy._private.system_model.fe._2583 import AlignmentMethodForRaceBearing
    from mastapy._private.system_model.fe._2584 import AlignmentUsingAxialNodePositions
    from mastapy._private.system_model.fe._2585 import AngleSource
    from mastapy._private.system_model.fe._2586 import BaseFEWithSelection
    from mastapy._private.system_model.fe._2587 import BatchOperations
    from mastapy._private.system_model.fe._2588 import BearingNodeAlignmentOption
    from mastapy._private.system_model.fe._2589 import BearingNodeOption
    from mastapy._private.system_model.fe._2590 import BearingRaceNodeLink
    from mastapy._private.system_model.fe._2591 import BearingRacePosition
    from mastapy._private.system_model.fe._2592 import ComponentOrientationOption
    from mastapy._private.system_model.fe._2593 import ContactPairWithSelection
    from mastapy._private.system_model.fe._2594 import CoordinateSystemWithSelection
    from mastapy._private.system_model.fe._2595 import CreateConnectedComponentOptions
    from mastapy._private.system_model.fe._2596 import (
        CreateMicrophoneNormalToSurfaceOptions,
    )
    from mastapy._private.system_model.fe._2597 import DegreeOfFreedomBoundaryCondition
    from mastapy._private.system_model.fe._2598 import (
        DegreeOfFreedomBoundaryConditionAngular,
    )
    from mastapy._private.system_model.fe._2599 import (
        DegreeOfFreedomBoundaryConditionLinear,
    )
    from mastapy._private.system_model.fe._2600 import ElectricMachineDataSet
    from mastapy._private.system_model.fe._2601 import ElectricMachineDynamicLoadData
    from mastapy._private.system_model.fe._2602 import ElementFaceGroupWithSelection
    from mastapy._private.system_model.fe._2603 import ElementPropertiesWithSelection
    from mastapy._private.system_model.fe._2604 import FEEntityGroupWithSelection
    from mastapy._private.system_model.fe._2605 import FEExportSettings
    from mastapy._private.system_model.fe._2606 import FEPartDRIVASurfaceSelection
    from mastapy._private.system_model.fe._2607 import FEPartWithBatchOptions
    from mastapy._private.system_model.fe._2608 import FEStiffnessGeometry
    from mastapy._private.system_model.fe._2609 import FEStiffnessTester
    from mastapy._private.system_model.fe._2610 import FESubstructure
    from mastapy._private.system_model.fe._2611 import FESubstructureExportOptions
    from mastapy._private.system_model.fe._2612 import FESubstructureNode
    from mastapy._private.system_model.fe._2613 import FESubstructureNodeModeShape
    from mastapy._private.system_model.fe._2614 import FESubstructureNodeModeShapes
    from mastapy._private.system_model.fe._2615 import FESubstructureType
    from mastapy._private.system_model.fe._2616 import FESubstructureWithBatchOptions
    from mastapy._private.system_model.fe._2617 import FESubstructureWithSelection
    from mastapy._private.system_model.fe._2618 import (
        FESubstructureWithSelectionComponents,
    )
    from mastapy._private.system_model.fe._2619 import (
        FESubstructureWithSelectionForHarmonicAnalysis,
    )
    from mastapy._private.system_model.fe._2620 import (
        FESubstructureWithSelectionForModalAnalysis,
    )
    from mastapy._private.system_model.fe._2621 import (
        FESubstructureWithSelectionForStaticAnalysis,
    )
    from mastapy._private.system_model.fe._2622 import GearMeshingOptions
    from mastapy._private.system_model.fe._2623 import (
        IndependentMASTACreatedCondensationNode,
    )
    from mastapy._private.system_model.fe._2624 import (
        IndependentMASTACreatedConstrainedNodes,
    )
    from mastapy._private.system_model.fe._2625 import (
        IndependentMASTACreatedConstrainedNodesWithSelectionComponents,
    )
    from mastapy._private.system_model.fe._2626 import (
        IndependentMASTACreatedRigidlyConnectedNodeGroup,
    )
    from mastapy._private.system_model.fe._2627 import (
        LinkComponentAxialPositionErrorReporter,
    )
    from mastapy._private.system_model.fe._2628 import LinkNodeSource
    from mastapy._private.system_model.fe._2629 import MaterialPropertiesWithSelection
    from mastapy._private.system_model.fe._2630 import (
        NodeBoundaryConditionStaticAnalysis,
    )
    from mastapy._private.system_model.fe._2631 import NodeGroupWithSelection
    from mastapy._private.system_model.fe._2632 import NodeSelectionDepthOption
    from mastapy._private.system_model.fe._2633 import (
        OptionsWhenExternalFEFileAlreadyExists,
    )
    from mastapy._private.system_model.fe._2634 import PerLinkExportOptions
    from mastapy._private.system_model.fe._2635 import PerNodeExportOptions
    from mastapy._private.system_model.fe._2636 import RaceBearingFE
    from mastapy._private.system_model.fe._2637 import RaceBearingFESystemDeflection
    from mastapy._private.system_model.fe._2638 import RaceBearingFEWithSelection
    from mastapy._private.system_model.fe._2639 import ReplacedShaftSelectionHelper
    from mastapy._private.system_model.fe._2640 import SystemDeflectionFEExportOptions
    from mastapy._private.system_model.fe._2641 import ThermalExpansionOption
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.fe._2581": ["AlignConnectedComponentOptions"],
        "_private.system_model.fe._2582": ["AlignmentMethod"],
        "_private.system_model.fe._2583": ["AlignmentMethodForRaceBearing"],
        "_private.system_model.fe._2584": ["AlignmentUsingAxialNodePositions"],
        "_private.system_model.fe._2585": ["AngleSource"],
        "_private.system_model.fe._2586": ["BaseFEWithSelection"],
        "_private.system_model.fe._2587": ["BatchOperations"],
        "_private.system_model.fe._2588": ["BearingNodeAlignmentOption"],
        "_private.system_model.fe._2589": ["BearingNodeOption"],
        "_private.system_model.fe._2590": ["BearingRaceNodeLink"],
        "_private.system_model.fe._2591": ["BearingRacePosition"],
        "_private.system_model.fe._2592": ["ComponentOrientationOption"],
        "_private.system_model.fe._2593": ["ContactPairWithSelection"],
        "_private.system_model.fe._2594": ["CoordinateSystemWithSelection"],
        "_private.system_model.fe._2595": ["CreateConnectedComponentOptions"],
        "_private.system_model.fe._2596": ["CreateMicrophoneNormalToSurfaceOptions"],
        "_private.system_model.fe._2597": ["DegreeOfFreedomBoundaryCondition"],
        "_private.system_model.fe._2598": ["DegreeOfFreedomBoundaryConditionAngular"],
        "_private.system_model.fe._2599": ["DegreeOfFreedomBoundaryConditionLinear"],
        "_private.system_model.fe._2600": ["ElectricMachineDataSet"],
        "_private.system_model.fe._2601": ["ElectricMachineDynamicLoadData"],
        "_private.system_model.fe._2602": ["ElementFaceGroupWithSelection"],
        "_private.system_model.fe._2603": ["ElementPropertiesWithSelection"],
        "_private.system_model.fe._2604": ["FEEntityGroupWithSelection"],
        "_private.system_model.fe._2605": ["FEExportSettings"],
        "_private.system_model.fe._2606": ["FEPartDRIVASurfaceSelection"],
        "_private.system_model.fe._2607": ["FEPartWithBatchOptions"],
        "_private.system_model.fe._2608": ["FEStiffnessGeometry"],
        "_private.system_model.fe._2609": ["FEStiffnessTester"],
        "_private.system_model.fe._2610": ["FESubstructure"],
        "_private.system_model.fe._2611": ["FESubstructureExportOptions"],
        "_private.system_model.fe._2612": ["FESubstructureNode"],
        "_private.system_model.fe._2613": ["FESubstructureNodeModeShape"],
        "_private.system_model.fe._2614": ["FESubstructureNodeModeShapes"],
        "_private.system_model.fe._2615": ["FESubstructureType"],
        "_private.system_model.fe._2616": ["FESubstructureWithBatchOptions"],
        "_private.system_model.fe._2617": ["FESubstructureWithSelection"],
        "_private.system_model.fe._2618": ["FESubstructureWithSelectionComponents"],
        "_private.system_model.fe._2619": [
            "FESubstructureWithSelectionForHarmonicAnalysis"
        ],
        "_private.system_model.fe._2620": [
            "FESubstructureWithSelectionForModalAnalysis"
        ],
        "_private.system_model.fe._2621": [
            "FESubstructureWithSelectionForStaticAnalysis"
        ],
        "_private.system_model.fe._2622": ["GearMeshingOptions"],
        "_private.system_model.fe._2623": ["IndependentMASTACreatedCondensationNode"],
        "_private.system_model.fe._2624": ["IndependentMASTACreatedConstrainedNodes"],
        "_private.system_model.fe._2625": [
            "IndependentMASTACreatedConstrainedNodesWithSelectionComponents"
        ],
        "_private.system_model.fe._2626": [
            "IndependentMASTACreatedRigidlyConnectedNodeGroup"
        ],
        "_private.system_model.fe._2627": ["LinkComponentAxialPositionErrorReporter"],
        "_private.system_model.fe._2628": ["LinkNodeSource"],
        "_private.system_model.fe._2629": ["MaterialPropertiesWithSelection"],
        "_private.system_model.fe._2630": ["NodeBoundaryConditionStaticAnalysis"],
        "_private.system_model.fe._2631": ["NodeGroupWithSelection"],
        "_private.system_model.fe._2632": ["NodeSelectionDepthOption"],
        "_private.system_model.fe._2633": ["OptionsWhenExternalFEFileAlreadyExists"],
        "_private.system_model.fe._2634": ["PerLinkExportOptions"],
        "_private.system_model.fe._2635": ["PerNodeExportOptions"],
        "_private.system_model.fe._2636": ["RaceBearingFE"],
        "_private.system_model.fe._2637": ["RaceBearingFESystemDeflection"],
        "_private.system_model.fe._2638": ["RaceBearingFEWithSelection"],
        "_private.system_model.fe._2639": ["ReplacedShaftSelectionHelper"],
        "_private.system_model.fe._2640": ["SystemDeflectionFEExportOptions"],
        "_private.system_model.fe._2641": ["ThermalExpansionOption"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AlignConnectedComponentOptions",
    "AlignmentMethod",
    "AlignmentMethodForRaceBearing",
    "AlignmentUsingAxialNodePositions",
    "AngleSource",
    "BaseFEWithSelection",
    "BatchOperations",
    "BearingNodeAlignmentOption",
    "BearingNodeOption",
    "BearingRaceNodeLink",
    "BearingRacePosition",
    "ComponentOrientationOption",
    "ContactPairWithSelection",
    "CoordinateSystemWithSelection",
    "CreateConnectedComponentOptions",
    "CreateMicrophoneNormalToSurfaceOptions",
    "DegreeOfFreedomBoundaryCondition",
    "DegreeOfFreedomBoundaryConditionAngular",
    "DegreeOfFreedomBoundaryConditionLinear",
    "ElectricMachineDataSet",
    "ElectricMachineDynamicLoadData",
    "ElementFaceGroupWithSelection",
    "ElementPropertiesWithSelection",
    "FEEntityGroupWithSelection",
    "FEExportSettings",
    "FEPartDRIVASurfaceSelection",
    "FEPartWithBatchOptions",
    "FEStiffnessGeometry",
    "FEStiffnessTester",
    "FESubstructure",
    "FESubstructureExportOptions",
    "FESubstructureNode",
    "FESubstructureNodeModeShape",
    "FESubstructureNodeModeShapes",
    "FESubstructureType",
    "FESubstructureWithBatchOptions",
    "FESubstructureWithSelection",
    "FESubstructureWithSelectionComponents",
    "FESubstructureWithSelectionForHarmonicAnalysis",
    "FESubstructureWithSelectionForModalAnalysis",
    "FESubstructureWithSelectionForStaticAnalysis",
    "GearMeshingOptions",
    "IndependentMASTACreatedCondensationNode",
    "IndependentMASTACreatedConstrainedNodes",
    "IndependentMASTACreatedConstrainedNodesWithSelectionComponents",
    "IndependentMASTACreatedRigidlyConnectedNodeGroup",
    "LinkComponentAxialPositionErrorReporter",
    "LinkNodeSource",
    "MaterialPropertiesWithSelection",
    "NodeBoundaryConditionStaticAnalysis",
    "NodeGroupWithSelection",
    "NodeSelectionDepthOption",
    "OptionsWhenExternalFEFileAlreadyExists",
    "PerLinkExportOptions",
    "PerNodeExportOptions",
    "RaceBearingFE",
    "RaceBearingFESystemDeflection",
    "RaceBearingFEWithSelection",
    "ReplacedShaftSelectionHelper",
    "SystemDeflectionFEExportOptions",
    "ThermalExpansionOption",
)
