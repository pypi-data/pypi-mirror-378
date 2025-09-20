"""ShaftAxialBendingXBendingYTorsionalComponentValues"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.shafts import _18

_SHAFT_AXIAL_BENDING_X_BENDING_Y_TORSIONAL_COMPONENT_VALUES = python_net_import(
    "SMT.MastaAPI.Shafts", "ShaftAxialBendingXBendingYTorsionalComponentValues"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="ShaftAxialBendingXBendingYTorsionalComponentValues")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ShaftAxialBendingXBendingYTorsionalComponentValues._Cast_ShaftAxialBendingXBendingYTorsionalComponentValues",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ShaftAxialBendingXBendingYTorsionalComponentValues",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ShaftAxialBendingXBendingYTorsionalComponentValues:
    """Special nested class for casting ShaftAxialBendingXBendingYTorsionalComponentValues to subclasses."""

    __parent__: "ShaftAxialBendingXBendingYTorsionalComponentValues"

    @property
    def shaft_axial_torsional_component_values(
        self: "CastSelf",
    ) -> "_18.ShaftAxialTorsionalComponentValues":
        return self.__parent__._cast(_18.ShaftAxialTorsionalComponentValues)

    @property
    def shaft_axial_bending_x_bending_y_torsional_component_values(
        self: "CastSelf",
    ) -> "ShaftAxialBendingXBendingYTorsionalComponentValues":
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
class ShaftAxialBendingXBendingYTorsionalComponentValues(
    _18.ShaftAxialTorsionalComponentValues
):
    """ShaftAxialBendingXBendingYTorsionalComponentValues

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SHAFT_AXIAL_BENDING_X_BENDING_Y_TORSIONAL_COMPONENT_VALUES

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def bending_x(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BendingX")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def bending_y(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BendingY")

        if temp is None:
            return 0.0

        return temp

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_ShaftAxialBendingXBendingYTorsionalComponentValues":
        """Cast to another type.

        Returns:
            _Cast_ShaftAxialBendingXBendingYTorsionalComponentValues
        """
        return _Cast_ShaftAxialBendingXBendingYTorsionalComponentValues(self)
