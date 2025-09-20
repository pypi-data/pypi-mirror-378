"""InnerSupportTolerance"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.bearings.tolerances import _2130

_INNER_SUPPORT_TOLERANCE = python_net_import(
    "SMT.MastaAPI.Bearings.Tolerances", "InnerSupportTolerance"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.tolerances import _2109, _2117

    Self = TypeVar("Self", bound="InnerSupportTolerance")
    CastSelf = TypeVar(
        "CastSelf", bound="InnerSupportTolerance._Cast_InnerSupportTolerance"
    )


__docformat__ = "restructuredtext en"
__all__ = ("InnerSupportTolerance",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InnerSupportTolerance:
    """Special nested class for casting InnerSupportTolerance to subclasses."""

    __parent__: "InnerSupportTolerance"

    @property
    def support_tolerance(self: "CastSelf") -> "_2130.SupportTolerance":
        return self.__parent__._cast(_2130.SupportTolerance)

    @property
    def interference_tolerance(self: "CastSelf") -> "_2117.InterferenceTolerance":
        from mastapy._private.bearings.tolerances import _2117

        return self.__parent__._cast(_2117.InterferenceTolerance)

    @property
    def bearing_connection_component(
        self: "CastSelf",
    ) -> "_2109.BearingConnectionComponent":
        from mastapy._private.bearings.tolerances import _2109

        return self.__parent__._cast(_2109.BearingConnectionComponent)

    @property
    def inner_support_tolerance(self: "CastSelf") -> "InnerSupportTolerance":
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
class InnerSupportTolerance(_2130.SupportTolerance):
    """InnerSupportTolerance

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _INNER_SUPPORT_TOLERANCE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_InnerSupportTolerance":
        """Cast to another type.

        Returns:
            _Cast_InnerSupportTolerance
        """
        return _Cast_InnerSupportTolerance(self)
