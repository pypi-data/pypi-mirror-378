"""MountableComponent"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
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
from mastapy._private.system_model.part_model import _2675

_MOUNTABLE_COMPONENT = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "MountableComponent"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets import (
        _2495,
        _2498,
        _2502,
    )
    from mastapy._private.system_model.part_model import (
        _2665,
        _2669,
        _2676,
        _2678,
        _2694,
        _2695,
        _2700,
        _2703,
        _2705,
        _2707,
        _2708,
        _2714,
        _2716,
    )
    from mastapy._private.system_model.part_model.couplings import (
        _2823,
        _2826,
        _2829,
        _2832,
        _2834,
        _2836,
        _2843,
        _2845,
        _2852,
        _2855,
        _2856,
        _2857,
        _2859,
        _2861,
    )
    from mastapy._private.system_model.part_model.cycloidal import _2813
    from mastapy._private.system_model.part_model.gears import (
        _2755,
        _2757,
        _2759,
        _2760,
        _2761,
        _2763,
        _2765,
        _2767,
        _2769,
        _2770,
        _2772,
        _2776,
        _2778,
        _2780,
        _2782,
        _2786,
        _2788,
        _2790,
        _2792,
        _2793,
        _2794,
        _2796,
    )

    Self = TypeVar("Self", bound="MountableComponent")
    CastSelf = TypeVar("CastSelf", bound="MountableComponent._Cast_MountableComponent")


__docformat__ = "restructuredtext en"
__all__ = ("MountableComponent",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MountableComponent:
    """Special nested class for casting MountableComponent to subclasses."""

    __parent__: "MountableComponent"

    @property
    def component(self: "CastSelf") -> "_2675.Component":
        return self.__parent__._cast(_2675.Component)

    @property
    def part(self: "CastSelf") -> "_2703.Part":
        from mastapy._private.system_model.part_model import _2703

        return self.__parent__._cast(_2703.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2419.DesignEntity":
        from mastapy._private.system_model import _2419

        return self.__parent__._cast(_2419.DesignEntity)

    @property
    def bearing(self: "CastSelf") -> "_2669.Bearing":
        from mastapy._private.system_model.part_model import _2669

        return self.__parent__._cast(_2669.Bearing)

    @property
    def connector(self: "CastSelf") -> "_2678.Connector":
        from mastapy._private.system_model.part_model import _2678

        return self.__parent__._cast(_2678.Connector)

    @property
    def mass_disc(self: "CastSelf") -> "_2694.MassDisc":
        from mastapy._private.system_model.part_model import _2694

        return self.__parent__._cast(_2694.MassDisc)

    @property
    def measurement_component(self: "CastSelf") -> "_2695.MeasurementComponent":
        from mastapy._private.system_model.part_model import _2695

        return self.__parent__._cast(_2695.MeasurementComponent)

    @property
    def oil_seal(self: "CastSelf") -> "_2700.OilSeal":
        from mastapy._private.system_model.part_model import _2700

        return self.__parent__._cast(_2700.OilSeal)

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
    def unbalanced_mass(self: "CastSelf") -> "_2714.UnbalancedMass":
        from mastapy._private.system_model.part_model import _2714

        return self.__parent__._cast(_2714.UnbalancedMass)

    @property
    def virtual_component(self: "CastSelf") -> "_2716.VirtualComponent":
        from mastapy._private.system_model.part_model import _2716

        return self.__parent__._cast(_2716.VirtualComponent)

    @property
    def agma_gleason_conical_gear(self: "CastSelf") -> "_2755.AGMAGleasonConicalGear":
        from mastapy._private.system_model.part_model.gears import _2755

        return self.__parent__._cast(_2755.AGMAGleasonConicalGear)

    @property
    def bevel_differential_gear(self: "CastSelf") -> "_2757.BevelDifferentialGear":
        from mastapy._private.system_model.part_model.gears import _2757

        return self.__parent__._cast(_2757.BevelDifferentialGear)

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
    def concept_gear(self: "CastSelf") -> "_2763.ConceptGear":
        from mastapy._private.system_model.part_model.gears import _2763

        return self.__parent__._cast(_2763.ConceptGear)

    @property
    def conical_gear(self: "CastSelf") -> "_2765.ConicalGear":
        from mastapy._private.system_model.part_model.gears import _2765

        return self.__parent__._cast(_2765.ConicalGear)

    @property
    def cylindrical_gear(self: "CastSelf") -> "_2767.CylindricalGear":
        from mastapy._private.system_model.part_model.gears import _2767

        return self.__parent__._cast(_2767.CylindricalGear)

    @property
    def cylindrical_planet_gear(self: "CastSelf") -> "_2769.CylindricalPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2769

        return self.__parent__._cast(_2769.CylindricalPlanetGear)

    @property
    def face_gear(self: "CastSelf") -> "_2770.FaceGear":
        from mastapy._private.system_model.part_model.gears import _2770

        return self.__parent__._cast(_2770.FaceGear)

    @property
    def gear(self: "CastSelf") -> "_2772.Gear":
        from mastapy._private.system_model.part_model.gears import _2772

        return self.__parent__._cast(_2772.Gear)

    @property
    def hypoid_gear(self: "CastSelf") -> "_2776.HypoidGear":
        from mastapy._private.system_model.part_model.gears import _2776

        return self.__parent__._cast(_2776.HypoidGear)

    @property
    def klingelnberg_cyclo_palloid_conical_gear(
        self: "CastSelf",
    ) -> "_2778.KlingelnbergCycloPalloidConicalGear":
        from mastapy._private.system_model.part_model.gears import _2778

        return self.__parent__._cast(_2778.KlingelnbergCycloPalloidConicalGear)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear(
        self: "CastSelf",
    ) -> "_2780.KlingelnbergCycloPalloidHypoidGear":
        from mastapy._private.system_model.part_model.gears import _2780

        return self.__parent__._cast(_2780.KlingelnbergCycloPalloidHypoidGear)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear(
        self: "CastSelf",
    ) -> "_2782.KlingelnbergCycloPalloidSpiralBevelGear":
        from mastapy._private.system_model.part_model.gears import _2782

        return self.__parent__._cast(_2782.KlingelnbergCycloPalloidSpiralBevelGear)

    @property
    def spiral_bevel_gear(self: "CastSelf") -> "_2786.SpiralBevelGear":
        from mastapy._private.system_model.part_model.gears import _2786

        return self.__parent__._cast(_2786.SpiralBevelGear)

    @property
    def straight_bevel_diff_gear(self: "CastSelf") -> "_2788.StraightBevelDiffGear":
        from mastapy._private.system_model.part_model.gears import _2788

        return self.__parent__._cast(_2788.StraightBevelDiffGear)

    @property
    def straight_bevel_gear(self: "CastSelf") -> "_2790.StraightBevelGear":
        from mastapy._private.system_model.part_model.gears import _2790

        return self.__parent__._cast(_2790.StraightBevelGear)

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
    def zerol_bevel_gear(self: "CastSelf") -> "_2796.ZerolBevelGear":
        from mastapy._private.system_model.part_model.gears import _2796

        return self.__parent__._cast(_2796.ZerolBevelGear)

    @property
    def ring_pins(self: "CastSelf") -> "_2813.RingPins":
        from mastapy._private.system_model.part_model.cycloidal import _2813

        return self.__parent__._cast(_2813.RingPins)

    @property
    def clutch_half(self: "CastSelf") -> "_2823.ClutchHalf":
        from mastapy._private.system_model.part_model.couplings import _2823

        return self.__parent__._cast(_2823.ClutchHalf)

    @property
    def concept_coupling_half(self: "CastSelf") -> "_2826.ConceptCouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2826

        return self.__parent__._cast(_2826.ConceptCouplingHalf)

    @property
    def coupling_half(self: "CastSelf") -> "_2829.CouplingHalf":
        from mastapy._private.system_model.part_model.couplings import _2829

        return self.__parent__._cast(_2829.CouplingHalf)

    @property
    def cvt_pulley(self: "CastSelf") -> "_2832.CVTPulley":
        from mastapy._private.system_model.part_model.couplings import _2832

        return self.__parent__._cast(_2832.CVTPulley)

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
    def shaft_hub_connection(self: "CastSelf") -> "_2845.ShaftHubConnection":
        from mastapy._private.system_model.part_model.couplings import _2845

        return self.__parent__._cast(_2845.ShaftHubConnection)

    @property
    def spring_damper_half(self: "CastSelf") -> "_2852.SpringDamperHalf":
        from mastapy._private.system_model.part_model.couplings import _2852

        return self.__parent__._cast(_2852.SpringDamperHalf)

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
    def torque_converter_pump(self: "CastSelf") -> "_2859.TorqueConverterPump":
        from mastapy._private.system_model.part_model.couplings import _2859

        return self.__parent__._cast(_2859.TorqueConverterPump)

    @property
    def torque_converter_turbine(self: "CastSelf") -> "_2861.TorqueConverterTurbine":
        from mastapy._private.system_model.part_model.couplings import _2861

        return self.__parent__._cast(_2861.TorqueConverterTurbine)

    @property
    def mountable_component(self: "CastSelf") -> "MountableComponent":
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
class MountableComponent(_2675.Component):
    """MountableComponent

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MOUNTABLE_COMPONENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def rotation_about_axis(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "RotationAboutAxis")

        if temp is None:
            return 0.0

        return temp

    @rotation_about_axis.setter
    @exception_bridge
    @enforce_parameter_types
    def rotation_about_axis(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "RotationAboutAxis",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def inner_component(self: "Self") -> "_2665.AbstractShaft":
        """mastapy.system_model.part_model.AbstractShaft

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerComponent")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def inner_connection(self: "Self") -> "_2498.Connection":
        """mastapy.system_model.connections_and_sockets.Connection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerConnection")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def inner_socket(self: "Self") -> "_2502.CylindricalSocket":
        """mastapy.system_model.connections_and_sockets.CylindricalSocket

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerSocket")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def is_mounted(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsMounted")

        if temp is None:
            return False

        return temp

    @exception_bridge
    @enforce_parameter_types
    def mount_on(
        self: "Self", shaft: "_2665.AbstractShaft", offset: "float" = float("nan")
    ) -> "_2495.CoaxialConnection":
        """mastapy.system_model.connections_and_sockets.CoaxialConnection

        Args:
            shaft (mastapy.system_model.part_model.AbstractShaft)
            offset (float, optional)
        """
        offset = float(offset)
        method_result = pythonnet_method_call(
            self.wrapped,
            "MountOn",
            shaft.wrapped if shaft else None,
            offset if offset else 0.0,
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def try_mount_on(
        self: "Self", shaft: "_2665.AbstractShaft", offset: "float" = float("nan")
    ) -> "_2676.ComponentsConnectedResult":
        """mastapy.system_model.part_model.ComponentsConnectedResult

        Args:
            shaft (mastapy.system_model.part_model.AbstractShaft)
            offset (float, optional)
        """
        offset = float(offset)
        method_result = pythonnet_method_call(
            self.wrapped,
            "TryMountOn",
            shaft.wrapped if shaft else None,
            offset if offset else 0.0,
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @property
    def cast_to(self: "Self") -> "_Cast_MountableComponent":
        """Cast to another type.

        Returns:
            _Cast_MountableComponent
        """
        return _Cast_MountableComponent(self)
