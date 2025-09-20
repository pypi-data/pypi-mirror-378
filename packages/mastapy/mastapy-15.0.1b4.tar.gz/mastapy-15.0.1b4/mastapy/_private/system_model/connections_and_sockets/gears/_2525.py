"""AGMAGleasonConicalGearMesh"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.connections_and_sockets.gears import _2533

_AGMA_GLEASON_CONICAL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "AGMAGleasonConicalGearMesh"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets import _2498, _2507
    from mastapy._private.system_model.connections_and_sockets.gears import (
        _2527,
        _2529,
        _2539,
        _2541,
        _2549,
        _2551,
        _2553,
        _2557,
    )

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearMesh")
    CastSelf = TypeVar(
        "CastSelf", bound="AGMAGleasonConicalGearMesh._Cast_AGMAGleasonConicalGearMesh"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearMesh",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearMesh:
    """Special nested class for casting AGMAGleasonConicalGearMesh to subclasses."""

    __parent__: "AGMAGleasonConicalGearMesh"

    @property
    def conical_gear_mesh(self: "CastSelf") -> "_2533.ConicalGearMesh":
        return self.__parent__._cast(_2533.ConicalGearMesh)

    @property
    def gear_mesh(self: "CastSelf") -> "_2539.GearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2539

        return self.__parent__._cast(_2539.GearMesh)

    @property
    def inter_mountable_component_connection(
        self: "CastSelf",
    ) -> "_2507.InterMountableComponentConnection":
        from mastapy._private.system_model.connections_and_sockets import _2507

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
    def hypoid_gear_mesh(self: "CastSelf") -> "_2541.HypoidGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2541

        return self.__parent__._cast(_2541.HypoidGearMesh)

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
    def zerol_bevel_gear_mesh(self: "CastSelf") -> "_2557.ZerolBevelGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2557

        return self.__parent__._cast(_2557.ZerolBevelGearMesh)

    @property
    def agma_gleason_conical_gear_mesh(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearMesh":
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
class AGMAGleasonConicalGearMesh(_2533.ConicalGearMesh):
    """AGMAGleasonConicalGearMesh

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_MESH

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearMesh":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearMesh
        """
        return _Cast_AGMAGleasonConicalGearMesh(self)
