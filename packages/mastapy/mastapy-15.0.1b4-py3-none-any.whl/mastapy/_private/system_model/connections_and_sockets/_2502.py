"""CylindricalSocket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.connections_and_sockets import _2522

_CYLINDRICAL_SOCKET = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "CylindricalSocket"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import (
        _2492,
        _2493,
        _2500,
        _2505,
        _2506,
        _2508,
        _2509,
        _2510,
        _2511,
        _2512,
        _2514,
        _2515,
        _2516,
        _2519,
        _2520,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings import (
        _2569,
        _2571,
        _2573,
        _2575,
        _2577,
        _2579,
        _2580,
    )
    from mastapy._private.system_model.connections_and_sockets.cycloidal import (
        _2559,
        _2560,
        _2562,
        _2563,
        _2565,
        _2566,
    )
    from mastapy._private.system_model.connections_and_sockets.gears import _2536

    Self = TypeVar("Self", bound="CylindricalSocket")
    CastSelf = TypeVar("CastSelf", bound="CylindricalSocket._Cast_CylindricalSocket")


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalSocket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalSocket:
    """Special nested class for casting CylindricalSocket to subclasses."""

    __parent__: "CylindricalSocket"

    @property
    def socket(self: "CastSelf") -> "_2522.Socket":
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
    def cvt_pulley_socket(self: "CastSelf") -> "_2500.CVTPulleySocket":
        from mastapy._private.system_model.connections_and_sockets import _2500

        return self.__parent__._cast(_2500.CVTPulleySocket)

    @property
    def inner_shaft_socket(self: "CastSelf") -> "_2505.InnerShaftSocket":
        from mastapy._private.system_model.connections_and_sockets import _2505

        return self.__parent__._cast(_2505.InnerShaftSocket)

    @property
    def inner_shaft_socket_base(self: "CastSelf") -> "_2506.InnerShaftSocketBase":
        from mastapy._private.system_model.connections_and_sockets import _2506

        return self.__parent__._cast(_2506.InnerShaftSocketBase)

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
    def mountable_component_socket(
        self: "CastSelf",
    ) -> "_2510.MountableComponentSocket":
        from mastapy._private.system_model.connections_and_sockets import _2510

        return self.__parent__._cast(_2510.MountableComponentSocket)

    @property
    def outer_shaft_socket(self: "CastSelf") -> "_2511.OuterShaftSocket":
        from mastapy._private.system_model.connections_and_sockets import _2511

        return self.__parent__._cast(_2511.OuterShaftSocket)

    @property
    def outer_shaft_socket_base(self: "CastSelf") -> "_2512.OuterShaftSocketBase":
        from mastapy._private.system_model.connections_and_sockets import _2512

        return self.__parent__._cast(_2512.OuterShaftSocketBase)

    @property
    def planetary_socket(self: "CastSelf") -> "_2514.PlanetarySocket":
        from mastapy._private.system_model.connections_and_sockets import _2514

        return self.__parent__._cast(_2514.PlanetarySocket)

    @property
    def planetary_socket_base(self: "CastSelf") -> "_2515.PlanetarySocketBase":
        from mastapy._private.system_model.connections_and_sockets import _2515

        return self.__parent__._cast(_2515.PlanetarySocketBase)

    @property
    def pulley_socket(self: "CastSelf") -> "_2516.PulleySocket":
        from mastapy._private.system_model.connections_and_sockets import _2516

        return self.__parent__._cast(_2516.PulleySocket)

    @property
    def rolling_ring_socket(self: "CastSelf") -> "_2519.RollingRingSocket":
        from mastapy._private.system_model.connections_and_sockets import _2519

        return self.__parent__._cast(_2519.RollingRingSocket)

    @property
    def shaft_socket(self: "CastSelf") -> "_2520.ShaftSocket":
        from mastapy._private.system_model.connections_and_sockets import _2520

        return self.__parent__._cast(_2520.ShaftSocket)

    @property
    def cylindrical_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2536.CylindricalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2536

        return self.__parent__._cast(_2536.CylindricalGearTeethSocket)

    @property
    def cycloidal_disc_axial_left_socket(
        self: "CastSelf",
    ) -> "_2559.CycloidalDiscAxialLeftSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2559,
        )

        return self.__parent__._cast(_2559.CycloidalDiscAxialLeftSocket)

    @property
    def cycloidal_disc_axial_right_socket(
        self: "CastSelf",
    ) -> "_2560.CycloidalDiscAxialRightSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2560,
        )

        return self.__parent__._cast(_2560.CycloidalDiscAxialRightSocket)

    @property
    def cycloidal_disc_inner_socket(
        self: "CastSelf",
    ) -> "_2562.CycloidalDiscInnerSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2562,
        )

        return self.__parent__._cast(_2562.CycloidalDiscInnerSocket)

    @property
    def cycloidal_disc_outer_socket(
        self: "CastSelf",
    ) -> "_2563.CycloidalDiscOuterSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2563,
        )

        return self.__parent__._cast(_2563.CycloidalDiscOuterSocket)

    @property
    def cycloidal_disc_planetary_bearing_socket(
        self: "CastSelf",
    ) -> "_2565.CycloidalDiscPlanetaryBearingSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2565,
        )

        return self.__parent__._cast(_2565.CycloidalDiscPlanetaryBearingSocket)

    @property
    def ring_pins_socket(self: "CastSelf") -> "_2566.RingPinsSocket":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2566,
        )

        return self.__parent__._cast(_2566.RingPinsSocket)

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
    def coupling_socket(self: "CastSelf") -> "_2573.CouplingSocket":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2573,
        )

        return self.__parent__._cast(_2573.CouplingSocket)

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
    def cylindrical_socket(self: "CastSelf") -> "CylindricalSocket":
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
class CylindricalSocket(_2522.Socket):
    """CylindricalSocket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CylindricalSocket":
        """Cast to another type.

        Returns:
            _Cast_CylindricalSocket
        """
        return _Cast_CylindricalSocket(self)
