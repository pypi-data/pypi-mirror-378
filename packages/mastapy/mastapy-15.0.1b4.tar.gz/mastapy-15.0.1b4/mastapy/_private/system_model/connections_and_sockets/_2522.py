"""Socket"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_method_call_overload,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

_COMPONENT = python_net_import("SMT.MastaAPI.SystemModel.PartModel", "Component")
_SOCKET = python_net_import("SMT.MastaAPI.SystemModel.ConnectionsAndSockets", "Socket")

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.connections_and_sockets import (
        _2492,
        _2493,
        _2498,
        _2500,
        _2502,
        _2504,
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
    from mastapy._private.system_model.connections_and_sockets.gears import (
        _2526,
        _2528,
        _2530,
        _2532,
        _2534,
        _2536,
        _2538,
        _2540,
        _2542,
        _2543,
        _2547,
        _2548,
        _2550,
        _2552,
        _2554,
        _2556,
        _2558,
    )
    from mastapy._private.system_model.part_model import _2675, _2676

    Self = TypeVar("Self", bound="Socket")
    CastSelf = TypeVar("CastSelf", bound="Socket._Cast_Socket")


__docformat__ = "restructuredtext en"
__all__ = ("Socket",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Socket:
    """Special nested class for casting Socket to subclasses."""

    __parent__: "Socket"

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
    def cylindrical_socket(self: "CastSelf") -> "_2502.CylindricalSocket":
        from mastapy._private.system_model.connections_and_sockets import _2502

        return self.__parent__._cast(_2502.CylindricalSocket)

    @property
    def electric_machine_stator_socket(
        self: "CastSelf",
    ) -> "_2504.ElectricMachineStatorSocket":
        from mastapy._private.system_model.connections_and_sockets import _2504

        return self.__parent__._cast(_2504.ElectricMachineStatorSocket)

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
    def agma_gleason_conical_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2526.AGMAGleasonConicalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2526

        return self.__parent__._cast(_2526.AGMAGleasonConicalGearTeethSocket)

    @property
    def bevel_differential_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2528.BevelDifferentialGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2528

        return self.__parent__._cast(_2528.BevelDifferentialGearTeethSocket)

    @property
    def bevel_gear_teeth_socket(self: "CastSelf") -> "_2530.BevelGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2530

        return self.__parent__._cast(_2530.BevelGearTeethSocket)

    @property
    def concept_gear_teeth_socket(self: "CastSelf") -> "_2532.ConceptGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2532

        return self.__parent__._cast(_2532.ConceptGearTeethSocket)

    @property
    def conical_gear_teeth_socket(self: "CastSelf") -> "_2534.ConicalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2534

        return self.__parent__._cast(_2534.ConicalGearTeethSocket)

    @property
    def cylindrical_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2536.CylindricalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2536

        return self.__parent__._cast(_2536.CylindricalGearTeethSocket)

    @property
    def face_gear_teeth_socket(self: "CastSelf") -> "_2538.FaceGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2538

        return self.__parent__._cast(_2538.FaceGearTeethSocket)

    @property
    def gear_teeth_socket(self: "CastSelf") -> "_2540.GearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2540

        return self.__parent__._cast(_2540.GearTeethSocket)

    @property
    def hypoid_gear_teeth_socket(self: "CastSelf") -> "_2542.HypoidGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2542

        return self.__parent__._cast(_2542.HypoidGearTeethSocket)

    @property
    def klingelnberg_conical_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2543.KlingelnbergConicalGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2543

        return self.__parent__._cast(_2543.KlingelnbergConicalGearTeethSocket)

    @property
    def klingelnberg_hypoid_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2547.KlingelnbergHypoidGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2547

        return self.__parent__._cast(_2547.KlingelnbergHypoidGearTeethSocket)

    @property
    def klingelnberg_spiral_bevel_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2548.KlingelnbergSpiralBevelGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2548

        return self.__parent__._cast(_2548.KlingelnbergSpiralBevelGearTeethSocket)

    @property
    def spiral_bevel_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2550.SpiralBevelGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2550

        return self.__parent__._cast(_2550.SpiralBevelGearTeethSocket)

    @property
    def straight_bevel_diff_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2552.StraightBevelDiffGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2552

        return self.__parent__._cast(_2552.StraightBevelDiffGearTeethSocket)

    @property
    def straight_bevel_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2554.StraightBevelGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2554

        return self.__parent__._cast(_2554.StraightBevelGearTeethSocket)

    @property
    def worm_gear_teeth_socket(self: "CastSelf") -> "_2556.WormGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2556

        return self.__parent__._cast(_2556.WormGearTeethSocket)

    @property
    def zerol_bevel_gear_teeth_socket(
        self: "CastSelf",
    ) -> "_2558.ZerolBevelGearTeethSocket":
        from mastapy._private.system_model.connections_and_sockets.gears import _2558

        return self.__parent__._cast(_2558.ZerolBevelGearTeethSocket)

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
    def socket(self: "CastSelf") -> "Socket":
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
class Socket(_0.APIBase):
    """Socket

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SOCKET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def connected_components(self: "Self") -> "List[_2675.Component]":
        """List[mastapy.system_model.part_model.Component]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectedComponents")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connections(self: "Self") -> "List[_2498.Connection]":
        """List[mastapy.system_model.connections_and_sockets.Connection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Connections")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def owner(self: "Self") -> "_2675.Component":
        """mastapy.system_model.part_model.Component

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Owner")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @exception_bridge
    @enforce_parameter_types
    def connect_to(
        self: "Self", component: "_2675.Component"
    ) -> "_2676.ComponentsConnectedResult":
        """mastapy.system_model.part_model.ComponentsConnectedResult

        Args:
            component (mastapy.system_model.part_model.Component)
        """
        method_result = pythonnet_method_call_overload(
            self.wrapped,
            "ConnectTo",
            [_COMPONENT],
            component.wrapped if component else None,
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def connect_to_socket(
        self: "Self", socket: "Socket"
    ) -> "_2676.ComponentsConnectedResult":
        """mastapy.system_model.part_model.ComponentsConnectedResult

        Args:
            socket (mastapy.system_model.connections_and_sockets.Socket)
        """
        method_result = pythonnet_method_call_overload(
            self.wrapped, "ConnectTo", [_SOCKET], socket.wrapped if socket else None
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def connection_to(self: "Self", socket: "Socket") -> "_2498.Connection":
        """mastapy.system_model.connections_and_sockets.Connection

        Args:
            socket (mastapy.system_model.connections_and_sockets.Socket)
        """
        method_result = pythonnet_method_call(
            self.wrapped, "ConnectionTo", socket.wrapped if socket else None
        )
        type_ = method_result.GetType()
        return (
            constructor.new(type_.Namespace, type_.Name)(method_result)
            if method_result is not None
            else None
        )

    @exception_bridge
    @enforce_parameter_types
    def get_possible_sockets_to_connect_to(
        self: "Self", component_to_connect_to: "_2675.Component"
    ) -> "List[Socket]":
        """List[mastapy.system_model.connections_and_sockets.Socket]

        Args:
            component_to_connect_to (mastapy.system_model.part_model.Component)
        """
        return conversion.pn_to_mp_objects_in_list(
            pythonnet_method_call(
                self.wrapped,
                "GetPossibleSocketsToConnectTo",
                component_to_connect_to.wrapped if component_to_connect_to else None,
            )
        )

    @property
    def cast_to(self: "Self") -> "_Cast_Socket":
        """Cast to another type.

        Returns:
            _Cast_Socket
        """
        return _Cast_Socket(self)
