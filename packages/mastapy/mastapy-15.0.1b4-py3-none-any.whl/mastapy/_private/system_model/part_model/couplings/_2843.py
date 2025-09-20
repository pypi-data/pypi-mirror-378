"""RollingRing"""

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
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.system_model.part_model.couplings import _2829

_ROLLING_RING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "RollingRing"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    from mastapy._private.gears import _424
    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.part_model import _2675, _2698, _2703

    Self = TypeVar("Self", bound="RollingRing")
    CastSelf = TypeVar("CastSelf", bound="RollingRing._Cast_RollingRing")


__docformat__ = "restructuredtext en"
__all__ = ("RollingRing",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_RollingRing:
    """Special nested class for casting RollingRing to subclasses."""

    __parent__: "RollingRing"

    @property
    def coupling_half(self: "CastSelf") -> "_2829.CouplingHalf":
        return self.__parent__._cast(_2829.CouplingHalf)

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
    def rolling_ring(self: "CastSelf") -> "RollingRing":
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
class RollingRing(_2829.CouplingHalf):
    """RollingRing

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ROLLING_RING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def average_diameter(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "AverageDiameter")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @average_diameter.setter
    @exception_bridge
    @enforce_parameter_types
    def average_diameter(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "AverageDiameter", value)

    @property
    @exception_bridge
    def is_internal(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "IsInternal")

        if temp is None:
            return False

        return temp

    @is_internal.setter
    @exception_bridge
    @enforce_parameter_types
    def is_internal(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped, "IsInternal", bool(value) if value is not None else False
        )

    @property
    @exception_bridge
    def largest_end(self: "Self") -> "_424.Hand":
        """mastapy.gears.Hand"""
        temp = pythonnet_property_get(self.wrapped, "LargestEnd")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(temp, "SMT.MastaAPI.Gears.Hand")

        if value is None:
            return None

        return constructor.new_from_mastapy("mastapy._private.gears._424", "Hand")(
            value
        )

    @largest_end.setter
    @exception_bridge
    @enforce_parameter_types
    def largest_end(self: "Self", value: "_424.Hand") -> None:
        value = conversion.mp_to_pn_enum(value, "SMT.MastaAPI.Gears.Hand")
        pythonnet_property_set(self.wrapped, "LargestEnd", value)

    @property
    def cast_to(self: "Self") -> "_Cast_RollingRing":
        """Cast to another type.

        Returns:
            _Cast_RollingRing
        """
        return _Cast_RollingRing(self)
