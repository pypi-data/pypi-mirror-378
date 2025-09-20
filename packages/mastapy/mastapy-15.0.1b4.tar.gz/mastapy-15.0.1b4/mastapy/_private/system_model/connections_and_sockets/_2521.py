"""ShaftToMountableComponentConnection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.connections_and_sockets import _2491

_SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets",
    "ShaftToMountableComponentConnection",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets import (
        _2495,
        _2498,
        _2513,
    )
    from mastapy._private.system_model.connections_and_sockets.cycloidal import _2561

    Self = TypeVar("Self", bound="ShaftToMountableComponentConnection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ShaftToMountableComponentConnection._Cast_ShaftToMountableComponentConnection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ShaftToMountableComponentConnection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ShaftToMountableComponentConnection:
    """Special nested class for casting ShaftToMountableComponentConnection to subclasses."""

    __parent__: "ShaftToMountableComponentConnection"

    @property
    def abstract_shaft_to_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2491.AbstractShaftToMountableComponentConnection":
        return self.__parent__._cast(_2491.AbstractShaftToMountableComponentConnection)

    @property
    def connection(self: "CastSelf") -> "_2498.Connection":
        from mastapy._private.system_model.connections_and_sockets import _2498

        return self.__parent__._cast(_2498.Connection)

    @property
    def design_entity(self: "CastSelf") -> "_2419.DesignEntity":
        from mastapy._private.system_model import _2419

        return self.__parent__._cast(_2419.DesignEntity)

    @property
    def coaxial_connection(self: "CastSelf") -> "_2495.CoaxialConnection":
        from mastapy._private.system_model.connections_and_sockets import _2495

        return self.__parent__._cast(_2495.CoaxialConnection)

    @property
    def planetary_connection(self: "CastSelf") -> "_2513.PlanetaryConnection":
        from mastapy._private.system_model.connections_and_sockets import _2513

        return self.__parent__._cast(_2513.PlanetaryConnection)

    @property
    def cycloidal_disc_central_bearing_connection(
        self: "CastSelf",
    ) -> "_2561.CycloidalDiscCentralBearingConnection":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2561,
        )

        return self.__parent__._cast(_2561.CycloidalDiscCentralBearingConnection)

    @property
    def shaft_to_mountable_component_connection(
        self: "CastSelf",
    ) -> "ShaftToMountableComponentConnection":
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
class ShaftToMountableComponentConnection(
    _2491.AbstractShaftToMountableComponentConnection
):
    """ShaftToMountableComponentConnection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SHAFT_TO_MOUNTABLE_COMPONENT_CONNECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ShaftToMountableComponentConnection":
        """Cast to another type.

        Returns:
            _Cast_ShaftToMountableComponentConnection
        """
        return _Cast_ShaftToMountableComponentConnection(self)
