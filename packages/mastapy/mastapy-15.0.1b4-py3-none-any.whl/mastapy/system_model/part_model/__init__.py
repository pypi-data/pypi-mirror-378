"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model._2663 import Assembly
    from mastapy._private.system_model.part_model._2664 import AbstractAssembly
    from mastapy._private.system_model.part_model._2665 import AbstractShaft
    from mastapy._private.system_model.part_model._2666 import AbstractShaftOrHousing
    from mastapy._private.system_model.part_model._2667 import (
        AGMALoadSharingTableApplicationLevel,
    )
    from mastapy._private.system_model.part_model._2668 import (
        AxialInternalClearanceTolerance,
    )
    from mastapy._private.system_model.part_model._2669 import Bearing
    from mastapy._private.system_model.part_model._2670 import BearingF0InputMethod
    from mastapy._private.system_model.part_model._2671 import (
        BearingRaceMountingOptions,
    )
    from mastapy._private.system_model.part_model._2672 import Bolt
    from mastapy._private.system_model.part_model._2673 import BoltedJoint
    from mastapy._private.system_model.part_model._2674 import (
        ClutchLossCalculationParameters,
    )
    from mastapy._private.system_model.part_model._2675 import Component
    from mastapy._private.system_model.part_model._2676 import ComponentsConnectedResult
    from mastapy._private.system_model.part_model._2677 import ConnectedSockets
    from mastapy._private.system_model.part_model._2678 import Connector
    from mastapy._private.system_model.part_model._2679 import Datum
    from mastapy._private.system_model.part_model._2680 import DefaultExportSettings
    from mastapy._private.system_model.part_model._2681 import (
        ElectricMachineSearchRegionSpecificationMethod,
    )
    from mastapy._private.system_model.part_model._2682 import EnginePartLoad
    from mastapy._private.system_model.part_model._2683 import EngineSpeed
    from mastapy._private.system_model.part_model._2684 import ExternalCADModel
    from mastapy._private.system_model.part_model._2685 import FEPart
    from mastapy._private.system_model.part_model._2686 import FlexiblePinAssembly
    from mastapy._private.system_model.part_model._2687 import GuideDxfModel
    from mastapy._private.system_model.part_model._2688 import GuideImage
    from mastapy._private.system_model.part_model._2689 import GuideModelUsage
    from mastapy._private.system_model.part_model._2690 import (
        InnerBearingRaceMountingOptions,
    )
    from mastapy._private.system_model.part_model._2691 import (
        InternalClearanceTolerance,
    )
    from mastapy._private.system_model.part_model._2692 import LoadSharingModes
    from mastapy._private.system_model.part_model._2693 import LoadSharingSettings
    from mastapy._private.system_model.part_model._2694 import MassDisc
    from mastapy._private.system_model.part_model._2695 import MeasurementComponent
    from mastapy._private.system_model.part_model._2696 import Microphone
    from mastapy._private.system_model.part_model._2697 import MicrophoneArray
    from mastapy._private.system_model.part_model._2698 import MountableComponent
    from mastapy._private.system_model.part_model._2699 import OilLevelSpecification
    from mastapy._private.system_model.part_model._2700 import OilSeal
    from mastapy._private.system_model.part_model._2701 import (
        OilSealLossCalculationParameters,
    )
    from mastapy._private.system_model.part_model._2702 import (
        OuterBearingRaceMountingOptions,
    )
    from mastapy._private.system_model.part_model._2703 import Part
    from mastapy._private.system_model.part_model._2704 import (
        PartModelExportPanelOptions,
    )
    from mastapy._private.system_model.part_model._2705 import PlanetCarrier
    from mastapy._private.system_model.part_model._2706 import PlanetCarrierSettings
    from mastapy._private.system_model.part_model._2707 import PointLoad
    from mastapy._private.system_model.part_model._2708 import PowerLoad
    from mastapy._private.system_model.part_model._2709 import (
        RadialInternalClearanceTolerance,
    )
    from mastapy._private.system_model.part_model._2710 import (
        RollingBearingElementLoadCase,
    )
    from mastapy._private.system_model.part_model._2711 import RootAssembly
    from mastapy._private.system_model.part_model._2712 import (
        ShaftDiameterModificationDueToRollingBearingRing,
    )
    from mastapy._private.system_model.part_model._2713 import SpecialisedAssembly
    from mastapy._private.system_model.part_model._2714 import UnbalancedMass
    from mastapy._private.system_model.part_model._2715 import (
        UnbalancedMassInclusionOption,
    )
    from mastapy._private.system_model.part_model._2716 import VirtualComponent
    from mastapy._private.system_model.part_model._2717 import (
        WindTurbineBladeModeDetails,
    )
    from mastapy._private.system_model.part_model._2718 import (
        WindTurbineSingleBladeDetails,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model._2663": ["Assembly"],
        "_private.system_model.part_model._2664": ["AbstractAssembly"],
        "_private.system_model.part_model._2665": ["AbstractShaft"],
        "_private.system_model.part_model._2666": ["AbstractShaftOrHousing"],
        "_private.system_model.part_model._2667": [
            "AGMALoadSharingTableApplicationLevel"
        ],
        "_private.system_model.part_model._2668": ["AxialInternalClearanceTolerance"],
        "_private.system_model.part_model._2669": ["Bearing"],
        "_private.system_model.part_model._2670": ["BearingF0InputMethod"],
        "_private.system_model.part_model._2671": ["BearingRaceMountingOptions"],
        "_private.system_model.part_model._2672": ["Bolt"],
        "_private.system_model.part_model._2673": ["BoltedJoint"],
        "_private.system_model.part_model._2674": ["ClutchLossCalculationParameters"],
        "_private.system_model.part_model._2675": ["Component"],
        "_private.system_model.part_model._2676": ["ComponentsConnectedResult"],
        "_private.system_model.part_model._2677": ["ConnectedSockets"],
        "_private.system_model.part_model._2678": ["Connector"],
        "_private.system_model.part_model._2679": ["Datum"],
        "_private.system_model.part_model._2680": ["DefaultExportSettings"],
        "_private.system_model.part_model._2681": [
            "ElectricMachineSearchRegionSpecificationMethod"
        ],
        "_private.system_model.part_model._2682": ["EnginePartLoad"],
        "_private.system_model.part_model._2683": ["EngineSpeed"],
        "_private.system_model.part_model._2684": ["ExternalCADModel"],
        "_private.system_model.part_model._2685": ["FEPart"],
        "_private.system_model.part_model._2686": ["FlexiblePinAssembly"],
        "_private.system_model.part_model._2687": ["GuideDxfModel"],
        "_private.system_model.part_model._2688": ["GuideImage"],
        "_private.system_model.part_model._2689": ["GuideModelUsage"],
        "_private.system_model.part_model._2690": ["InnerBearingRaceMountingOptions"],
        "_private.system_model.part_model._2691": ["InternalClearanceTolerance"],
        "_private.system_model.part_model._2692": ["LoadSharingModes"],
        "_private.system_model.part_model._2693": ["LoadSharingSettings"],
        "_private.system_model.part_model._2694": ["MassDisc"],
        "_private.system_model.part_model._2695": ["MeasurementComponent"],
        "_private.system_model.part_model._2696": ["Microphone"],
        "_private.system_model.part_model._2697": ["MicrophoneArray"],
        "_private.system_model.part_model._2698": ["MountableComponent"],
        "_private.system_model.part_model._2699": ["OilLevelSpecification"],
        "_private.system_model.part_model._2700": ["OilSeal"],
        "_private.system_model.part_model._2701": ["OilSealLossCalculationParameters"],
        "_private.system_model.part_model._2702": ["OuterBearingRaceMountingOptions"],
        "_private.system_model.part_model._2703": ["Part"],
        "_private.system_model.part_model._2704": ["PartModelExportPanelOptions"],
        "_private.system_model.part_model._2705": ["PlanetCarrier"],
        "_private.system_model.part_model._2706": ["PlanetCarrierSettings"],
        "_private.system_model.part_model._2707": ["PointLoad"],
        "_private.system_model.part_model._2708": ["PowerLoad"],
        "_private.system_model.part_model._2709": ["RadialInternalClearanceTolerance"],
        "_private.system_model.part_model._2710": ["RollingBearingElementLoadCase"],
        "_private.system_model.part_model._2711": ["RootAssembly"],
        "_private.system_model.part_model._2712": [
            "ShaftDiameterModificationDueToRollingBearingRing"
        ],
        "_private.system_model.part_model._2713": ["SpecialisedAssembly"],
        "_private.system_model.part_model._2714": ["UnbalancedMass"],
        "_private.system_model.part_model._2715": ["UnbalancedMassInclusionOption"],
        "_private.system_model.part_model._2716": ["VirtualComponent"],
        "_private.system_model.part_model._2717": ["WindTurbineBladeModeDetails"],
        "_private.system_model.part_model._2718": ["WindTurbineSingleBladeDetails"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "Assembly",
    "AbstractAssembly",
    "AbstractShaft",
    "AbstractShaftOrHousing",
    "AGMALoadSharingTableApplicationLevel",
    "AxialInternalClearanceTolerance",
    "Bearing",
    "BearingF0InputMethod",
    "BearingRaceMountingOptions",
    "Bolt",
    "BoltedJoint",
    "ClutchLossCalculationParameters",
    "Component",
    "ComponentsConnectedResult",
    "ConnectedSockets",
    "Connector",
    "Datum",
    "DefaultExportSettings",
    "ElectricMachineSearchRegionSpecificationMethod",
    "EnginePartLoad",
    "EngineSpeed",
    "ExternalCADModel",
    "FEPart",
    "FlexiblePinAssembly",
    "GuideDxfModel",
    "GuideImage",
    "GuideModelUsage",
    "InnerBearingRaceMountingOptions",
    "InternalClearanceTolerance",
    "LoadSharingModes",
    "LoadSharingSettings",
    "MassDisc",
    "MeasurementComponent",
    "Microphone",
    "MicrophoneArray",
    "MountableComponent",
    "OilLevelSpecification",
    "OilSeal",
    "OilSealLossCalculationParameters",
    "OuterBearingRaceMountingOptions",
    "Part",
    "PartModelExportPanelOptions",
    "PlanetCarrier",
    "PlanetCarrierSettings",
    "PointLoad",
    "PowerLoad",
    "RadialInternalClearanceTolerance",
    "RollingBearingElementLoadCase",
    "RootAssembly",
    "ShaftDiameterModificationDueToRollingBearingRing",
    "SpecialisedAssembly",
    "UnbalancedMass",
    "UnbalancedMassInclusionOption",
    "VirtualComponent",
    "WindTurbineBladeModeDetails",
    "WindTurbineSingleBladeDetails",
)
