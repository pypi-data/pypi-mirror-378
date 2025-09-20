"""BearingConnectionComponent"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

_BEARING_CONNECTION_COMPONENT = python_net_import(
    "SMT.MastaAPI.Bearings.Tolerances", "BearingConnectionComponent"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.tolerances import (
        _2114,
        _2115,
        _2116,
        _2117,
        _2119,
        _2120,
        _2121,
        _2124,
        _2125,
        _2128,
        _2130,
    )

    Self = TypeVar("Self", bound="BearingConnectionComponent")
    CastSelf = TypeVar(
        "CastSelf", bound="BearingConnectionComponent._Cast_BearingConnectionComponent"
    )


__docformat__ = "restructuredtext en"
__all__ = ("BearingConnectionComponent",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BearingConnectionComponent:
    """Special nested class for casting BearingConnectionComponent to subclasses."""

    __parent__: "BearingConnectionComponent"

    @property
    def inner_ring_tolerance(self: "CastSelf") -> "_2114.InnerRingTolerance":
        from mastapy._private.bearings.tolerances import _2114

        return self.__parent__._cast(_2114.InnerRingTolerance)

    @property
    def inner_support_tolerance(self: "CastSelf") -> "_2115.InnerSupportTolerance":
        from mastapy._private.bearings.tolerances import _2115

        return self.__parent__._cast(_2115.InnerSupportTolerance)

    @property
    def interference_detail(self: "CastSelf") -> "_2116.InterferenceDetail":
        from mastapy._private.bearings.tolerances import _2116

        return self.__parent__._cast(_2116.InterferenceDetail)

    @property
    def interference_tolerance(self: "CastSelf") -> "_2117.InterferenceTolerance":
        from mastapy._private.bearings.tolerances import _2117

        return self.__parent__._cast(_2117.InterferenceTolerance)

    @property
    def mounting_sleeve_diameter_detail(
        self: "CastSelf",
    ) -> "_2119.MountingSleeveDiameterDetail":
        from mastapy._private.bearings.tolerances import _2119

        return self.__parent__._cast(_2119.MountingSleeveDiameterDetail)

    @property
    def outer_ring_tolerance(self: "CastSelf") -> "_2120.OuterRingTolerance":
        from mastapy._private.bearings.tolerances import _2120

        return self.__parent__._cast(_2120.OuterRingTolerance)

    @property
    def outer_support_tolerance(self: "CastSelf") -> "_2121.OuterSupportTolerance":
        from mastapy._private.bearings.tolerances import _2121

        return self.__parent__._cast(_2121.OuterSupportTolerance)

    @property
    def ring_detail(self: "CastSelf") -> "_2124.RingDetail":
        from mastapy._private.bearings.tolerances import _2124

        return self.__parent__._cast(_2124.RingDetail)

    @property
    def ring_tolerance(self: "CastSelf") -> "_2125.RingTolerance":
        from mastapy._private.bearings.tolerances import _2125

        return self.__parent__._cast(_2125.RingTolerance)

    @property
    def support_detail(self: "CastSelf") -> "_2128.SupportDetail":
        from mastapy._private.bearings.tolerances import _2128

        return self.__parent__._cast(_2128.SupportDetail)

    @property
    def support_tolerance(self: "CastSelf") -> "_2130.SupportTolerance":
        from mastapy._private.bearings.tolerances import _2130

        return self.__parent__._cast(_2130.SupportTolerance)

    @property
    def bearing_connection_component(self: "CastSelf") -> "BearingConnectionComponent":
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
class BearingConnectionComponent(_0.APIBase):
    """BearingConnectionComponent

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEARING_CONNECTION_COMPONENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_BearingConnectionComponent":
        """Cast to another type.

        Returns:
            _Cast_BearingConnectionComponent
        """
        return _Cast_BearingConnectionComponent(self)
