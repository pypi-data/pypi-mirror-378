"""MountingSleeveDiameterDetail"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.bearings.tolerances import _2116

_MOUNTING_SLEEVE_DIAMETER_DETAIL = python_net_import(
    "SMT.MastaAPI.Bearings.Tolerances", "MountingSleeveDiameterDetail"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.tolerances import _2109

    Self = TypeVar("Self", bound="MountingSleeveDiameterDetail")
    CastSelf = TypeVar(
        "CastSelf",
        bound="MountingSleeveDiameterDetail._Cast_MountingSleeveDiameterDetail",
    )


__docformat__ = "restructuredtext en"
__all__ = ("MountingSleeveDiameterDetail",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MountingSleeveDiameterDetail:
    """Special nested class for casting MountingSleeveDiameterDetail to subclasses."""

    __parent__: "MountingSleeveDiameterDetail"

    @property
    def interference_detail(self: "CastSelf") -> "_2116.InterferenceDetail":
        return self.__parent__._cast(_2116.InterferenceDetail)

    @property
    def bearing_connection_component(
        self: "CastSelf",
    ) -> "_2109.BearingConnectionComponent":
        from mastapy._private.bearings.tolerances import _2109

        return self.__parent__._cast(_2109.BearingConnectionComponent)

    @property
    def mounting_sleeve_diameter_detail(
        self: "CastSelf",
    ) -> "MountingSleeveDiameterDetail":
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
class MountingSleeveDiameterDetail(_2116.InterferenceDetail):
    """MountingSleeveDiameterDetail

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MOUNTING_SLEEVE_DIAMETER_DETAIL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_MountingSleeveDiameterDetail":
        """Cast to another type.

        Returns:
            _Cast_MountingSleeveDiameterDetail
        """
        return _Cast_MountingSleeveDiameterDetail(self)
