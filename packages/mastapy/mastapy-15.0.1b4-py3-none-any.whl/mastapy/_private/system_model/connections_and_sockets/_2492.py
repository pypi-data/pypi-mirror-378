"""BearingInnerSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.connections_and_sockets import _2508

_BEARING_INNER_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "BearingInnerSocket"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import (
        _2502,
        _2510,
        _2522,
    )

    Self = TypeVar("Self", bound="BearingInnerSocket")
    CastSelf = TypeVar("CastSelf", bound="BearingInnerSocket._Cast_BearingInnerSocket")


__docformat__ = "restructuredtext en"
__all__ = ("BearingInnerSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BearingInnerSocket:
    """Special nested class for casting BearingInnerSocket to subclasses."""

    __parent__: "BearingInnerSocket"

    @property
    def mountable_component_inner_socket(
        self: "CastSelf",
    ) -> "_2508.MountableComponentInnerSocket":
        return self.__parent__._cast(_2508.MountableComponentInnerSocket)

    @property
    def mountable_component_socket(
        self: "CastSelf",
    ) -> "_2510.MountableComponentSocket":
        from mastapy._private.system_model.connections_and_sockets import _2510

        return self.__parent__._cast(_2510.MountableComponentSocket)

    @property
    def cylindrical_socket(self: "CastSelf") -> "_2502.CylindricalSocket":
        from mastapy._private.system_model.connections_and_sockets import _2502

        return self.__parent__._cast(_2502.CylindricalSocket)

    @property
    def socket(self: "CastSelf") -> "_2522.Socket":
        from mastapy._private.system_model.connections_and_sockets import _2522

        return self.__parent__._cast(_2522.Socket)

    @property
    def bearing_inner_socket(self: "CastSelf") -> "BearingInnerSocket":
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
class BearingInnerSocket(_2508.MountableComponentInnerSocket):
    """BearingInnerSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEARING_INNER_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_BearingInnerSocket":
        """Cast to another type.

        Returns:
            _Cast_BearingInnerSocket
        """
        return _Cast_BearingInnerSocket(self)
