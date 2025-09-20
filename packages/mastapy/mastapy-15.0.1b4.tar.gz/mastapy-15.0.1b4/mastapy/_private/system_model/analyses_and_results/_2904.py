"""CompoundAdvancedSystemDeflection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call_overload,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.system_model.analyses_and_results import _2893

_CONCEPT_COUPLING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings",
    "ConceptCouplingConnection",
)
_COUPLING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings", "CouplingConnection"
)
_SPRING_DAMPER_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings", "SpringDamperConnection"
)
_TORQUE_CONVERTER_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings",
    "TorqueConverterConnection",
)
_PART_TO_PART_SHEAR_COUPLING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings",
    "PartToPartShearCouplingConnection",
)
_CLUTCH_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings", "ClutchConnection"
)
_ABSTRACT_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "AbstractShaft"
)
_MICROPHONE = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Microphone")
_MICROPHONE_ARRAY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "MicrophoneArray"
)
_ABSTRACT_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "AbstractAssembly"
)
_ABSTRACT_SHAFT_OR_HOUSING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "AbstractShaftOrHousing"
)
_BEARING = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Bearing")
_BOLT = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Bolt")
_BOLTED_JOINT = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "BoltedJoint")
_COMPONENT = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Component")
_CONNECTOR = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Connector")
_DATUM = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Datum")
_EXTERNAL_CAD_MODEL = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "ExternalCADModel"
)
_FE_PART = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "FEPart")
_FLEXIBLE_PIN_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "FlexiblePinAssembly"
)
_ASSEMBLY = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Assembly")
_GUIDE_DXF_MODEL = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "GuideDxfModel"
)
_MASS_DISC = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "MassDisc")
_MEASUREMENT_COMPONENT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "MeasurementComponent"
)
_MOUNTABLE_COMPONENT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "MountableComponent"
)
_OIL_SEAL = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "OilSeal")
_PART = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Part")
_PLANET_CARRIER = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "PlanetCarrier"
)
_POINT_LOAD = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "PointLoad")
_POWER_LOAD = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "PowerLoad")
_ROOT_ASSEMBLY = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "RootAssembly")
_SPECIALISED_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "SpecialisedAssembly"
)
_UNBALANCED_MASS = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "UnbalancedMass"
)
_VIRTUAL_COMPONENT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "VirtualComponent"
)
_SHAFT = python_net_import("SMT.MastaAPI.SystemModel.PartModel.ShaftModel", "Shaft")
_CONCEPT_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConceptGear"
)
_CONCEPT_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConceptGearSet"
)
_FACE_GEAR = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Gears", "FaceGear")
_FACE_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "FaceGearSet"
)
_AGMA_GLEASON_CONICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "AGMAGleasonConicalGear"
)
_AGMA_GLEASON_CONICAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "AGMAGleasonConicalGearSet"
)
_BEVEL_DIFFERENTIAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelDifferentialGear"
)
_BEVEL_DIFFERENTIAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelDifferentialGearSet"
)
_BEVEL_DIFFERENTIAL_PLANET_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelDifferentialPlanetGear"
)
_BEVEL_DIFFERENTIAL_SUN_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelDifferentialSunGear"
)
_BEVEL_GEAR = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelGear")
_BEVEL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "BevelGearSet"
)
_CONICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConicalGear"
)
_CONICAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConicalGearSet"
)
_CYLINDRICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "CylindricalGear"
)
_CYLINDRICAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "CylindricalGearSet"
)
_CYLINDRICAL_PLANET_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "CylindricalPlanetGear"
)
_GEAR = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Gears", "Gear")
_GEAR_SET = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Gears", "GearSet")
_HYPOID_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "HypoidGear"
)
_HYPOID_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "HypoidGearSet"
)
_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "KlingelnbergCycloPalloidConicalGear"
)
_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "KlingelnbergCycloPalloidConicalGearSet"
)
_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "KlingelnbergCycloPalloidHypoidGear"
)
_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "KlingelnbergCycloPalloidHypoidGearSet"
)
_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears",
    "KlingelnbergCycloPalloidSpiralBevelGear",
)
_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears",
    "KlingelnbergCycloPalloidSpiralBevelGearSet",
)
_PLANETARY_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "PlanetaryGearSet"
)
_SPIRAL_BEVEL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "SpiralBevelGear"
)
_SPIRAL_BEVEL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "SpiralBevelGearSet"
)
_STRAIGHT_BEVEL_DIFF_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelDiffGear"
)
_STRAIGHT_BEVEL_DIFF_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelDiffGearSet"
)
_STRAIGHT_BEVEL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelGear"
)
_STRAIGHT_BEVEL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelGearSet"
)
_STRAIGHT_BEVEL_PLANET_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelPlanetGear"
)
_STRAIGHT_BEVEL_SUN_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelSunGear"
)
_WORM_GEAR = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Gears", "WormGear")
_WORM_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "WormGearSet"
)
_ZEROL_BEVEL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ZerolBevelGear"
)
_ZEROL_BEVEL_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ZerolBevelGearSet"
)
_CYCLOIDAL_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Cycloidal", "CycloidalAssembly"
)
_CYCLOIDAL_DISC = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Cycloidal", "CycloidalDisc"
)
_RING_PINS = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Cycloidal", "RingPins"
)
_PART_TO_PART_SHEAR_COUPLING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "PartToPartShearCoupling"
)
_PART_TO_PART_SHEAR_COUPLING_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "PartToPartShearCouplingHalf"
)
_BELT_DRIVE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "BeltDrive"
)
_CLUTCH = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Couplings", "Clutch")
_CLUTCH_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "ClutchHalf"
)
_CONCEPT_COUPLING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "ConceptCoupling"
)
_CONCEPT_COUPLING_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "ConceptCouplingHalf"
)
_COUPLING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "Coupling"
)
_COUPLING_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "CouplingHalf"
)
_CVT = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Couplings", "CVT")
_CVT_PULLEY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "CVTPulley"
)
_PULLEY = python_net_import("SMT.MastaAPI.SystemModel.PartModel.Couplings", "Pulley")
_SHAFT_HUB_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "ShaftHubConnection"
)
_ROLLING_RING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "RollingRing"
)
_ROLLING_RING_ASSEMBLY = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "RollingRingAssembly"
)
_SPRING_DAMPER = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "SpringDamper"
)
_SPRING_DAMPER_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "SpringDamperHalf"
)
_SYNCHRONISER = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "Synchroniser"
)
_SYNCHRONISER_HALF = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "SynchroniserHalf"
)
_SYNCHRONISER_PART = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "SynchroniserPart"
)
_SYNCHRONISER_SLEEVE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "SynchroniserSleeve"
)
_TORQUE_CONVERTER = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "TorqueConverter"
)
_TORQUE_CONVERTER_PUMP = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "TorqueConverterPump"
)
_TORQUE_CONVERTER_TURBINE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "TorqueConverterTurbine"
)
_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets",
    "ShaftToMountableComponentConnection",
)
_CVT_BELT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "CVTBeltConnection"
)
_BELT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "BeltConnection"
)
_COAXIAL_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "CoaxialConnection"
)
_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "Connection"
)
_INTER_MOUNTABLE_COMPONENT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets",
    "InterMountableComponentConnection",
)
_PLANETARY_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "PlanetaryConnection"
)
_ROLLING_RING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "RollingRingConnection"
)
_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets",
    "AbstractShaftToMountableComponentConnection",
)
_BEVEL_DIFFERENTIAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "BevelDifferentialGearMesh"
)
_CONCEPT_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "ConceptGearMesh"
)
_FACE_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "FaceGearMesh"
)
_STRAIGHT_BEVEL_DIFF_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "StraightBevelDiffGearMesh"
)
_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "BevelGearMesh"
)
_CONICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "ConicalGearMesh"
)
_AGMA_GLEASON_CONICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "AGMAGleasonConicalGearMesh"
)
_CYLINDRICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "CylindricalGearMesh"
)
_HYPOID_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "HypoidGearMesh"
)
_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears",
    "KlingelnbergCycloPalloidConicalGearMesh",
)
_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears",
    "KlingelnbergCycloPalloidHypoidGearMesh",
)
_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears",
    "KlingelnbergCycloPalloidSpiralBevelGearMesh",
)
_SPIRAL_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "SpiralBevelGearMesh"
)
_STRAIGHT_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "StraightBevelGearMesh"
)
_WORM_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "WormGearMesh"
)
_ZEROL_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "ZerolBevelGearMesh"
)
_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "GearMesh"
)
_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal",
    "CycloidalDiscCentralBearingConnection",
)
_CYCLOIDAL_DISC_PLANETARY_BEARING_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal",
    "CycloidalDiscPlanetaryBearingConnection",
)
_RING_PINS_TO_DISC_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Cycloidal",
    "RingPinsToDiscConnection",
)
_COMPOUND_ADVANCED_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults", "CompoundAdvancedSystemDeflection"
)

if TYPE_CHECKING:
    from typing import Any, Iterable, Type, TypeVar

    from mastapy._private import _7900
    from mastapy._private.system_model.analyses_and_results.advanced_system_deflections.compound import (
        _7535,
        _7536,
        _7537,
        _7538,
        _7539,
        _7540,
        _7541,
        _7542,
        _7543,
        _7544,
        _7545,
        _7546,
        _7547,
        _7548,
        _7549,
        _7550,
        _7551,
        _7552,
        _7553,
        _7554,
        _7555,
        _7556,
        _7557,
        _7558,
        _7559,
        _7560,
        _7561,
        _7562,
        _7563,
        _7564,
        _7565,
        _7566,
        _7567,
        _7568,
        _7569,
        _7570,
        _7571,
        _7572,
        _7573,
        _7574,
        _7575,
        _7576,
        _7577,
        _7578,
        _7579,
        _7580,
        _7581,
        _7582,
        _7583,
        _7584,
        _7585,
        _7586,
        _7587,
        _7588,
        _7589,
        _7590,
        _7591,
        _7592,
        _7593,
        _7594,
        _7595,
        _7596,
        _7597,
        _7598,
        _7599,
        _7600,
        _7601,
        _7602,
        _7603,
        _7604,
        _7605,
        _7606,
        _7607,
        _7608,
        _7609,
        _7610,
        _7611,
        _7612,
        _7613,
        _7614,
        _7615,
        _7616,
        _7617,
        _7618,
        _7619,
        _7620,
        _7621,
        _7622,
        _7623,
        _7624,
        _7625,
        _7626,
        _7627,
        _7628,
        _7629,
        _7630,
        _7631,
        _7632,
        _7633,
        _7634,
        _7635,
        _7636,
        _7637,
        _7638,
        _7639,
        _7640,
        _7641,
        _7642,
        _7643,
        _7644,
        _7645,
        _7646,
        _7647,
        _7648,
        _7649,
        _7650,
        _7651,
        _7652,
        _7653,
        _7654,
        _7655,
        _7656,
        _7657,
        _7658,
        _7659,
        _7660,
        _7661,
        _7662,
        _7663,
        _7664,
        _7665,
    )
    from mastapy._private.system_model.connections_and_sockets import (
        _2491,
        _2494,
        _2495,
        _2498,
        _2499,
        _2507,
        _2513,
        _2518,
        _2521,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings import (
        _2568,
        _2570,
        _2572,
        _2574,
        _2576,
        _2578,
    )
    from mastapy._private.system_model.connections_and_sockets.cycloidal import (
        _2561,
        _2564,
        _2567,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import (
        _2525,
        _2527,
        _2529,
        _2531,
        _2533,
        _2535,
        _2537,
        _2539,
        _2541,
        _2544,
        _2545,
        _2546,
        _2549,
        _2551,
        _2553,
        _2555,
        _2557,
    )
    from mastapy._private.system_model.part_model import (
        _2663,
        _2664,
        _2665,
        _2666,
        _2669,
        _2672,
        _2673,
        _2675,
        _2678,
        _2679,
        _2684,
        _2685,
        _2686,
        _2687,
        _2694,
        _2695,
        _2696,
        _2697,
        _2698,
        _2700,
        _2703,
        _2705,
        _2707,
        _2708,
        _2711,
        _2713,
        _2714,
        _2716,
    )
    from mastapy._private.system_model.part_model.couplings import (
        _2820,
        _2822,
        _2823,
        _2825,
        _2826,
        _2828,
        _2829,
        _2831,
        _2832,
        _2833,
        _2834,
        _2836,
        _2843,
        _2844,
        _2845,
        _2851,
        _2852,
        _2853,
        _2855,
        _2856,
        _2857,
        _2858,
        _2859,
        _2861,
    )
    from mastapy._private.system_model.part_model.cycloidal import _2811, _2812, _2813
    from mastapy._private.system_model.part_model.gears import (
        _2755,
        _2756,
        _2757,
        _2758,
        _2759,
        _2760,
        _2761,
        _2762,
        _2763,
        _2764,
        _2765,
        _2766,
        _2767,
        _2768,
        _2769,
        _2770,
        _2771,
        _2772,
        _2774,
        _2776,
        _2777,
        _2778,
        _2779,
        _2780,
        _2781,
        _2782,
        _2783,
        _2784,
        _2786,
        _2787,
        _2788,
        _2789,
        _2790,
        _2791,
        _2792,
        _2793,
        _2794,
        _2795,
        _2796,
        _2797,
    )
    from mastapy._private.system_model.part_model.shaft_model import _2719

    Self = TypeVar("Self", bound="CompoundAdvancedSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CompoundAdvancedSystemDeflection._Cast_CompoundAdvancedSystemDeflection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CompoundAdvancedSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CompoundAdvancedSystemDeflection:
    """Special nested class for casting CompoundAdvancedSystemDeflection to subclasses."""

    __parent__: "CompoundAdvancedSystemDeflection"

    @property
    def compound_analysis(self: "CastSelf") -> "_2893.CompoundAnalysis":
        return self.__parent__._cast(_2893.CompoundAnalysis)

    @property
    def marshal_by_ref_object_permanent(
        self: "CastSelf",
    ) -> "_7900.MarshalByRefObjectPermanent":
        from mastapy._private import _7900

        return self.__parent__._cast(_7900.MarshalByRefObjectPermanent)

    @property
    def compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "CompoundAdvancedSystemDeflection":
        return self.__parent__

    def __getattr__(self: "CastSelf", name: str) -> "Any":
        try:
            return self.__getattribute__(name)
        except AttributeError:
            class_name = utility.camel(name)
            raise CastException(
                f'Detected an invalid cast. Cannot cast to type "{class_name}"'
            ) from None


@extended_dataclass(frozen=True, slots=True, weakref_slot=True, eq=False)
class CompoundAdvancedSystemDeflection(_2893.CompoundAnalysis):
    """CompoundAdvancedSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPOUND_ADVANCED_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_coupling_connection(
        self: "Self", design_entity: "_2570.ConceptCouplingConnection"
    ) -> "Iterable[_7562.ConceptCouplingConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConceptCouplingConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.ConceptCouplingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_COUPLING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_coupling_connection(
        self: "Self", design_entity: "_2572.CouplingConnection"
    ) -> "Iterable[_7573.CouplingConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CouplingConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.CouplingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_COUPLING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spring_damper_connection(
        self: "Self", design_entity: "_2576.SpringDamperConnection"
    ) -> "Iterable[_7640.SpringDamperConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SpringDamperConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.SpringDamperConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPRING_DAMPER_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_torque_converter_connection(
        self: "Self", design_entity: "_2578.TorqueConverterConnection"
    ) -> "Iterable[_7655.TorqueConverterConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.TorqueConverterConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.TorqueConverterConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_TORQUE_CONVERTER_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_abstract_shaft(
        self: "Self", design_entity: "_2665.AbstractShaft"
    ) -> "Iterable[_7536.AbstractShaftCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.AbstractShaftCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.AbstractShaft)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ABSTRACT_SHAFT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_microphone(
        self: "Self", design_entity: "_2696.Microphone"
    ) -> "Iterable[_7613.MicrophoneCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.MicrophoneCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Microphone)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_MICROPHONE],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_microphone_array(
        self: "Self", design_entity: "_2697.MicrophoneArray"
    ) -> "Iterable[_7612.MicrophoneArrayCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.MicrophoneArrayCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.MicrophoneArray)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_MICROPHONE_ARRAY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_abstract_assembly(
        self: "Self", design_entity: "_2664.AbstractAssembly"
    ) -> "Iterable[_7535.AbstractAssemblyCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.AbstractAssemblyCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.AbstractAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ABSTRACT_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_abstract_shaft_or_housing(
        self: "Self", design_entity: "_2666.AbstractShaftOrHousing"
    ) -> "Iterable[_7537.AbstractShaftOrHousingCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.AbstractShaftOrHousingCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.AbstractShaftOrHousing)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ABSTRACT_SHAFT_OR_HOUSING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bearing(
        self: "Self", design_entity: "_2669.Bearing"
    ) -> "Iterable[_7543.BearingCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BearingCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Bearing)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEARING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bolt(
        self: "Self", design_entity: "_2672.Bolt"
    ) -> "Iterable[_7554.BoltCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BoltCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Bolt)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BOLT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bolted_joint(
        self: "Self", design_entity: "_2673.BoltedJoint"
    ) -> "Iterable[_7555.BoltedJointCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BoltedJointCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.BoltedJoint)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BOLTED_JOINT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_component(
        self: "Self", design_entity: "_2675.Component"
    ) -> "Iterable[_7560.ComponentCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ComponentCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Component)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_COMPONENT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_connector(
        self: "Self", design_entity: "_2678.Connector"
    ) -> "Iterable[_7571.ConnectorCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConnectorCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Connector)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONNECTOR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_datum(
        self: "Self", design_entity: "_2679.Datum"
    ) -> "Iterable[_7586.DatumCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.DatumCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Datum)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_DATUM],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_external_cad_model(
        self: "Self", design_entity: "_2684.ExternalCADModel"
    ) -> "Iterable[_7587.ExternalCADModelCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ExternalCADModelCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.ExternalCADModel)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_EXTERNAL_CAD_MODEL],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_fe_part(
        self: "Self", design_entity: "_2685.FEPart"
    ) -> "Iterable[_7591.FEPartCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.FEPartCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.FEPart)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_FE_PART],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_flexible_pin_assembly(
        self: "Self", design_entity: "_2686.FlexiblePinAssembly"
    ) -> "Iterable[_7592.FlexiblePinAssemblyCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.FlexiblePinAssemblyCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.FlexiblePinAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_FLEXIBLE_PIN_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_assembly(
        self: "Self", design_entity: "_2663.Assembly"
    ) -> "Iterable[_7542.AssemblyCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.AssemblyCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Assembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_guide_dxf_model(
        self: "Self", design_entity: "_2687.GuideDxfModel"
    ) -> "Iterable[_7596.GuideDxfModelCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.GuideDxfModelCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.GuideDxfModel)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_GUIDE_DXF_MODEL],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_mass_disc(
        self: "Self", design_entity: "_2694.MassDisc"
    ) -> "Iterable[_7610.MassDiscCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.MassDiscCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.MassDisc)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_MASS_DISC],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_measurement_component(
        self: "Self", design_entity: "_2695.MeasurementComponent"
    ) -> "Iterable[_7611.MeasurementComponentCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.MeasurementComponentCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.MeasurementComponent)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_MEASUREMENT_COMPONENT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_mountable_component(
        self: "Self", design_entity: "_2698.MountableComponent"
    ) -> "Iterable[_7614.MountableComponentCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.MountableComponentCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.MountableComponent)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_MOUNTABLE_COMPONENT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_oil_seal(
        self: "Self", design_entity: "_2700.OilSeal"
    ) -> "Iterable[_7615.OilSealCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.OilSealCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.OilSeal)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_OIL_SEAL],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_part(
        self: "Self", design_entity: "_2703.Part"
    ) -> "Iterable[_7616.PartCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.PartCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.Part)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PART],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_planet_carrier(
        self: "Self", design_entity: "_2705.PlanetCarrier"
    ) -> "Iterable[_7622.PlanetCarrierCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.PlanetCarrierCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.PlanetCarrier)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PLANET_CARRIER],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_point_load(
        self: "Self", design_entity: "_2707.PointLoad"
    ) -> "Iterable[_7623.PointLoadCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.PointLoadCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.PointLoad)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_POINT_LOAD],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_power_load(
        self: "Self", design_entity: "_2708.PowerLoad"
    ) -> "Iterable[_7624.PowerLoadCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.PowerLoadCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.PowerLoad)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_POWER_LOAD],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_root_assembly(
        self: "Self", design_entity: "_2711.RootAssembly"
    ) -> "Iterable[_7631.RootAssemblyCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.RootAssemblyCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.RootAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ROOT_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_specialised_assembly(
        self: "Self", design_entity: "_2713.SpecialisedAssembly"
    ) -> "Iterable[_7635.SpecialisedAssemblyCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SpecialisedAssemblyCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.SpecialisedAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPECIALISED_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_unbalanced_mass(
        self: "Self", design_entity: "_2714.UnbalancedMass"
    ) -> "Iterable[_7658.UnbalancedMassCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.UnbalancedMassCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.UnbalancedMass)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_UNBALANCED_MASS],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_virtual_component(
        self: "Self", design_entity: "_2716.VirtualComponent"
    ) -> "Iterable[_7659.VirtualComponentCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.VirtualComponentCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.VirtualComponent)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_VIRTUAL_COMPONENT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_shaft(
        self: "Self", design_entity: "_2719.Shaft"
    ) -> "Iterable[_7632.ShaftCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ShaftCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.shaft_model.Shaft)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SHAFT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_gear(
        self: "Self", design_entity: "_2763.ConceptGear"
    ) -> "Iterable[_7564.ConceptGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConceptGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConceptGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_gear_set(
        self: "Self", design_entity: "_2764.ConceptGearSet"
    ) -> "Iterable[_7566.ConceptGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConceptGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConceptGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_face_gear(
        self: "Self", design_entity: "_2770.FaceGear"
    ) -> "Iterable[_7588.FaceGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.FaceGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.FaceGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_FACE_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_face_gear_set(
        self: "Self", design_entity: "_2771.FaceGearSet"
    ) -> "Iterable[_7590.FaceGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.FaceGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.FaceGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_FACE_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_agma_gleason_conical_gear(
        self: "Self", design_entity: "_2755.AGMAGleasonConicalGear"
    ) -> "Iterable[_7539.AGMAGleasonConicalGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.AGMAGleasonConicalGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.AGMAGleasonConicalGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_AGMA_GLEASON_CONICAL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_agma_gleason_conical_gear_set(
        self: "Self", design_entity: "_2756.AGMAGleasonConicalGearSet"
    ) -> "Iterable[_7541.AGMAGleasonConicalGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.AGMAGleasonConicalGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.AGMAGleasonConicalGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_AGMA_GLEASON_CONICAL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_differential_gear(
        self: "Self", design_entity: "_2757.BevelDifferentialGear"
    ) -> "Iterable[_7546.BevelDifferentialGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BevelDifferentialGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_DIFFERENTIAL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_differential_gear_set(
        self: "Self", design_entity: "_2758.BevelDifferentialGearSet"
    ) -> "Iterable[_7548.BevelDifferentialGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BevelDifferentialGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_DIFFERENTIAL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_differential_planet_gear(
        self: "Self", design_entity: "_2759.BevelDifferentialPlanetGear"
    ) -> "Iterable[_7549.BevelDifferentialPlanetGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BevelDifferentialPlanetGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialPlanetGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_DIFFERENTIAL_PLANET_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_differential_sun_gear(
        self: "Self", design_entity: "_2760.BevelDifferentialSunGear"
    ) -> "Iterable[_7550.BevelDifferentialSunGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BevelDifferentialSunGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelDifferentialSunGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_DIFFERENTIAL_SUN_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_gear(
        self: "Self", design_entity: "_2761.BevelGear"
    ) -> "Iterable[_7551.BevelGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BevelGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_gear_set(
        self: "Self", design_entity: "_2762.BevelGearSet"
    ) -> "Iterable[_7553.BevelGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BevelGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.BevelGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_conical_gear(
        self: "Self", design_entity: "_2765.ConicalGear"
    ) -> "Iterable[_7567.ConicalGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConicalGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConicalGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONICAL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_conical_gear_set(
        self: "Self", design_entity: "_2766.ConicalGearSet"
    ) -> "Iterable[_7569.ConicalGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConicalGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ConicalGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONICAL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cylindrical_gear(
        self: "Self", design_entity: "_2767.CylindricalGear"
    ) -> "Iterable[_7582.CylindricalGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CylindricalGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.CylindricalGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYLINDRICAL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cylindrical_gear_set(
        self: "Self", design_entity: "_2768.CylindricalGearSet"
    ) -> "Iterable[_7584.CylindricalGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CylindricalGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.CylindricalGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYLINDRICAL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cylindrical_planet_gear(
        self: "Self", design_entity: "_2769.CylindricalPlanetGear"
    ) -> "Iterable[_7585.CylindricalPlanetGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CylindricalPlanetGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.CylindricalPlanetGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYLINDRICAL_PLANET_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_gear(
        self: "Self", design_entity: "_2772.Gear"
    ) -> "Iterable[_7593.GearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.GearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.Gear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_gear_set(
        self: "Self", design_entity: "_2774.GearSet"
    ) -> "Iterable[_7595.GearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.GearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.GearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_hypoid_gear(
        self: "Self", design_entity: "_2776.HypoidGear"
    ) -> "Iterable[_7597.HypoidGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.HypoidGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.HypoidGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_HYPOID_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_hypoid_gear_set(
        self: "Self", design_entity: "_2777.HypoidGearSet"
    ) -> "Iterable[_7599.HypoidGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.HypoidGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.HypoidGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_HYPOID_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_conical_gear(
        self: "Self", design_entity: "_2778.KlingelnbergCycloPalloidConicalGear"
    ) -> "Iterable[_7601.KlingelnbergCycloPalloidConicalGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.KlingelnbergCycloPalloidConicalGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidConicalGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_conical_gear_set(
        self: "Self", design_entity: "_2779.KlingelnbergCycloPalloidConicalGearSet"
    ) -> "Iterable[_7603.KlingelnbergCycloPalloidConicalGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.KlingelnbergCycloPalloidConicalGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidConicalGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_hypoid_gear(
        self: "Self", design_entity: "_2780.KlingelnbergCycloPalloidHypoidGear"
    ) -> "Iterable[_7604.KlingelnbergCycloPalloidHypoidGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.KlingelnbergCycloPalloidHypoidGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_hypoid_gear_set(
        self: "Self", design_entity: "_2781.KlingelnbergCycloPalloidHypoidGearSet"
    ) -> "Iterable[_7606.KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.KlingelnbergCycloPalloidHypoidGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidHypoidGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_spiral_bevel_gear(
        self: "Self", design_entity: "_2782.KlingelnbergCycloPalloidSpiralBevelGear"
    ) -> "Iterable[_7607.KlingelnbergCycloPalloidSpiralBevelGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.KlingelnbergCycloPalloidSpiralBevelGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_spiral_bevel_gear_set(
        self: "Self", design_entity: "_2783.KlingelnbergCycloPalloidSpiralBevelGearSet"
    ) -> "Iterable[_7609.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.KlingelnbergCycloPalloidSpiralBevelGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.KlingelnbergCycloPalloidSpiralBevelGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_planetary_gear_set(
        self: "Self", design_entity: "_2784.PlanetaryGearSet"
    ) -> "Iterable[_7621.PlanetaryGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.PlanetaryGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.PlanetaryGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PLANETARY_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spiral_bevel_gear(
        self: "Self", design_entity: "_2786.SpiralBevelGear"
    ) -> "Iterable[_7636.SpiralBevelGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SpiralBevelGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.SpiralBevelGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPIRAL_BEVEL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spiral_bevel_gear_set(
        self: "Self", design_entity: "_2787.SpiralBevelGearSet"
    ) -> "Iterable[_7638.SpiralBevelGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SpiralBevelGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.SpiralBevelGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPIRAL_BEVEL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_diff_gear(
        self: "Self", design_entity: "_2788.StraightBevelDiffGear"
    ) -> "Iterable[_7642.StraightBevelDiffGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.StraightBevelDiffGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelDiffGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_DIFF_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_diff_gear_set(
        self: "Self", design_entity: "_2789.StraightBevelDiffGearSet"
    ) -> "Iterable[_7644.StraightBevelDiffGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.StraightBevelDiffGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelDiffGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_DIFF_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_gear(
        self: "Self", design_entity: "_2790.StraightBevelGear"
    ) -> "Iterable[_7645.StraightBevelGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.StraightBevelGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_gear_set(
        self: "Self", design_entity: "_2791.StraightBevelGearSet"
    ) -> "Iterable[_7647.StraightBevelGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.StraightBevelGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_planet_gear(
        self: "Self", design_entity: "_2792.StraightBevelPlanetGear"
    ) -> "Iterable[_7648.StraightBevelPlanetGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.StraightBevelPlanetGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelPlanetGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_PLANET_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_sun_gear(
        self: "Self", design_entity: "_2793.StraightBevelSunGear"
    ) -> "Iterable[_7649.StraightBevelSunGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.StraightBevelSunGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.StraightBevelSunGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_SUN_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_worm_gear(
        self: "Self", design_entity: "_2794.WormGear"
    ) -> "Iterable[_7660.WormGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.WormGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.WormGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_WORM_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_worm_gear_set(
        self: "Self", design_entity: "_2795.WormGearSet"
    ) -> "Iterable[_7662.WormGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.WormGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.WormGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_WORM_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_zerol_bevel_gear(
        self: "Self", design_entity: "_2796.ZerolBevelGear"
    ) -> "Iterable[_7663.ZerolBevelGearCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ZerolBevelGearCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ZerolBevelGear)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ZEROL_BEVEL_GEAR],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_zerol_bevel_gear_set(
        self: "Self", design_entity: "_2797.ZerolBevelGearSet"
    ) -> "Iterable[_7665.ZerolBevelGearSetCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ZerolBevelGearSetCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.gears.ZerolBevelGearSet)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ZEROL_BEVEL_GEAR_SET],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cycloidal_assembly(
        self: "Self", design_entity: "_2811.CycloidalAssembly"
    ) -> "Iterable[_7578.CycloidalAssemblyCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CycloidalAssemblyCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.cycloidal.CycloidalAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYCLOIDAL_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cycloidal_disc(
        self: "Self", design_entity: "_2812.CycloidalDisc"
    ) -> "Iterable[_7580.CycloidalDiscCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CycloidalDiscCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.cycloidal.CycloidalDisc)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYCLOIDAL_DISC],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_ring_pins(
        self: "Self", design_entity: "_2813.RingPins"
    ) -> "Iterable[_7626.RingPinsCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.RingPinsCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.cycloidal.RingPins)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_RING_PINS],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_part_to_part_shear_coupling(
        self: "Self", design_entity: "_2833.PartToPartShearCoupling"
    ) -> "Iterable[_7617.PartToPartShearCouplingCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.PartToPartShearCouplingCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.PartToPartShearCoupling)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PART_TO_PART_SHEAR_COUPLING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_part_to_part_shear_coupling_half(
        self: "Self", design_entity: "_2834.PartToPartShearCouplingHalf"
    ) -> "Iterable[_7619.PartToPartShearCouplingHalfCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.PartToPartShearCouplingHalfCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.PartToPartShearCouplingHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PART_TO_PART_SHEAR_COUPLING_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_belt_drive(
        self: "Self", design_entity: "_2820.BeltDrive"
    ) -> "Iterable[_7545.BeltDriveCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BeltDriveCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.BeltDrive)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BELT_DRIVE],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_clutch(
        self: "Self", design_entity: "_2822.Clutch"
    ) -> "Iterable[_7556.ClutchCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ClutchCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Clutch)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CLUTCH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_clutch_half(
        self: "Self", design_entity: "_2823.ClutchHalf"
    ) -> "Iterable[_7558.ClutchHalfCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ClutchHalfCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ClutchHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CLUTCH_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_coupling(
        self: "Self", design_entity: "_2825.ConceptCoupling"
    ) -> "Iterable[_7561.ConceptCouplingCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConceptCouplingCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ConceptCoupling)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_COUPLING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_coupling_half(
        self: "Self", design_entity: "_2826.ConceptCouplingHalf"
    ) -> "Iterable[_7563.ConceptCouplingHalfCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConceptCouplingHalfCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ConceptCouplingHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_COUPLING_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_coupling(
        self: "Self", design_entity: "_2828.Coupling"
    ) -> "Iterable[_7572.CouplingCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CouplingCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Coupling)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_COUPLING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_coupling_half(
        self: "Self", design_entity: "_2829.CouplingHalf"
    ) -> "Iterable[_7574.CouplingHalfCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CouplingHalfCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.CouplingHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_COUPLING_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cvt(
        self: "Self", design_entity: "_2831.CVT"
    ) -> "Iterable[_7576.CVTCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CVTCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.CVT)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CVT],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cvt_pulley(
        self: "Self", design_entity: "_2832.CVTPulley"
    ) -> "Iterable[_7577.CVTPulleyCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CVTPulleyCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.CVTPulley)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CVT_PULLEY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_pulley(
        self: "Self", design_entity: "_2836.Pulley"
    ) -> "Iterable[_7625.PulleyCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.PulleyCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Pulley)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PULLEY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_shaft_hub_connection(
        self: "Self", design_entity: "_2845.ShaftHubConnection"
    ) -> "Iterable[_7633.ShaftHubConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ShaftHubConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.ShaftHubConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SHAFT_HUB_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_rolling_ring(
        self: "Self", design_entity: "_2843.RollingRing"
    ) -> "Iterable[_7629.RollingRingCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.RollingRingCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.RollingRing)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ROLLING_RING],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_rolling_ring_assembly(
        self: "Self", design_entity: "_2844.RollingRingAssembly"
    ) -> "Iterable[_7628.RollingRingAssemblyCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.RollingRingAssemblyCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.RollingRingAssembly)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ROLLING_RING_ASSEMBLY],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spring_damper(
        self: "Self", design_entity: "_2851.SpringDamper"
    ) -> "Iterable[_7639.SpringDamperCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SpringDamperCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SpringDamper)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPRING_DAMPER],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spring_damper_half(
        self: "Self", design_entity: "_2852.SpringDamperHalf"
    ) -> "Iterable[_7641.SpringDamperHalfCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SpringDamperHalfCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SpringDamperHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPRING_DAMPER_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_synchroniser(
        self: "Self", design_entity: "_2853.Synchroniser"
    ) -> "Iterable[_7650.SynchroniserCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SynchroniserCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.Synchroniser)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SYNCHRONISER],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_synchroniser_half(
        self: "Self", design_entity: "_2855.SynchroniserHalf"
    ) -> "Iterable[_7651.SynchroniserHalfCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SynchroniserHalfCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SynchroniserHalf)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SYNCHRONISER_HALF],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_synchroniser_part(
        self: "Self", design_entity: "_2856.SynchroniserPart"
    ) -> "Iterable[_7652.SynchroniserPartCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SynchroniserPartCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SynchroniserPart)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SYNCHRONISER_PART],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_synchroniser_sleeve(
        self: "Self", design_entity: "_2857.SynchroniserSleeve"
    ) -> "Iterable[_7653.SynchroniserSleeveCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SynchroniserSleeveCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.SynchroniserSleeve)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SYNCHRONISER_SLEEVE],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_torque_converter(
        self: "Self", design_entity: "_2858.TorqueConverter"
    ) -> "Iterable[_7654.TorqueConverterCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.TorqueConverterCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.TorqueConverter)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_TORQUE_CONVERTER],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_torque_converter_pump(
        self: "Self", design_entity: "_2859.TorqueConverterPump"
    ) -> "Iterable[_7656.TorqueConverterPumpCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.TorqueConverterPumpCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.TorqueConverterPump)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_TORQUE_CONVERTER_PUMP],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_torque_converter_turbine(
        self: "Self", design_entity: "_2861.TorqueConverterTurbine"
    ) -> "Iterable[_7657.TorqueConverterTurbineCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.TorqueConverterTurbineCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.part_model.couplings.TorqueConverterTurbine)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_TORQUE_CONVERTER_TURBINE],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_shaft_to_mountable_component_connection(
        self: "Self", design_entity: "_2521.ShaftToMountableComponentConnection"
    ) -> "Iterable[_7634.ShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.ShaftToMountableComponentConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cvt_belt_connection(
        self: "Self", design_entity: "_2499.CVTBeltConnection"
    ) -> "Iterable[_7575.CVTBeltConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CVTBeltConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.CVTBeltConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CVT_BELT_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_belt_connection(
        self: "Self", design_entity: "_2494.BeltConnection"
    ) -> "Iterable[_7544.BeltConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BeltConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.BeltConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BELT_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_coaxial_connection(
        self: "Self", design_entity: "_2495.CoaxialConnection"
    ) -> "Iterable[_7559.CoaxialConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CoaxialConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.CoaxialConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_COAXIAL_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_connection(
        self: "Self", design_entity: "_2498.Connection"
    ) -> "Iterable[_7570.ConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.Connection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_inter_mountable_component_connection(
        self: "Self", design_entity: "_2507.InterMountableComponentConnection"
    ) -> "Iterable[_7600.InterMountableComponentConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.InterMountableComponentConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.InterMountableComponentConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_INTER_MOUNTABLE_COMPONENT_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_planetary_connection(
        self: "Self", design_entity: "_2513.PlanetaryConnection"
    ) -> "Iterable[_7620.PlanetaryConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.PlanetaryConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.PlanetaryConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PLANETARY_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_rolling_ring_connection(
        self: "Self", design_entity: "_2518.RollingRingConnection"
    ) -> "Iterable[_7630.RollingRingConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.RollingRingConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.RollingRingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ROLLING_RING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_abstract_shaft_to_mountable_component_connection(
        self: "Self", design_entity: "_2491.AbstractShaftToMountableComponentConnection"
    ) -> "Iterable[_7538.AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.AbstractShaftToMountableComponentConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.AbstractShaftToMountableComponentConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ABSTRACT_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_differential_gear_mesh(
        self: "Self", design_entity: "_2527.BevelDifferentialGearMesh"
    ) -> "Iterable[_7547.BevelDifferentialGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BevelDifferentialGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.BevelDifferentialGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_DIFFERENTIAL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_concept_gear_mesh(
        self: "Self", design_entity: "_2531.ConceptGearMesh"
    ) -> "Iterable[_7565.ConceptGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConceptGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.ConceptGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONCEPT_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_face_gear_mesh(
        self: "Self", design_entity: "_2537.FaceGearMesh"
    ) -> "Iterable[_7589.FaceGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.FaceGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.FaceGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_FACE_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_diff_gear_mesh(
        self: "Self", design_entity: "_2551.StraightBevelDiffGearMesh"
    ) -> "Iterable[_7643.StraightBevelDiffGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.StraightBevelDiffGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.StraightBevelDiffGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_DIFF_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_bevel_gear_mesh(
        self: "Self", design_entity: "_2529.BevelGearMesh"
    ) -> "Iterable[_7552.BevelGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.BevelGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.BevelGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_BEVEL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_conical_gear_mesh(
        self: "Self", design_entity: "_2533.ConicalGearMesh"
    ) -> "Iterable[_7568.ConicalGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ConicalGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.ConicalGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CONICAL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_agma_gleason_conical_gear_mesh(
        self: "Self", design_entity: "_2525.AGMAGleasonConicalGearMesh"
    ) -> "Iterable[_7540.AGMAGleasonConicalGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.AGMAGleasonConicalGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.AGMAGleasonConicalGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_AGMA_GLEASON_CONICAL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cylindrical_gear_mesh(
        self: "Self", design_entity: "_2535.CylindricalGearMesh"
    ) -> "Iterable[_7583.CylindricalGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CylindricalGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.CylindricalGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYLINDRICAL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_hypoid_gear_mesh(
        self: "Self", design_entity: "_2541.HypoidGearMesh"
    ) -> "Iterable[_7598.HypoidGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.HypoidGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.HypoidGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_HYPOID_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_conical_gear_mesh(
        self: "Self", design_entity: "_2544.KlingelnbergCycloPalloidConicalGearMesh"
    ) -> "Iterable[_7602.KlingelnbergCycloPalloidConicalGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.KlingelnbergCycloPalloidConicalGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidConicalGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_hypoid_gear_mesh(
        self: "Self", design_entity: "_2545.KlingelnbergCycloPalloidHypoidGearMesh"
    ) -> "Iterable[_7605.KlingelnbergCycloPalloidHypoidGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.KlingelnbergCycloPalloidHypoidGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidHypoidGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_HYPOID_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(
        self: "Self", design_entity: "_2546.KlingelnbergCycloPalloidSpiralBevelGearMesh"
    ) -> "Iterable[_7608.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.KlingelnbergCycloPalloidSpiralBevelGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.KlingelnbergCycloPalloidSpiralBevelGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_KLINGELNBERG_CYCLO_PALLOID_SPIRAL_BEVEL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_spiral_bevel_gear_mesh(
        self: "Self", design_entity: "_2549.SpiralBevelGearMesh"
    ) -> "Iterable[_7637.SpiralBevelGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.SpiralBevelGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.SpiralBevelGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_SPIRAL_BEVEL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_straight_bevel_gear_mesh(
        self: "Self", design_entity: "_2553.StraightBevelGearMesh"
    ) -> "Iterable[_7646.StraightBevelGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.StraightBevelGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.StraightBevelGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_STRAIGHT_BEVEL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_worm_gear_mesh(
        self: "Self", design_entity: "_2555.WormGearMesh"
    ) -> "Iterable[_7661.WormGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.WormGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.WormGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_WORM_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_zerol_bevel_gear_mesh(
        self: "Self", design_entity: "_2557.ZerolBevelGearMesh"
    ) -> "Iterable[_7664.ZerolBevelGearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ZerolBevelGearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.ZerolBevelGearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_ZEROL_BEVEL_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_gear_mesh(
        self: "Self", design_entity: "_2539.GearMesh"
    ) -> "Iterable[_7594.GearMeshCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.GearMeshCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.gears.GearMesh)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_GEAR_MESH],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cycloidal_disc_central_bearing_connection(
        self: "Self", design_entity: "_2561.CycloidalDiscCentralBearingConnection"
    ) -> "Iterable[_7579.CycloidalDiscCentralBearingConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CycloidalDiscCentralBearingConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.cycloidal.CycloidalDiscCentralBearingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYCLOIDAL_DISC_CENTRAL_BEARING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_cycloidal_disc_planetary_bearing_connection(
        self: "Self", design_entity: "_2564.CycloidalDiscPlanetaryBearingConnection"
    ) -> "Iterable[_7581.CycloidalDiscPlanetaryBearingConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.CycloidalDiscPlanetaryBearingConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.cycloidal.CycloidalDiscPlanetaryBearingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CYCLOIDAL_DISC_PLANETARY_BEARING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_ring_pins_to_disc_connection(
        self: "Self", design_entity: "_2567.RingPinsToDiscConnection"
    ) -> "Iterable[_7627.RingPinsToDiscConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.RingPinsToDiscConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.cycloidal.RingPinsToDiscConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_RING_PINS_TO_DISC_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_part_to_part_shear_coupling_connection(
        self: "Self", design_entity: "_2574.PartToPartShearCouplingConnection"
    ) -> "Iterable[_7618.PartToPartShearCouplingConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.PartToPartShearCouplingConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.PartToPartShearCouplingConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_PART_TO_PART_SHEAR_COUPLING_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for_clutch_connection(
        self: "Self", design_entity: "_2568.ClutchConnection"
    ) -> "Iterable[_7557.ClutchConnectionCompoundAdvancedSystemDeflection]":
        """Iterable[mastapy.system_model.analyses_and_results.advanced_system_deflections.compound.ClutchConnectionCompoundAdvancedSystemDeflection]

        Args:
            design_entity (mastapy.system_model.connections_and_sockets.couplings.ClutchConnection)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call_overload(
                self.wrapped,
                "ResultsFor",
                [_CLUTCH_CONNECTION],
                design_entity.wrapped if design_entity else None,
            )
        )

    @property
    def cast_to(self: "Self") -> "_Cast_CompoundAdvancedSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_CompoundAdvancedSystemDeflection
        """
        return _Cast_CompoundAdvancedSystemDeflection(self)
