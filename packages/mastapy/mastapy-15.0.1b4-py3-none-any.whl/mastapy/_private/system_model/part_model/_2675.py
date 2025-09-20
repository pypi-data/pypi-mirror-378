"""Component"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.implicit import overridable
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_method_call_overload,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private._math.vector_3d import Vector3D
from mastapy._private.system_model.part_model import _2703

_COMPONENT = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Component")
_SOCKET = python_net_import("SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "Socket")

if TYPE_CHECKING:
    from typing import Any, List, Tuple, Type, TypeVar, Union

    from mastapy._private.math_utility import _1683, _1684
    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets import (
        _2496,
        _2498,
        _2517,
        _2522,
    )
    from mastapy._private.system_model.part_model import (
        _2665,
        _2666,
        _2669,
        _2672,
        _2676,
        _2678,
        _2679,
        _2684,
        _2685,
        _2687,
        _2694,
        _2695,
        _2696,
        _2698,
        _2700,
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
    from mastapy._private.system_model.part_model.cycloidal import _2812, _2813
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
    from mastapy._private.system_model.part_model.shaft_model import _2719

    Self = TypeVar("Self", bound="Component")
    CastSelf = TypeVar("CastSelf", bound="Component._Cast_Component")


__docformat__ = "restructuredtext en"
__all__ = ("Component",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Component:
    """Special nested class for casting Component to subclasses."""

    __parent__: "Component"

    @property
    def part(self: "CastSelf") -> "_2703.Part":
        return self.__parent__._cast(_2703.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2419.DesignEntity":
        from mastapy._private.system_model import _2419

        return self.__parent__._cast(_2419.DesignEntity)

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
    def mountable_component(self: "CastSelf") -> "_2698.MountableComponent":
        from mastapy._private.system_model.part_model import _2698

        return self.__parent__._cast(_2698.MountableComponent)

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
    def shaft(self: "CastSelf") -> "_2719.Shaft":
        from mastapy._private.system_model.part_model.shaft_model import _2719

        return self.__parent__._cast(_2719.Shaft)

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
    def cycloidal_disc(self: "CastSelf") -> "_2812.CycloidalDisc":
        from mastapy._private.system_model.part_model.cycloidal import _2812

        return self.__parent__._cast(_2812.CycloidalDisc)

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
    def component(self: "CastSelf") -> "Component":
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
class Component(_2703.Part):
    """Component

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPONENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def additional_modal_damping_ratio(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "AdditionalModalDampingRatio")

        if temp is None:
            return 0.0

        return temp

    @additional_modal_damping_ratio.setter
    @exception_bridge
    @enforce_parameter_types
    def additional_modal_damping_ratio(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "AdditionalModalDampingRatio",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def draw_3d_transparent(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "Draw3DTransparent")

        if temp is None:
            return False

        return temp

    @draw_3d_transparent.setter
    @exception_bridge
    @enforce_parameter_types
    def draw_3d_transparent(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "Draw3DTransparent",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def length(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "Length")

        if temp is None:
            return 0.0

        return temp

    @length.setter
    @exception_bridge
    @enforce_parameter_types
    def length(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "Length", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def polar_inertia(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "PolarInertia")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @polar_inertia.setter
    @exception_bridge
    @enforce_parameter_types
    def polar_inertia(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "PolarInertia", value)

    @property
    @exception_bridge
    def polar_inertia_for_synchroniser_sizing_only(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(
            self.wrapped, "PolarInertiaForSynchroniserSizingOnly"
        )

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @polar_inertia_for_synchroniser_sizing_only.setter
    @exception_bridge
    @enforce_parameter_types
    def polar_inertia_for_synchroniser_sizing_only(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(
            self.wrapped, "PolarInertiaForSynchroniserSizingOnly", value
        )

    @property
    @exception_bridge
    def reason_mass_properties_are_unknown(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReasonMassPropertiesAreUnknown")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def reason_mass_properties_are_zero(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReasonMassPropertiesAreZero")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def translation(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Translation")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def transverse_inertia(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "TransverseInertia")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @transverse_inertia.setter
    @exception_bridge
    @enforce_parameter_types
    def transverse_inertia(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "TransverseInertia", value)

    @property
    @exception_bridge
    def x_axis(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "XAxis")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def y_axis(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "YAxis")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def z_axis(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ZAxis")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def coordinate_system_euler_angles(self: "Self") -> "Vector3D":
        """Vector3D"""
        temp = pythonnet_property_get(self.wrapped, "CoordinateSystemEulerAngles")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @coordinate_system_euler_angles.setter
    @exception_bridge
    @enforce_parameter_types
    def coordinate_system_euler_angles(self: "Self", value: "Vector3D") -> None:
        value = conversion.mp_to_pn_vector3d(value)
        pythonnet_property_set(self.wrapped, "CoordinateSystemEulerAngles", value)

    @property
    @exception_bridge
    def local_coordinate_system(self: "Self") -> "_1683.CoordinateSystem3D":
        """mastapy.math_utility.CoordinateSystem3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "LocalCoordinateSystem")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def position(self: "Self") -> "Vector3D":
        """Vector3D"""
        temp = pythonnet_property_get(self.wrapped, "Position")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @position.setter
    @exception_bridge
    @enforce_parameter_types
    def position(self: "Self", value: "Vector3D") -> None:
        value = conversion.mp_to_pn_vector3d(value)
        pythonnet_property_set(self.wrapped, "Position", value)

    @property
    @exception_bridge
    def component_connections(self: "Self") -> "List[_2496.ComponentConnection]":
        """List[mastapy.system_model.connections_and_sockets.ComponentConnection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentConnections")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def available_socket_offsets(self: "Self") -> "List[str]":
        """List[str]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AvailableSocketOffsets")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, str)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def centre_offset(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "CentreOffset")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def translation_vector(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TranslationVector")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def x_axis_vector(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "XAxisVector")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def y_axis_vector(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "YAxisVector")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def z_axis_vector(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ZAxisVector")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @exception_bridge
    @enforce_parameter_types
    def can_connect_to(self: "Self", component: "Component") -> "bool":
        """bool

        Args:
            component (mastapy.system_model.part_model.Component)
        """
        method_result = pythonnet_method_call(
            self.wrapped, "CanConnectTo", component.wrapped if component else None
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def can_delete_connection(self: "Self", connection: "_2498.Connection") -> "bool":
        """bool

        Args:
            connection (mastapy.system_model.connections_and_sockets.Connection)
        """
        method_result = pythonnet_method_call(
            self.wrapped,
            "CanDeleteConnection",
            connection.wrapped if connection else None,
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def connect_to(
        self: "Self", component: "Component"
    ) -> "_2676.ComponentsConnectedResult":
        """mastapy.system_model.part_model.ComponentsConnectedResult

        Args:
            component (mastapy.system_model.part_model.Component)
        """
        method_result = pythonnet_method_call_overload(
            self.wrapped,
            "ConnectTo",
            [_COMPONENT],
            component.wrapped if component else None,
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def connect_to_socket(
        self: "Self", socket: "_2522.Socket"
    ) -> "_2676.ComponentsConnectedResult":
        """mastapy.system_model.part_model.ComponentsConnectedResult

        Args:
            socket (mastapy.system_model.connections_and_sockets.Socket)
        """
        method_result = pythonnet_method_call_overload(
            self.wrapped, "ConnectTo", [_SOCKET], socket.wrapped if socket else None
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    def create_coordinate_system_editor(self: "Self") -> "_1684.CoordinateSystemEditor":
        """mastapy.math_utility.CoordinateSystemEditor"""
        method_result = pythonnet_method_call(
            self.wrapped, "CreateCoordinateSystemEditor"
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def diameter_at_middle_of_connection(
        self: "Self", connection: "_2498.Connection"
    ) -> "float":
        """float

        Args:
            connection (mastapy.system_model.connections_and_sockets.Connection)
        """
        method_result = pythonnet_method_call(
            self.wrapped,
            "DiameterAtMiddleOfConnection",
            connection.wrapped if connection else None,
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def diameter_of_socket_for(self: "Self", connection: "_2498.Connection") -> "float":
        """float

        Args:
            connection (mastapy.system_model.connections_and_sockets.Connection)
        """
        method_result = pythonnet_method_call(
            self.wrapped,
            "DiameterOfSocketFor",
            connection.wrapped if connection else None,
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def is_coaxially_connected_to(self: "Self", component: "Component") -> "bool":
        """bool

        Args:
            component (mastapy.system_model.part_model.Component)
        """
        method_result = pythonnet_method_call(
            self.wrapped,
            "IsCoaxiallyConnectedTo",
            component.wrapped if component else None,
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def is_directly_connected_to(self: "Self", component: "Component") -> "bool":
        """bool

        Args:
            component (mastapy.system_model.part_model.Component)
        """
        method_result = pythonnet_method_call(
            self.wrapped,
            "IsDirectlyConnectedTo",
            component.wrapped if component else None,
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def is_directly_or_indirectly_connected_to(
        self: "Self", component: "Component"
    ) -> "bool":
        """bool

        Args:
            component (mastapy.system_model.part_model.Component)
        """
        method_result = pythonnet_method_call(
            self.wrapped,
            "IsDirectlyOrIndirectlyConnectedTo",
            component.wrapped if component else None,
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def move_all_concentric_parts_radially(
        self: "Self", delta_x: "float", delta_y: "float"
    ) -> "bool":
        """bool

        Args:
            delta_x (float)
            delta_y (float)
        """
        delta_x = float(delta_x)
        delta_y = float(delta_y)
        method_result = pythonnet_method_call(
            self.wrapped,
            "MoveAllConcentricPartsRadially",
            delta_x if delta_x else 0.0,
            delta_y if delta_y else 0.0,
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def move_along_axis(self: "Self", delta: "float") -> None:
        """Method does not return.

        Args:
            delta (float)
        """
        delta = float(delta)
        pythonnet_method_call(self.wrapped, "MoveAlongAxis", delta if delta else 0.0)

    @exception_bridge
    @enforce_parameter_types
    def move_with_concentric_parts_to_new_origin(
        self: "Self", target_origin: "Vector3D"
    ) -> "bool":
        """bool

        Args:
            target_origin (Vector3D)
        """
        target_origin = conversion.mp_to_pn_vector3d(target_origin)
        method_result = pythonnet_method_call(
            self.wrapped, "MoveWithConcentricPartsToNewOrigin", target_origin
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def possible_sockets_to_connect_with_component(
        self: "Self", component: "Component"
    ) -> "List[_2522.Socket]":
        """List[mastapy.system_model.connections_and_sockets.Socket]

        Args:
            component (mastapy.system_model.part_model.Component)
        """
        return conversion.pn_to_mp_objects_in_list(
            pythonnet_method_call_overload(
                self.wrapped,
                "PossibleSocketsToConnectWith",
                [_COMPONENT],
                component.wrapped if component else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def possible_sockets_to_connect_with(
        self: "Self", socket: "_2522.Socket"
    ) -> "List[_2522.Socket]":
        """List[mastapy.system_model.connections_and_sockets.Socket]

        Args:
            socket (mastapy.system_model.connections_and_sockets.Socket)
        """
        return conversion.pn_to_mp_objects_in_list(
            pythonnet_method_call_overload(
                self.wrapped,
                "PossibleSocketsToConnectWith",
                [_SOCKET],
                socket.wrapped if socket else None,
            )
        )

    @exception_bridge
    @enforce_parameter_types
    def set_position_and_axis_of_component_and_connected_components(
        self: "Self", origin: "Vector3D", z_axis: "Vector3D"
    ) -> "_2517.RealignmentResult":
        """mastapy.system_model.connections_and_sockets.RealignmentResult

        Args:
            origin (Vector3D)
            z_axis (Vector3D)
        """
        origin = conversion.mp_to_pn_vector3d(origin)
        z_axis = conversion.mp_to_pn_vector3d(z_axis)
        method_result = pythonnet_method_call(
            self.wrapped,
            "SetPositionAndAxisOfComponentAndConnectedComponents",
            origin,
            z_axis,
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def set_position_and_rotation_of_component_and_connected_components(
        self: "Self", new_coordinate_system: "_1683.CoordinateSystem3D"
    ) -> "_2517.RealignmentResult":
        """mastapy.system_model.connections_and_sockets.RealignmentResult

        Args:
            new_coordinate_system (mastapy.math_utility.CoordinateSystem3D)
        """
        method_result = pythonnet_method_call(
            self.wrapped,
            "SetPositionAndRotationOfComponentAndConnectedComponents",
            new_coordinate_system.wrapped if new_coordinate_system else None,
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def set_position_of_component_and_connected_components(
        self: "Self", position: "Vector3D"
    ) -> "_2517.RealignmentResult":
        """mastapy.system_model.connections_and_sockets.RealignmentResult

        Args:
            position (Vector3D)
        """
        position = conversion.mp_to_pn_vector3d(position)
        method_result = pythonnet_method_call(
            self.wrapped, "SetPositionOfComponentAndConnectedComponents", position
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def socket_named(self: "Self", socket_name: "str") -> "_2522.Socket":
        """mastapy.system_model.connections_and_sockets.Socket

        Args:
            socket_name (str)
        """
        socket_name = str(socket_name)
        method_result = pythonnet_method_call(
            self.wrapped, "SocketNamed", socket_name if socket_name else ""
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def try_connect_to(
        self: "Self", component: "Component", hint_offset: "float" = float("nan")
    ) -> "_2676.ComponentsConnectedResult":
        """mastapy.system_model.part_model.ComponentsConnectedResult

        Args:
            component (mastapy.system_model.part_model.Component)
            hint_offset (float, optional)
        """
        hint_offset = float(hint_offset)
        method_result = pythonnet_method_call(
            self.wrapped,
            "TryConnectTo",
            component.wrapped if component else None,
            hint_offset if hint_offset else 0.0,
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @property
    def cast_to(self: "Self") -> "_Cast_Component":
        """Cast to another type.

        Returns:
            _Cast_Component
        """
        return _Cast_Component(self)
