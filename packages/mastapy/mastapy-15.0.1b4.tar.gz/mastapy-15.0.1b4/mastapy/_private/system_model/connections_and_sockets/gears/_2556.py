"""WormGearTeethSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.connections_and_sockets.gears import _2540

_WORM_GEAR_TEETH_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "WormGearTeethSocket"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import _2522

    Self = TypeVar("Self", bound="WormGearTeethSocket")
    CastSelf = TypeVar(
        "CastSelf", bound="WormGearTeethSocket._Cast_WormGearTeethSocket"
    )


__docformat__ = "restructuredtext en"
__all__ = ("WormGearTeethSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_WormGearTeethSocket:
    """Special nested class for casting WormGearTeethSocket to subclasses."""

    __parent__: "WormGearTeethSocket"

    @property
    def gear_teeth_socket(self: "CastSelf") -> "_2540.GearTeethSocket":
        return self.__parent__._cast(_2540.GearTeethSocket)

    @property
    def socket(self: "CastSelf") -> "_2522.Socket":
        from mastapy._private.system_model.connections_and_sockets import _2522

        return self.__parent__._cast(_2522.Socket)

    @property
    def worm_gear_teeth_socket(self: "CastSelf") -> "WormGearTeethSocket":
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
class WormGearTeethSocket(_2540.GearTeethSocket):
    """WormGearTeethSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _WORM_GEAR_TEETH_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_WormGearTeethSocket":
        """Cast to another type.

        Returns:
            _Cast_WormGearTeethSocket
        """
        return _Cast_WormGearTeethSocket(self)
