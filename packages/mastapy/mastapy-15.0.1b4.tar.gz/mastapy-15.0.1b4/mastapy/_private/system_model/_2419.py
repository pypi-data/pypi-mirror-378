"""DesignEntity"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from PIL.Image import Image

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

_DESIGN_ENTITY = python_net_import("SMT.MastaAPI.SystemModel", "DesignEntity")

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike
    from mastapy._private.system_model import _2416
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
    from mastapy._private.utility.model_validation import _1993, _1994
    from mastapy._private.utility.scripting import _1941

    Self = TypeVar("Self", bound="DesignEntity")
    CastSelf = TypeVar("CastSelf", bound="DesignEntity._Cast_DesignEntity")


__docformat__ = "restructuredtext en"
__all__ = ("DesignEntity",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_DesignEntity:
    """Special nested class for casting DesignEntity to subclasses."""

    __parent__: "DesignEntity"

    @property
    def abstract_shaft_to_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2491.AbstractShaftToMountableComponentConnection":
        from mastapy._private.system_model.connections_and_sockets import _2491

        return self.__parent__._cast(_2491.AbstractShaftToMountableComponentConnection)

    @property
    def belt_connection(self: "CastSelf") -> "_2494.BeltConnection":
        from mastapy._private.system_model.connections_and_sockets import _2494

        return self.__parent__._cast(_2494.BeltConnection)

    @property
    def coaxial_connection(self: "CastSelf") -> "_2495.CoaxialConnection":
        from mastapy._private.system_model.connections_and_sockets import _2495

        return self.__parent__._cast(_2495.CoaxialConnection)

    @property
    def connection(self: "CastSelf") -> "_2498.Connection":
        from mastapy._private.system_model.connections_and_sockets import _2498

        return self.__parent__._cast(_2498.Connection)

    @property
    def cvt_belt_connection(self: "CastSelf") -> "_2499.CVTBeltConnection":
        from mastapy._private.system_model.connections_and_sockets import _2499

        return self.__parent__._cast(_2499.CVTBeltConnection)

    @property
    def inter_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2507.InterMountableComponentConnection":
        from mastapy._private.system_model.connections_and_sockets import _2507

        return self.__parent__._cast(_2507.InterMountableComponentConnection)

    @property
    def planetary_connection(self: "CastSelf") -> "_2513.PlanetaryConnection":
        from mastapy._private.system_model.connections_and_sockets import _2513

        return self.__parent__._cast(_2513.PlanetaryConnection)

    @property
    def rolling_ring_connection(self: "CastSelf") -> "_2518.RollingRingConnection":
        from mastapy._private.system_model.connections_and_sockets import _2518

        return self.__parent__._cast(_2518.RollingRingConnection)

    @property
    def shaft_to_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2521.ShaftToMountableComponentConnection":
        from mastapy._private.system_model.connections_and_sockets import _2521

        return self.__parent__._cast(_2521.ShaftToMountableComponentConnection)

    @property
    def agma_gleason_conical_gear_mesh(
        self: "CastSelf",
    ) -> "_2525.AGMAGleasonConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2525

        return self.__parent__._cast(_2525.AGMAGleasonConicalGearMesh)

    @property
    def bevel_differential_gear_mesh(
        self: "CastSelf",
    ) -> "_2527.BevelDifferentialGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2527

        return self.__parent__._cast(_2527.BevelDifferentialGearMesh)

    @property
    def bevel_gear_mesh(self: "CastSelf") -> "_2529.BevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2529

        return self.__parent__._cast(_2529.BevelGearMesh)

    @property
    def concept_gear_mesh(self: "CastSelf") -> "_2531.ConceptGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2531

        return self.__parent__._cast(_2531.ConceptGearMesh)

    @property
    def conical_gear_mesh(self: "CastSelf") -> "_2533.ConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2533

        return self.__parent__._cast(_2533.ConicalGearMesh)

    @property
    def cylindrical_gear_mesh(self: "CastSelf") -> "_2535.CylindricalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2535

        return self.__parent__._cast(_2535.CylindricalGearMesh)

    @property
    def face_gear_mesh(self: "CastSelf") -> "_2537.FaceGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2537

        return self.__parent__._cast(_2537.FaceGearMesh)

    @property
    def gear_mesh(self: "CastSelf") -> "_2539.GearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2539

        return self.__parent__._cast(_2539.GearMesh)

    @property
    def hypoid_gear_mesh(self: "CastSelf") -> "_2541.HypoidGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2541

        return self.__parent__._cast(_2541.HypoidGearMesh)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh(
        self: "CastSelf",
    ) -> "_2544.KlingelnbergCycloPalloidConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2544

        return self.__parent__._cast(_2544.KlingelnbergCycloPalloidConicalGearMesh)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh(
        self: "CastSelf",
    ) -> "_2545.KlingelnbergCycloPalloidHypoidGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2545

        return self.__parent__._cast(_2545.KlingelnbergCycloPalloidHypoidGearMesh)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(
        self: "CastSelf",
    ) -> "_2546.KlingelnbergCycloPalloidSpiralBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2546

        return self.__parent__._cast(_2546.KlingelnbergCycloPalloidSpiralBevelGearMesh)

    @property
    def spiral_bevel_gear_mesh(self: "CastSelf") -> "_2549.SpiralBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2549

        return self.__parent__._cast(_2549.SpiralBevelGearMesh)

    @property
    def straight_bevel_diff_gear_mesh(
        self: "CastSelf",
    ) -> "_2551.StraightBevelDiffGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2551

        return self.__parent__._cast(_2551.StraightBevelDiffGearMesh)

    @property
    def straight_bevel_gear_mesh(self: "CastSelf") -> "_2553.StraightBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2553

        return self.__parent__._cast(_2553.StraightBevelGearMesh)

    @property
    def worm_gear_mesh(self: "CastSelf") -> "_2555.WormGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2555

        return self.__parent__._cast(_2555.WormGearMesh)

    @property
    def zerol_bevel_gear_mesh(self: "CastSelf") -> "_2557.ZerolBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2557

        return self.__parent__._cast(_2557.ZerolBevelGearMesh)

    @property
    def cycloidal_disc_central_bearing_connection(
        self: "CastSelf",
    ) -> "_2561.CycloidalDiscCentralBearingConnection":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2561,
        )

        return self.__parent__._cast(_2561.CycloidalDiscCentralBearingConnection)

    @property
    def cycloidal_disc_planetary_bearing_connection(
        self: "CastSelf",
    ) -> "_2564.CycloidalDiscPlanetaryBearingConnection":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2564,
        )

        return self.__parent__._cast(_2564.CycloidalDiscPlanetaryBearingConnection)

    @property
    def ring_pins_to_disc_connection(
        self: "CastSelf",
    ) -> "_2567.RingPinsToDiscConnection":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2567,
        )

        return self.__parent__._cast(_2567.RingPinsToDiscConnection)

    @property
    def clutch_connection(self: "CastSelf") -> "_2568.ClutchConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2568,
        )

        return self.__parent__._cast(_2568.ClutchConnection)

    @property
    def concept_coupling_connection(
        self: "CastSelf",
    ) -> "_2570.ConceptCouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2570,
        )

        return self.__parent__._cast(_2570.ConceptCouplingConnection)

    @property
    def coupling_connection(self: "CastSelf") -> "_2572.CouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2572,
        )

        return self.__parent__._cast(_2572.CouplingConnection)

    @property
    def part_to_part_shear_coupling_connection(
        self: "CastSelf",
    ) -> "_2574.PartToPartShearCouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2574,
        )

        return self.__parent__._cast(_2574.PartToPartShearCouplingConnection)

    @property
    def spring_damper_connection(self: "CastSelf") -> "_2576.SpringDamperConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2576,
        )

        return self.__parent__._cast(_2576.SpringDamperConnection)

    @property
    def torque_converter_connection(
        self: "CastSelf",
    ) -> "_2578.TorqueConverterConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2578,
        )

        return self.__parent__._cast(_2578.TorqueConverterConnection)

    @property
    def assembly(self: "CastSelf") -> "_2663.Assembly":
        from mastapy._private.system_model.part_model import _2663

        return self.__parent__._cast(_2663.Assembly)

    @property
    def abstract_assembly(self: "CastSelf") -> "_2664.AbstractAssembly":
        from mastapy._private.system_model.part_model import _2664

        return self.__parent__._cast(_2664.AbstractAssembly)

    @property
    def abstract_shaft(self: "CastSelf") -> "_2665.AbstractShaft":
        from mastapy._private.system_model.part_model import _2665

        return self.__parent__._cast(_2665.AbstractShaft)

    @property
    def abstract_shaft_or_housing(self: "CastSelf") -> "_2666.AbstractShaftOrHousing":
        from mastapy._private.system_model.part_model import _2666

        return self.__parent__._cast(_2666.AbstractShaftOrHousing)

    @property
    def bearing(self: "CastSelf") -> "_2669.Bearing":
        from mastapy._private.system_model.part_model import _2669

        return self.__parent__._cast(_2669.Bearing)

    @property
    def bolt(self: "CastSelf") -> "_2672.Bolt":
        from mastapy._private.system_model.part_model import _2672

        return self.__parent__._cast(_2672.Bolt)

    @property
    def bolted_joint(self: "CastSelf") -> "_2673.BoltedJoint":
        from mastapy._private.system_model.part_model import _2673

        return self.__parent__._cast(_2673.BoltedJoint)

    @property
    def component(self: "CastSelf") -> "_2675.Component":
        from mastapy._private.system_model.part_model import _2675

        return self.__parent__._cast(_2675.Component)

    @property
    def connector(self: "CastSelf") -> "_2678.Connector":
        from mastapy._private.system_model.part_model import _2678

        return self.__parent__._cast(_2678.Connector)

    @property
    def datum(self: "CastSelf") -> "_2679.Datum":
        from mastapy._private.system_model.part_model import _2679

        return self.__parent__._cast(_2679.Datum)

    @property
    def external_cad_model(self: "CastSelf") -> "_2684.ExternalCADModel":
        from mastapy._private.system_model.part_model import _2684

        return self.__parent__._cast(_2684.ExternalCADModel)

    @property
    def fe_part(self: "CastSelf") -> "_2685.FEPart":
        from mastapy._private.system_model.part_model import _2685

        return self.__parent__._cast(_2685.FEPart)

    @property
    def flexible_pin_assembly(self: "CastSelf") -> "_2686.FlexiblePinAssembly":
        from mastapy._private.system_model.part_model import _2686

        return self.__parent__._cast(_2686.FlexiblePinAssembly)

    @property
    def guide_dxf_model(self: "CastSelf") -> "_2687.GuideDxfModel":
        from mastapy._private.system_model.part_model import _2687

        return self.__parent__._cast(_2687.GuideDxfModel)

    @property
    def mass_disc(self: "CastSelf") -> "_2694.MassDisc":
        from mastapy._private.system_model.part_model import _2694

        return self.__parent__._cast(_2694.MassDisc)

    @property
    def measurement_component(self: "CastSelf") -> "_2695.MeasurementComponent":
        from mastapy._private.system_model.part_model import _2695

        return self.__parent__._cast(_2695.MeasurementComponent)

    @property
    def microphone(self: "CastSelf") -> "_2696.Microphone":
        from mastapy._private.system_model.part_model import _2696

        return self.__parent__._cast(_2696.Microphone)

    @property
    def microphone_array(self: "CastSelf") -> "_2697.MicrophoneArray":
        from mastapy._private.system_model.part_model import _2697

        return self.__parent__._cast(_2697.MicrophoneArray)

    @property
    def mountable_component(self: "CastSelf") -> "_2698.MountableComponent":
        from mastapy._private.system_model.part_model import _2698

        return self.__parent__._cast(_2698.MountableComponent)

    @property
    def oil_seal(self: "CastSelf") -> "_2700.OilSeal":
        from mastapy._private.system_model.part_model import _2700

        return self.__parent__._cast(_2700.OilSeal)

    @property
    def part(self: "CastSelf") -> "_2703.Part":
        from mastapy._private.system_model.part_model import _2703

        return self.__parent__._cast(_2703.Part)

    @property
    def planet_carrier(self: "CastSelf") -> "_2705.PlanetCarrier":
        from mastapy._private.system_model.part_model import _2705

        return self.__parent__._cast(_2705.PlanetCarrier)

    @property
    def point_load(self: "CastSelf") -> "_2707.PointLoad":
        from mastapy._private.system_model.part_model import _2707

        return self.__parent__._cast(_2707.PointLoad)

    @property
    def power_load(self: "CastSelf") -> "_2708.PowerLoad":
        from mastapy._private.system_model.part_model import _2708

        return self.__parent__._cast(_2708.PowerLoad)

    @property
    def root_assembly(self: "CastSelf") -> "_2711.RootAssembly":
        from mastapy._private.system_model.part_model import _2711

        return self.__parent__._cast(_2711.RootAssembly)

    @property
    def specialised_assembly(self: "CastSelf") -> "_2713.SpecialisedAssembly":
        from mastapy._private.system_model.part_model import _2713

        return self.__parent__._cast(_2713.SpecialisedAssembly)

    @property
    def unbalanced_mass(self: "CastSelf") -> "_2714.UnbalancedMass":
        from mastapy._private.system_model.part_model import _2714

        return self.__parent__._cast(_2714.UnbalancedMass)

    @property
    def virtual_component(self: "CastSelf") -> "_2716.VirtualComponent":
        from mastapy._private.system_model.part_model import _2716

        return self.__parent__._cast(_2716.VirtualComponent)

    @property
    def shaft(self: "CastSelf") -> "_2719.Shaft":
        from mastapy._private.system_model.part_model.shaft_model import _2719

        return self.__parent__._cast(_2719.Shaft)

    @property
    def agma_gleason_conical_gear(self: "CastSelf") -> "_2755.AGMAGleasonConicalGear":
        from mastapy._private.system_model.part_model.gears import _2755

        return self.__parent__._cast(_2755.AGMAGleasonConicalGear)

    @property
    def agma_gleason_conical_gear_set(
        self: "CastSelf",
    ) -> "_2756.AGMAGleasonConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2756

        return self.__parent__._cast(_2756.AGMAGleasonConicalGearSet)

    @property
    def bevel_differential_gear(self: "CastSelf") -> "_2757.BevelDifferentialGear":
        from mastapy._private.system_model.part_model.gears import _2757

        return self.__parent__._cast(_2757.BevelDifferentialGear)

    @property
    def bevel_differential_gear_set(
        self: "CastSelf",
    ) -> "_2758.BevelDifferentialGearSet":
        from mastapy._private.system_model.part_model.gears import _2758

        return self.__parent__._cast(_2758.BevelDifferentialGearSet)

    @property
    def bevel_differential_planet_gear(
        self: "CastSelf",
    ) -> "_2759.BevelDifferentialPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2759

        return self.__parent__._cast(_2759.BevelDifferentialPlanetGear)

    @property
    def bevel_differential_sun_gear(
        self: "CastSelf",
    ) -> "_2760.BevelDifferentialSunGear":
        from mastapy._private.system_model.part_model.gears import _2760

        return self.__parent__._cast(_2760.BevelDifferentialSunGear)

    @property
    def bevel_gear(self: "CastSelf") -> "_2761.BevelGear":
        from mastapy._private.system_model.part_model.gears import _2761

        return self.__parent__._cast(_2761.BevelGear)

    @property
    def bevel_gear_set(self: "CastSelf") -> "_2762.BevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2762

        return self.__parent__._cast(_2762.BevelGearSet)

    @property
    def concept_gear(self: "CastSelf") -> "_2763.ConceptGear":
        from mastapy._private.system_model.part_model.gears import _2763

        return self.__parent__._cast(_2763.ConceptGear)

    @property
    def concept_gear_set(self: "CastSelf") -> "_2764.ConceptGearSet":
        from mastapy._private.system_model.part_model.gears import _2764

        return self.__parent__._cast(_2764.ConceptGearSet)

    @property
    def conical_gear(self: "CastSelf") -> "_2765.ConicalGear":
        from mastapy._private.system_model.part_model.gears import _2765

        return self.__parent__._cast(_2765.ConicalGear)

    @property
    def conical_gear_set(self: "CastSelf") -> "_2766.ConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2766

        return self.__parent__._cast(_2766.ConicalGearSet)

    @property
    def cylindrical_gear(self: "CastSelf") -> "_2767.CylindricalGear":
        from mastapy._private.system_model.part_model.gears import _2767

        return self.__parent__._cast(_2767.CylindricalGear)

    @property
    def cylindrical_gear_set(self: "CastSelf") -> "_2768.CylindricalGearSet":
        from mastapy._private.system_model.part_model.gears import _2768

        return self.__parent__._cast(_2768.CylindricalGearSet)

    @property
    def cylindrical_planet_gear(self: "CastSelf") -> "_2769.CylindricalPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2769

        return self.__parent__._cast(_2769.CylindricalPlanetGear)

    @property
    def face_gear(self: "CastSelf") -> "_2770.FaceGear":
        from mastapy._private.system_model.part_model.gears import _2770

        return self.__parent__._cast(_2770.FaceGear)

    @property
    def face_gear_set(self: "CastSelf") -> "_2771.FaceGearSet":
        from mastapy._private.system_model.part_model.gears import _2771

        return self.__parent__._cast(_2771.FaceGearSet)

    @property
    def gear(self: "CastSelf") -> "_2772.Gear":
        from mastapy._private.system_model.part_model.gears import _2772

        return self.__parent__._cast(_2772.Gear)

    @property
    def gear_set(self: "CastSelf") -> "_2774.GearSet":
        from mastapy._private.system_model.part_model.gears import _2774

        return self.__parent__._cast(_2774.GearSet)

    @property
    def hypoid_gear(self: "CastSelf") -> "_2776.HypoidGear":
        from mastapy._private.system_model.part_model.gears import _2776

        return self.__parent__._cast(_2776.HypoidGear)

    @property
    def hypoid_gear_set(self: "CastSelf") -> "_2777.HypoidGearSet":
        from mastapy._private.system_model.part_model.gears import _2777

        return self.__parent__._cast(_2777.HypoidGearSet)

    @property
    def klingelnberg_cyclo_palloid_conical_gear(
        self: "CastSelf",
    ) -> "_2778.KlingelnbergCycloPalloidConicalGear":
        from mastapy._private.system_model.part_model.gears import _2778

        return self.__parent__._cast(_2778.KlingelnbergCycloPalloidConicalGear)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set(
        self: "CastSelf",
    ) -> "_2779.KlingelnbergCycloPalloidConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2779

        return self.__parent__._cast(_2779.KlingelnbergCycloPalloidConicalGearSet)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear(
        self: "CastSelf",
    ) -> "_2780.KlingelnbergCycloPalloidHypoidGear":
        from mastapy._private.system_model.part_model.gears import _2780

        return self.__parent__._cast(_2780.KlingelnbergCycloPalloidHypoidGear)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set(
        self: "CastSelf",
    ) -> "_2781.KlingelnbergCycloPalloidHypoidGearSet":
        from mastapy._private.system_model.part_model.gears import _2781

        return self.__parent__._cast(_2781.KlingelnbergCycloPalloidHypoidGearSet)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear(
        self: "CastSelf",
    ) -> "_2782.KlingelnbergCycloPalloidSpiralBevelGear":
        from mastapy._private.system_model.part_model.gears import _2782

        return self.__parent__._cast(_2782.KlingelnbergCycloPalloidSpiralBevelGear)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set(
        self: "CastSelf",
    ) -> "_2783.KlingelnbergCycloPalloidSpiralBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2783

        return self.__parent__._cast(_2783.KlingelnbergCycloPalloidSpiralBevelGearSet)

    @property
    def planetary_gear_set(self: "CastSelf") -> "_2784.PlanetaryGearSet":
        from mastapy._private.system_model.part_model.gears import _2784

        return self.__parent__._cast(_2784.PlanetaryGearSet)

    @property
    def spiral_bevel_gear(self: "CastSelf") -> "_2786.SpiralBevelGear":
        from mastapy._private.system_model.part_model.gears import _2786

        return self.__parent__._cast(_2786.SpiralBevelGear)

    @property
    def spiral_bevel_gear_set(self: "CastSelf") -> "_2787.SpiralBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2787

        return self.__parent__._cast(_2787.SpiralBevelGearSet)

    @property
    def straight_bevel_diff_gear(self: "CastSelf") -> "_2788.StraightBevelDiffGear":
        from mastapy._private.system_model.part_model.gears import _2788

        return self.__parent__._cast(_2788.StraightBevelDiffGear)

    @property
    def straight_bevel_diff_gear_set(
        self: "CastSelf",
    ) -> "_2789.StraightBevelDiffGearSet":
        from mastapy._private.system_model.part_model.gears import _2789

        return self.__parent__._cast(_2789.StraightBevelDiffGearSet)

    @property
    def straight_bevel_gear(self: "CastSelf") -> "_2790.StraightBevelGear":
        from mastapy._private.system_model.part_model.gears import _2790

        return self.__parent__._cast(_2790.StraightBevelGear)

    @property
    def straight_bevel_gear_set(self: "CastSelf") -> "_2791.StraightBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2791

        return self.__parent__._cast(_2791.StraightBevelGearSet)

    @property
    def straight_bevel_planet_gear(self: "CastSelf") -> "_2792.StraightBevelPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2792

        return self.__parent__._cast(_2792.StraightBevelPlanetGear)

    @property
    def straight_bevel_sun_gear(self: "CastSelf") -> "_2793.StraightBevelSunGear":
        from mastapy._private.system_model.part_model.gears import _2793

        return self.__parent__._cast(_2793.StraightBevelSunGear)

    @property
    def worm_gear(self: "CastSelf") -> "_2794.WormGear":
        from mastapy._private.system_model.part_model.gears import _2794

        return self.__parent__._cast(_2794.WormGear)

    @property
    def worm_gear_set(self: "CastSelf") -> "_2795.WormGearSet":
        from mastapy._private.system_model.part_model.gears import _2795

        return self.__parent__._cast(_2795.WormGearSet)

    @property
    def zerol_bevel_gear(self: "CastSelf") -> "_2796.ZerolBevelGear":
        from mastapy._private.system_model.part_model.gears import _2796

        return self.__parent__._cast(_2796.ZerolBevelGear)

    @property
    def zerol_bevel_gear_set(self: "CastSelf") -> "_2797.ZerolBevelGearSet":
        from mastapy._private.system_model.part_model.gears import _2797

        return self.__parent__._cast(_2797.ZerolBevelGearSet)

    @property
    def cycloidal_assembly(self: "CastSelf") -> "_2811.CycloidalAssembly":
        from mastapy._private.system_model.part_model.cycloidal import _2811

        return self.__parent__._cast(_2811.CycloidalAssembly)

    @property
    def cycloidal_disc(self: "CastSelf") -> "_2812.CycloidalDisc":
        from mastapy._private.system_model.part_model.cycloidal import _2812

        return self.__parent__._cast(_2812.CycloidalDisc)

    @property
    def ring_pins(self: "CastSelf") -> "_2813.RingPins":
        from mastapy._private.system_model.part_model.cycloidal import _2813

        return self.__parent__._cast(_2813.RingPins)

    @property
    def belt_drive(self: "CastSelf") -> "_2820.BeltDrive":
        from mastapy._private.system_model.part_model.couplings import _2820

        return self.__parent__._cast(_2820.BeltDrive)

    @property
    def clutch(self: "CastSelf") -> "_2822.Clutch":
        from mastapy._private.system_model.part_model.couplings import _2822

        return self.__parent__._cast(_2822.Clutch)

    @property
    def clutch_half(self: "CastSelf") -> "_2823.ClutchHalf":
        from mastapy._private.system_model.part_model.couplings import _2823

        return self.__parent__._cast(_2823.ClutchHalf)

    @property
    def concept_coupling(self: "CastSelf") -> "_2825.ConceptCoupling":
        from mastapy._private.system_model.part_model.couplings import _2825

        return self.__parent__._cast(_2825.ConceptCoupling)

    @property
    def concept_coupling_half(self: "CastSelf") -> "_2826.ConceptCouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2826

        return self.__parent__._cast(_2826.ConceptCouplingHalf)

    @property
    def coupling(self: "CastSelf") -> "_2828.Coupling":
        from mastapy._private.system_model.part_model.couplings import _2828

        return self.__parent__._cast(_2828.Coupling)

    @property
    def coupling_half(self: "CastSelf") -> "_2829.CouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2829

        return self.__parent__._cast(_2829.CouplingHalf)

    @property
    def cvt(self: "CastSelf") -> "_2831.CVT":
        from mastapy._private.system_model.part_model.couplings import _2831

        return self.__parent__._cast(_2831.CVT)

    @property
    def cvt_pulley(self: "CastSelf") -> "_2832.CVTPulley":
        from mastapy._private.system_model.part_model.couplings import _2832

        return self.__parent__._cast(_2832.CVTPulley)

    @property
    def part_to_part_shear_coupling(
        self: "CastSelf",
    ) -> "_2833.PartToPartShearCoupling":
        from mastapy._private.system_model.part_model.couplings import _2833

        return self.__parent__._cast(_2833.PartToPartShearCoupling)

    @property
    def part_to_part_shear_coupling_half(
        self: "CastSelf",
    ) -> "_2834.PartToPartShearCouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2834

        return self.__parent__._cast(_2834.PartToPartShearCouplingHalf)

    @property
    def pulley(self: "CastSelf") -> "_2836.Pulley":
        from mastapy._private.system_model.part_model.couplings import _2836

        return self.__parent__._cast(_2836.Pulley)

    @property
    def rolling_ring(self: "CastSelf") -> "_2843.RollingRing":
        from mastapy._private.system_model.part_model.couplings import _2843

        return self.__parent__._cast(_2843.RollingRing)

    @property
    def rolling_ring_assembly(self: "CastSelf") -> "_2844.RollingRingAssembly":
        from mastapy._private.system_model.part_model.couplings import _2844

        return self.__parent__._cast(_2844.RollingRingAssembly)

    @property
    def shaft_hub_connection(self: "CastSelf") -> "_2845.ShaftHubConnection":
        from mastapy._private.system_model.part_model.couplings import _2845

        return self.__parent__._cast(_2845.ShaftHubConnection)

    @property
    def spring_damper(self: "CastSelf") -> "_2851.SpringDamper":
        from mastapy._private.system_model.part_model.couplings import _2851

        return self.__parent__._cast(_2851.SpringDamper)

    @property
    def spring_damper_half(self: "CastSelf") -> "_2852.SpringDamperHalf":
        from mastapy._private.system_model.part_model.couplings import _2852

        return self.__parent__._cast(_2852.SpringDamperHalf)

    @property
    def synchroniser(self: "CastSelf") -> "_2853.Synchroniser":
        from mastapy._private.system_model.part_model.couplings import _2853

        return self.__parent__._cast(_2853.Synchroniser)

    @property
    def synchroniser_half(self: "CastSelf") -> "_2855.SynchroniserHalf":
        from mastapy._private.system_model.part_model.couplings import _2855

        return self.__parent__._cast(_2855.SynchroniserHalf)

    @property
    def synchroniser_part(self: "CastSelf") -> "_2856.SynchroniserPart":
        from mastapy._private.system_model.part_model.couplings import _2856

        return self.__parent__._cast(_2856.SynchroniserPart)

    @property
    def synchroniser_sleeve(self: "CastSelf") -> "_2857.SynchroniserSleeve":
        from mastapy._private.system_model.part_model.couplings import _2857

        return self.__parent__._cast(_2857.SynchroniserSleeve)

    @property
    def torque_converter(self: "CastSelf") -> "_2858.TorqueConverter":
        from mastapy._private.system_model.part_model.couplings import _2858

        return self.__parent__._cast(_2858.TorqueConverter)

    @property
    def torque_converter_pump(self: "CastSelf") -> "_2859.TorqueConverterPump":
        from mastapy._private.system_model.part_model.couplings import _2859

        return self.__parent__._cast(_2859.TorqueConverterPump)

    @property
    def torque_converter_turbine(self: "CastSelf") -> "_2861.TorqueConverterTurbine":
        from mastapy._private.system_model.part_model.couplings import _2861

        return self.__parent__._cast(_2861.TorqueConverterTurbine)

    @property
    def design_entity(self: "CastSelf") -> "DesignEntity":
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
class DesignEntity(_0.APIBase):
    """DesignEntity

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _DESIGN_ENTITY

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def comment(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Comment")

        if temp is None:
            return ""

        return temp

    @comment.setter
    @exception_bridge
    @enforce_parameter_types
    def comment(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Comment", str(value) if value is not None else ""
        )

    @property
    @exception_bridge
    def full_name_without_root_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "FullNameWithoutRootName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def id(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ID")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def icon(self: "Self") -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Icon")

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def small_icon(self: "Self") -> "Image":
        """Image

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SmallIcon")

        if temp is None:
            return None

        value = conversion.pn_to_mp_smt_bitmap(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def unique_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "UniqueName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def design_properties(self: "Self") -> "_2416.Design":
        """mastapy.system_model.Design

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DesignProperties")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def all_design_entities(self: "Self") -> "List[DesignEntity]":
        """List[mastapy.system_model.DesignEntity]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AllDesignEntities")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def all_status_errors(self: "Self") -> "List[_1994.StatusItem]":
        """List[mastapy.utility.model_validation.StatusItem]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AllStatusErrors")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def status(self: "Self") -> "_1993.Status":
        """mastapy.utility.model_validation.Status

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Status")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def user_specified_data(self: "Self") -> "_1941.UserSpecifiedData":
        """mastapy.utility.scripting.UserSpecifiedData

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "UserSpecifiedData")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def report_names(self: "Self") -> "List[str]":
        """List[str]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReportNames")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, str)

        if value is None:
            return None

        return value

    @exception_bridge
    def delete(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "Delete")

    @exception_bridge
    @enforce_parameter_types
    def output_default_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputDefaultReportTo", file_path)

    @exception_bridge
    def get_default_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetDefaultReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportTo", file_path)

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_as_text_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportAsTextTo", file_path)

    @exception_bridge
    def get_active_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetActiveReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_masta_report(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsMastaReport",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_text_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsTextTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def get_named_report_with_encoded_images(self: "Self", report_name: "str") -> "str":
        """str

        Args:
            report_name (str)
        """
        report_name = str(report_name)
        method_result = pythonnet_method_call(
            self.wrapped,
            "GetNamedReportWithEncodedImages",
            report_name if report_name else "",
        )
        return method_result

    @property
    def cast_to(self: "Self") -> "_Cast_DesignEntity":
        """Cast to another type.

        Returns:
            _Cast_DesignEntity
        """
        return _Cast_DesignEntity(self)
