"""StraightBevelGearMesh"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.connections_and_sockets.gears import _2529

_STRAIGHT_BEVEL_GEAR_MESH = python_net_import(
    "SMT.MastaAPI.SystemModel.ConnectionsAndSockets.Gears", "StraightBevelGearMesh"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.gear_designs.straight_bevel import _1066
    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets import _2498, _2507
    from mastapy._private.system_model.connections_and_sockets.gears import (
        _2525,
        _2533,
        _2539,
    )

    Self = TypeVar("Self", bound="StraightBevelGearMesh")
    CastSelf = TypeVar(
        "CastSelf", bound="StraightBevelGearMesh._Cast_StraightBevelGearMesh"
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelGearMesh",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelGearMesh:
    """Special nested class for casting StraightBevelGearMesh to subclasses."""

    __parent__: "StraightBevelGearMesh"

    @property
    def bevel_gear_mesh(self: "CastSelf") -> "_2529.BevelGearMesh":
        return self.__parent__._cast(_2529.BevelGearMesh)

    @property
    def agma_gleason_conical_gear_mesh(
        self: "CastSelf",
    ) -> "_2525.AGMAGleasonConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2525

        return self.__parent__._cast(_2525.AGMAGleasonConicalGearMesh)

    @property
    def conical_gear_mesh(self: "CastSelf") -> "_2533.ConicalGearMesh":
        from mastapy._private.system_model.connections_and_sockets.gears import _2533

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
    def straight_bevel_gear_mesh(self: "CastSelf") -> "StraightBevelGearMesh":
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
class StraightBevelGearMesh(_2529.BevelGearMesh):
    """StraightBevelGearMesh

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_GEAR_MESH

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def bevel_gear_mesh_design(self: "Self") -> "_1066.StraightBevelGearMeshDesign":
        """mastapy.gears.gear_designs.straight_bevel.StraightBevelGearMeshDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BevelGearMeshDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def straight_bevel_gear_mesh_design(
        self: "Self",
    ) -> "_1066.StraightBevelGearMeshDesign":
        """mastapy.gears.gear_designs.straight_bevel.StraightBevelGearMeshDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelGearMeshDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_StraightBevelGearMesh":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelGearMesh
        """
        return _Cast_StraightBevelGearMesh(self)
