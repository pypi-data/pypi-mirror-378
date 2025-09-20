"""MountableComponentSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.connections_and_sockets import _2502

_MOUNTABLE_COMPONENT_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "MountableComponentSocket"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import (
        _2492,
        _2493,
        _2508,
        _2509,
        _2522,
    )

    Self = TypeVar("Self", bound="MountableComponentSocket")
    CastSelf = TypeVar(
        "CastSelf", bound="MountableComponentSocket._Cast_MountableComponentSocket"
    )


__docformat__ = "restructuredtext en"
__all__ = ("MountableComponentSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MountableComponentSocket:
    """Special nested class for casting MountableComponentSocket to subclasses."""

    __parent__: "MountableComponentSocket"

    @property
    def cylindrical_socket(self: "CastSelf") -> "_2502.CylindricalSocket":
        return self.__parent__._cast(_2502.CylindricalSocket)

    @property
    def socket(self: "CastSelf") -> "_2522.Socket":
        from mastapy._private.system_model.connections_and_sockets import _2522

        return self.__parent__._cast(_2522.Socket)

    @property
    def bearing_inner_socket(self: "CastSelf") -> "_2492.BearingInnerSocket":
        from mastapy._private.system_model.connections_and_sockets import _2492

        return self.__parent__._cast(_2492.BearingInnerSocket)

    @property
    def bearing_outer_socket(self: "CastSelf") -> "_2493.BearingOuterSocket":
        from mastapy._private.system_model.connections_and_sockets import _2493

        return self.__parent__._cast(_2493.BearingOuterSocket)

    @property
    def mountable_component_inner_socket(
        self: "CastSelf",
    ) -> "_2508.MountableComponentInnerSocket":
        from mastapy._private.system_model.connections_and_sockets import _2508

        return self.__parent__._cast(_2508.MountableComponentInnerSocket)

    @property
    def mountable_component_outer_socket(
        self: "CastSelf",
    ) -> "_2509.MountableComponentOuterSocket":
        from mastapy._private.system_model.connections_and_sockets import _2509

        return self.__parent__._cast(_2509.MountableComponentOuterSocket)

    @property
    def mountable_component_socket(self: "CastSelf") -> "MountableComponentSocket":
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
class MountableComponentSocket(_2502.CylindricalSocket):
    """MountableComponentSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MOUNTABLE_COMPONENT_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_MountableComponentSocket":
        """Cast to another type.

        Returns:
            _Cast_MountableComponentSocket
        """
        return _Cast_MountableComponentSocket(self)
