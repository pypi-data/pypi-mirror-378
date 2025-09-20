"""InterMountableComponentConnection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.system_model.connections_and_sockets import _2498

_INTER_MOUNTABLE_COMPONENT_CONNECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets",
    "InterMountableComponentConnection",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets import (
        _2494,
        _2499,
        _2518,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings import (
        _2568,
        _2570,
        _2572,
        _2574,
        _2576,
        _2578,
    )
    from mastapy._private.system_model.connections_and_sockets.cycloidal import _2567
    from mastapy._private.system_model.connections_and_sockets.gears import (
        _2525,
        _2527,
        _2529,
        _2531,
        _2533,
        _2535,
        _2537,
        _2539,
        _2541,
        _2544,
        _2545,
        _2546,
        _2549,
        _2551,
        _2553,
        _2555,
        _2557,
    )

    Self = TypeVar("Self", bound="InterMountableComponentConnection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="InterMountableComponentConnection._Cast_InterMountableComponentConnection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("InterMountableComponentConnection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InterMountableComponentConnection:
    """Special nested class for casting InterMountableComponentConnection to subclasses."""

    __parent__: "InterMountableComponentConnection"

    @property
    def connection(self: "CastSelf") -> "_2498.Connection":
        return self.__parent__._cast(_2498.Connection)

    @property
    def design_entity(self: "CastSelf") -> "_2419.DesignEntity":
        from mastapy._private.system_model import _2419

        return self.__parent__._cast(_2419.DesignEntity)

    @property
    def belt_connection(self: "CastSelf") -> "_2494.BeltConnection":
        from mastapy._private.system_model.connections_and_sockets import _2494

        return self.__parent__._cast(_2494.BeltConnection)

    @property
    def cvt_belt_connection(self: "CastSelf") -> "_2499.CVTBeltConnection":
        from mastapy._private.system_model.connections_and_sockets import _2499

        return self.__parent__._cast(_2499.CVTBeltConnection)

    @property
    def rolling_ring_connection(self: "CastSelf") -> "_2518.RollingRingConnection":
        from mastapy._private.system_model.connections_and_sockets import _2518

        return self.__parent__._cast(_2518.RollingRingConnection)

    @property
    def agma_gleason_conical_gear_mesh(
        self: "CastSelf",
    ) -> "_2525.AGMAGleasonConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2525

        return self.__parent__._cast(_2525.AGMAGleasonConicalGearMesh)

    @property
    def bevel_differential_gear_mesh(
        self: "CastSelf",
    ) -> "_2527.BevelDifferentialGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2527

        return self.__parent__._cast(_2527.BevelDifferentialGearMesh)

    @property
    def bevel_gear_mesh(self: "CastSelf") -> "_2529.BevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2529

        return self.__parent__._cast(_2529.BevelGearMesh)

    @property
    def concept_gear_mesh(self: "CastSelf") -> "_2531.ConceptGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2531

        return self.__parent__._cast(_2531.ConceptGearMesh)

    @property
    def conical_gear_mesh(self: "CastSelf") -> "_2533.ConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2533

        return self.__parent__._cast(_2533.ConicalGearMesh)

    @property
    def cylindrical_gear_mesh(self: "CastSelf") -> "_2535.CylindricalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2535

        return self.__parent__._cast(_2535.CylindricalGearMesh)

    @property
    def face_gear_mesh(self: "CastSelf") -> "_2537.FaceGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2537

        return self.__parent__._cast(_2537.FaceGearMesh)

    @property
    def gear_mesh(self: "CastSelf") -> "_2539.GearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2539

        return self.__parent__._cast(_2539.GearMesh)

    @property
    def hypoid_gear_mesh(self: "CastSelf") -> "_2541.HypoidGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2541

        return self.__parent__._cast(_2541.HypoidGearMesh)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_mesh(
        self: "CastSelf",
    ) -> "_2544.KlingelnbergCycloPalloidConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2544

        return self.__parent__._cast(_2544.KlingelnbergCycloPalloidConicalGearMesh)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_mesh(
        self: "CastSelf",
    ) -> "_2545.KlingelnbergCycloPalloidHypoidGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2545

        return self.__parent__._cast(_2545.KlingelnbergCycloPalloidHypoidGearMesh)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_mesh(
        self: "CastSelf",
    ) -> "_2546.KlingelnbergCycloPalloidSpiralBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2546

        return self.__parent__._cast(_2546.KlingelnbergCycloPalloidSpiralBevelGearMesh)

    @property
    def spiral_bevel_gear_mesh(self: "CastSelf") -> "_2549.SpiralBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2549

        return self.__parent__._cast(_2549.SpiralBevelGearMesh)

    @property
    def straight_bevel_diff_gear_mesh(
        self: "CastSelf",
    ) -> "_2551.StraightBevelDiffGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2551

        return self.__parent__._cast(_2551.StraightBevelDiffGearMesh)

    @property
    def straight_bevel_gear_mesh(self: "CastSelf") -> "_2553.StraightBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2553

        return self.__parent__._cast(_2553.StraightBevelGearMesh)

    @property
    def worm_gear_mesh(self: "CastSelf") -> "_2555.WormGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2555

        return self.__parent__._cast(_2555.WormGearMesh)

    @property
    def zerol_bevel_gear_mesh(self: "CastSelf") -> "_2557.ZerolBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2557

        return self.__parent__._cast(_2557.ZerolBevelGearMesh)

    @property
    def ring_pins_to_disc_connection(
        self: "CastSelf",
    ) -> "_2567.RingPinsToDiscConnection":
        from mastapy._private.system_model.connections_and_sockets.cycloidal import (
            _2567,
        )

        return self.__parent__._cast(_2567.RingPinsToDiscConnection)

    @property
    def clutch_connection(self: "CastSelf") -> "_2568.ClutchConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2568,
        )

        return self.__parent__._cast(_2568.ClutchConnection)

    @property
    def concept_coupling_connection(
        self: "CastSelf",
    ) -> "_2570.ConceptCouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2570,
        )

        return self.__parent__._cast(_2570.ConceptCouplingConnection)

    @property
    def coupling_connection(self: "CastSelf") -> "_2572.CouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2572,
        )

        return self.__parent__._cast(_2572.CouplingConnection)

    @property
    def part_to_part_shear_coupling_connection(
        self: "CastSelf",
    ) -> "_2574.PartToPartShearCouplingConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2574,
        )

        return self.__parent__._cast(_2574.PartToPartShearCouplingConnection)

    @property
    def spring_damper_connection(self: "CastSelf") -> "_2576.SpringDamperConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2576,
        )

        return self.__parent__._cast(_2576.SpringDamperConnection)

    @property
    def torque_converter_connection(
        self: "CastSelf",
    ) -> "_2578.TorqueConverterConnection":
        from mastapy._private.system_model.connections_and_sockets.couplings import (
            _2578,
        )

        return self.__parent__._cast(_2578.TorqueConverterConnection)

    @property
    def inter_mountable_component_connection(
        self: "CastSelf",
    ) -> "InterMountableComponentConnection":
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
class InterMountableComponentConnection(_2498.Connection):
    """InterMountableComponentConnection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _INTER_MOUNTABLE_COMPONENT_CONNECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def additional_modal_damping_ratio(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "AdditionalModalDampingRatio")

        if temp is None:
            return 0.0

        return temp

    @additional_modal_damping_ratio.setter
    @exception_bridge
    @enforce_parameter_types
    def additional_modal_damping_ratio(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "AdditionalModalDampingRatio",
            float(value) if value is not None else 0.0,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_InterMountableComponentConnection":
        """Cast to another type.

        Returns:
            _Cast_InterMountableComponentConnection
        """
        return _Cast_InterMountableComponentConnection(self)
