"""ConicalGear"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.system_model.part_model.gears import _2772

_CONICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConicalGear"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.gear_designs.conical import _1274
    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.part_model import _2675, _2698, _2703
    from mastapy._private.system_model.part_model.gears import (
        _2755,
        _2757,
        _2759,
        _2760,
        _2761,
        _2773,
        _2776,
        _2778,
        _2780,
        _2782,
        _2786,
        _2788,
        _2790,
        _2792,
        _2793,
        _2796,
    )

    Self = TypeVar("Self", bound="ConicalGear")
    CastSelf = TypeVar("CastSelf", bound="ConicalGear._Cast_ConicalGear")


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGear",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGear:
    """Special nested class for casting ConicalGear to subclasses."""

    __parent__: "ConicalGear"

    @property
    def gear(self: "CastSelf") -> "_2772.Gear":
        return self.__parent__._cast(_2772.Gear)

    @property
    def mountable_component(self: "CastSelf") -> "_2698.MountableComponent":
        from mastapy._private.system_model.part_model import _2698

        return self.__parent__._cast(_2698.MountableComponent)

    @property
    def component(self: "CastSelf") -> "_2675.Component":
        from mastapy._private.system_model.part_model import _2675

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
    def zerol_bevel_gear(self: "CastSelf") -> "_2796.ZerolBevelGear":
        from mastapy._private.system_model.part_model.gears import _2796

        return self.__parent__._cast(_2796.ZerolBevelGear)

    @property
    def conical_gear(self: "CastSelf") -> "ConicalGear":
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
class ConicalGear(_2772.Gear):
    """ConicalGear

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_GEAR

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def length(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Length")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def orientation(self: "Self") -> "_2773.GearOrientations":
        """mastapy.system_model.part_model.gears.GearOrientations"""
        temp = pythonnet_property_get(self.wrapped, "Orientation")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.SystemModel.PartModel.Gears.GearOrientations"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.system_model.part_model.gears._2773", "GearOrientations"
        )(value)

    @orientation.setter
    @exception_bridge
    @enforce_parameter_types
    def orientation(self: "Self", value: "_2773.GearOrientations") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.SystemModel.PartModel.Gears.GearOrientations"
        )
        pythonnet_property_set(self.wrapped, "Orientation", value)

    @property
    @exception_bridge
    def active_gear_design(self: "Self") -> "_1274.ConicalGearDesign":
        """mastapy.gears.gear_designs.conical.ConicalGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ActiveGearDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def conical_gear_design(self: "Self") -> "_1274.ConicalGearDesign":
        """mastapy.gears.gear_designs.conical.ConicalGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalGearDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalGear":
        """Cast to another type.

        Returns:
            _Cast_ConicalGear
        """
        return _Cast_ConicalGear(self)
