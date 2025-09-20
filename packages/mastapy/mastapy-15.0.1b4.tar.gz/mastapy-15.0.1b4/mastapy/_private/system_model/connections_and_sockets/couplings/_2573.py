"""CouplingSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.connections_and_sockets import _2502

_COUPLING_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Couplings", "CouplingSocket"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import _2522
    from mastapy._private.system_model.connections_and_sockets.couplings import (
        _2569,
        _2571,
        _2575,
        _2577,
        _2579,
        _2580,
    )

    Self = TypeVar("Self", bound="CouplingSocket")
    CastSelf = TypeVar("CastSelf", bound="CouplingSocket._Cast_CouplingSocket")


__docformat__ = "restructuredtext en"
__all__ = ("CouplingSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CouplingSocket:
    """Special nested class for casting CouplingSocket to subclasses."""

    __parent__: "CouplingSocket"

    @property
    def cylindrical_socket(self: "CastSelf") -> "_2502.CylindricalSocket":
        return self.__parent__._cast(_2502.CylindricalSocket)

    @property
    def socket(self: "CastSelf") -> "_2522.Socket":
        from mastapy._private.system_model.connections_and_sockets import _2522

        return self.__parent__._cast(_2522.Socket)

    @property
    def clutch_socket(self: "CastSelf") -> "_2569.ClutchSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2569,
        )

        return self.__parent__._cast(_2569.ClutchSocket)

    @property
    def concept_coupling_socket(self: "CastSelf") -> "_2571.ConceptCouplingSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2571,
        )

        return self.__parent__._cast(_2571.ConceptCouplingSocket)

    @property
    def part_to_part_shear_coupling_socket(
        self: "CastSelf",
    ) -> "_2575.PartToPartShearCouplingSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2575,
        )

        return self.__parent__._cast(_2575.PartToPartShearCouplingSocket)

    @property
    def spring_damper_socket(self: "CastSelf") -> "_2577.SpringDamperSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2577,
        )

        return self.__parent__._cast(_2577.SpringDamperSocket)

    @property
    def torque_converter_pump_socket(
        self: "CastSelf",
    ) -> "_2579.TorqueConverterPumpSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2579,
        )

        return self.__parent__._cast(_2579.TorqueConverterPumpSocket)

    @property
    def torque_converter_turbine_socket(
        self: "CastSelf",
    ) -> "_2580.TorqueConverterTurbineSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2580,
        )

        return self.__parent__._cast(_2580.TorqueConverterTurbineSocket)

    @property
    def coupling_socket(self: "CastSelf") -> "CouplingSocket":
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
class CouplingSocket(_2502.CylindricalSocket):
    """CouplingSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CouplingSocket":
        """Cast to another type.

        Returns:
            _Cast_CouplingSocket
        """
        return _Cast_CouplingSocket(self)
