"""FrictionSources"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

_FRICTION_SOURCES = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule", "FrictionSources"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="FrictionSources")
    CastSelf = TypeVar("CastSelf", bound="FrictionSources._Cast_FrictionSources")


__docformat__ = "restructuredtext en"
__all__ = ("FrictionSources",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_FrictionSources:
    """Special nested class for casting FrictionSources to subclasses."""

    __parent__: "FrictionSources"

    @property
    def friction_sources(self: "CastSelf") -> "FrictionSources":
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
class FrictionSources(_0.APIBase):
    """FrictionSources

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _FRICTION_SOURCES

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def drag_loss(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DragLoss")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def rolling(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Rolling")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def seals(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Seals")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def sliding(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Sliding")

        if temp is None:
            return 0.0

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_FrictionSources":
        """Cast to another type.

        Returns:
            _Cast_FrictionSources
        """
        return _Cast_FrictionSources(self)
