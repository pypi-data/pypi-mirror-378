"""SpiralBevelGear"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.part_model.gears import _2761

_SPIRAL_BEVEL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "SpiralBevelGear"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.gear_designs.spiral_bevel import _1073
    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.part_model import _2675, _2698, _2703
    from mastapy._private.system_model.part_model.gears import _2755, _2765, _2772

    Self = TypeVar("Self", bound="SpiralBevelGear")
    CastSelf = TypeVar("CastSelf", bound="SpiralBevelGear._Cast_SpiralBevelGear")


__docformat__ = "restructuredtext en"
__all__ = ("SpiralBevelGear",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SpiralBevelGear:
    """Special nested class for casting SpiralBevelGear to subclasses."""

    __parent__: "SpiralBevelGear"

    @property
    def bevel_gear(self: "CastSelf") -> "_2761.BevelGear":
        return self.__parent__._cast(_2761.BevelGear)

    @property
    def agma_gleason_conical_gear(self: "CastSelf") -> "_2755.AGMAGleasonConicalGear":
        from mastapy._private.system_model.part_model.gears import _2755

        return self.__parent__._cast(_2755.AGMAGleasonConicalGear)

    @property
    def conical_gear(self: "CastSelf") -> "_2765.ConicalGear":
        from mastapy._private.system_model.part_model.gears import _2765

        return self.__parent__._cast(_2765.ConicalGear)

    @property
    def gear(self: "CastSelf") -> "_2772.Gear":
        from mastapy._private.system_model.part_model.gears import _2772

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
    def spiral_bevel_gear(self: "CastSelf") -> "SpiralBevelGear":
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
class SpiralBevelGear(_2761.BevelGear):
    """SpiralBevelGear

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SPIRAL_BEVEL_GEAR

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def bevel_gear_design(self: "Self") -> "_1073.SpiralBevelGearDesign":
        """mastapy.gears.gear_designs.spiral_bevel.SpiralBevelGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BevelGearDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def spiral_bevel_gear_design(self: "Self") -> "_1073.SpiralBevelGearDesign":
        """mastapy.gears.gear_designs.spiral_bevel.SpiralBevelGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SpiralBevelGearDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_SpiralBevelGear":
        """Cast to another type.

        Returns:
            _Cast_SpiralBevelGear
        """
        return _Cast_SpiralBevelGear(self)
