"""MicroGeometryInputsLead"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.gears.manufacturing.cylindrical import _736, _737

_MICRO_GEOMETRY_INPUTS_LEAD = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Cylindrical", "MicroGeometryInputsLead"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar

    Self = TypeVar("Self", bound="MicroGeometryInputsLead")
    CastSelf = TypeVar(
        "CastSelf", bound="MicroGeometryInputsLead._Cast_MicroGeometryInputsLead"
    )


__docformat__ = "restructuredtext en"
__all__ = ("MicroGeometryInputsLead",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MicroGeometryInputsLead:
    """Special nested class for casting MicroGeometryInputsLead to subclasses."""

    __parent__: "MicroGeometryInputsLead"

    @property
    def micro_geometry_inputs(self: "CastSelf") -> "_737.MicroGeometryInputs":
        return self.__parent__._cast(_737.MicroGeometryInputs)

    @property
    def micro_geometry_inputs_lead(self: "CastSelf") -> "MicroGeometryInputsLead":
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
class MicroGeometryInputsLead(_737.MicroGeometryInputs[_736.LeadModificationSegment]):
    """MicroGeometryInputsLead

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MICRO_GEOMETRY_INPUTS_LEAD

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def lead_micro_geometry_range(self: "Self") -> "Tuple[float, float]":
        """Tuple[float, float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "LeadMicroGeometryRange")

        if temp is None:
            return None

        value = conversion.pn_to_mp_range(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def number_of_lead_segments(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfLeadSegments")

        if temp is None:
            return 0

        return temp

    @number_of_lead_segments.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_lead_segments(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "NumberOfLeadSegments", int(value) if value is not None else 0
        )

    @property
    def cast_to(self: "Self") -> "_Cast_MicroGeometryInputsLead":
        """Cast to another type.

        Returns:
            _Cast_MicroGeometryInputsLead
        """
        return _Cast_MicroGeometryInputsLead(self)
