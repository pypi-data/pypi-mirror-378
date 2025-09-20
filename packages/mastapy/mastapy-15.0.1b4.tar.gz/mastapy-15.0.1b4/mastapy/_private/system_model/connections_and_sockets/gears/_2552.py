"""StraightBevelDiffGearTeethSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.connections_and_sockets.gears import _2530

_STRAIGHT_BEVEL_DIFF_GEAR_TEETH_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears",
    "StraightBevelDiffGearTeethSocket",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import _2522
    from mastapy._private.system_model.connections_and_sockets.gears import (
        _2526,
        _2534,
        _2540,
    )

    Self = TypeVar("Self", bound="StraightBevelDiffGearTeethSocket")
    CastSelf = TypeVar(
        "CastSelf",
        bound="StraightBevelDiffGearTeethSocket._Cast_StraightBevelDiffGearTeethSocket",
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelDiffGearTeethSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelDiffGearTeethSocket:
    """Special nested class for casting StraightBevelDiffGearTeethSocket to subclasses."""

    __parent__: "StraightBevelDiffGearTeethSocket"

    @property
    def bevel_gear_teeth_socket(self: "CastSelf") -> "_2530.BevelGearTeethSocket":
        return self.__parent__._cast(_2530.BevelGearTeethSocket)

    @property
    def agma_gleason_conical_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2526.AGMAGleasonConicalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2526

        return self.__parent__._cast(_2526.AGMAGleasonConicalGearTeethSocket)

    @property
    def conical_gear_teeth_socket(self: "CastSelf") -> "_2534.ConicalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2534

        return self.__parent__._cast(_2534.ConicalGearTeethSocket)

    @property
    def gear_teeth_socket(self: "CastSelf") -> "_2540.GearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2540

        return self.__parent__._cast(_2540.GearTeethSocket)

    @property
    def socket(self: "CastSelf") -> "_2522.Socket":
        from mastapy._private.system_model.connections_and_sockets import _2522

        return self.__parent__._cast(_2522.Socket)

    @property
    def straight_bevel_diff_gear_teeth_socket(
        self: "CastSelf",
    ) -> "StraightBevelDiffGearTeethSocket":
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
class StraightBevelDiffGearTeethSocket(_2530.BevelGearTeethSocket):
    """StraightBevelDiffGearTeethSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_DIFF_GEAR_TEETH_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_StraightBevelDiffGearTeethSocket":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelDiffGearTeethSocket
        """
        return _Cast_StraightBevelDiffGearTeethSocket(self)
