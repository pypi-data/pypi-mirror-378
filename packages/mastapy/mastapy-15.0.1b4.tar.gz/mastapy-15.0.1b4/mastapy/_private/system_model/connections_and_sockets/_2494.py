"""BeltConnection"""

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
from mastapy._private.system_model.connections_and_sockets import _2507

_BELT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "BeltConnection"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets import _2498, _2499

    Self = TypeVar("Self", bound="BeltConnection")
    CastSelf = TypeVar("CastSelf", bound="BeltConnection._Cast_BeltConnection")


__docformat__ = "restructuredtext en"
__all__ = ("BeltConnection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BeltConnection:
    """Special nested class for casting BeltConnection to subclasses."""

    __parent__: "BeltConnection"

    @property
    def inter_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2507.InterMountableComponentConnection":
        return self.__parent__._cast(_2507.InterMountableComponentConnection)

    @property
    def connection(self: "CastSelf") -> "_2498.Connection":
        from mastapy._private.system_model.connections_and_sockets import _2498

        return self.__parent__._cast(_2498.Connection)

    @property
    def design_entity(self: "CastSelf") -> "_2419.DesignEntity":
        from mastapy._private.system_model import _2419

        return self.__parent__._cast(_2419.DesignEntity)

    @property
    def cvt_belt_connection(self: "CastSelf") -> "_2499.CVTBeltConnection":
        from mastapy._private.system_model.connections_and_sockets import _2499

        return self.__parent__._cast(_2499.CVTBeltConnection)

    @property
    def belt_connection(self: "CastSelf") -> "BeltConnection":
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
class BeltConnection(_2507.InterMountableComponentConnection):
    """BeltConnection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BELT_CONNECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def stiffness_of_strand(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StiffnessOfStrand")

        if temp is None:
            return 0.0

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_BeltConnection":
        """Cast to another type.

        Returns:
            _Cast_BeltConnection
        """
        return _Cast_BeltConnection(self)
