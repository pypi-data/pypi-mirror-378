"""MultiNodeFELink"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.fe.links import _2648

_MULTI_NODE_FE_LINK = python_net_import(
    "SMT.MastaAPI.SystemModel.FE.Links", "MultiNodeFELink"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.fe.links import (
        _2649,
        _2651,
        _2652,
        _2653,
        _2654,
        _2656,
        _2657,
        _2658,
        _2659,
        _2660,
        _2661,
    )

    Self = TypeVar("Self", bound="MultiNodeFELink")
    CastSelf = TypeVar("CastSelf", bound="MultiNodeFELink._Cast_MultiNodeFELink")


__docformat__ = "restructuredtext en"
__all__ = ("MultiNodeFELink",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MultiNodeFELink:
    """Special nested class for casting MultiNodeFELink to subclasses."""

    __parent__: "MultiNodeFELink"

    @property
    def fe_link(self: "CastSelf") -> "_2648.FELink":
        return self.__parent__._cast(_2648.FELink)

    @property
    def electric_machine_stator_fe_link(
        self: "CastSelf",
    ) -> "_2649.ElectricMachineStatorFELink":
        from mastapy._private.system_model.fe.links import _2649

        return self.__parent__._cast(_2649.ElectricMachineStatorFELink)

    @property
    def gear_mesh_fe_link(self: "CastSelf") -> "_2651.GearMeshFELink":
        from mastapy._private.system_model.fe.links import _2651

        return self.__parent__._cast(_2651.GearMeshFELink)

    @property
    def gear_with_duplicated_meshes_fe_link(
        self: "CastSelf",
    ) -> "_2652.GearWithDuplicatedMeshesFELink":
        from mastapy._private.system_model.fe.links import _2652

        return self.__parent__._cast(_2652.GearWithDuplicatedMeshesFELink)

    @property
    def multi_angle_connection_fe_link(
        self: "CastSelf",
    ) -> "_2653.MultiAngleConnectionFELink":
        from mastapy._private.system_model.fe.links import _2653

        return self.__parent__._cast(_2653.MultiAngleConnectionFELink)

    @property
    def multi_node_connector_fe_link(
        self: "CastSelf",
    ) -> "_2654.MultiNodeConnectorFELink":
        from mastapy._private.system_model.fe.links import _2654

        return self.__parent__._cast(_2654.MultiNodeConnectorFELink)

    @property
    def planetary_connector_multi_node_fe_link(
        self: "CastSelf",
    ) -> "_2656.PlanetaryConnectorMultiNodeFELink":
        from mastapy._private.system_model.fe.links import _2656

        return self.__parent__._cast(_2656.PlanetaryConnectorMultiNodeFELink)

    @property
    def planet_based_fe_link(self: "CastSelf") -> "_2657.PlanetBasedFELink":
        from mastapy._private.system_model.fe.links import _2657

        return self.__parent__._cast(_2657.PlanetBasedFELink)

    @property
    def planet_carrier_fe_link(self: "CastSelf") -> "_2658.PlanetCarrierFELink":
        from mastapy._private.system_model.fe.links import _2658

        return self.__parent__._cast(_2658.PlanetCarrierFELink)

    @property
    def point_load_fe_link(self: "CastSelf") -> "_2659.PointLoadFELink":
        from mastapy._private.system_model.fe.links import _2659

        return self.__parent__._cast(_2659.PointLoadFELink)

    @property
    def rolling_ring_connection_fe_link(
        self: "CastSelf",
    ) -> "_2660.RollingRingConnectionFELink":
        from mastapy._private.system_model.fe.links import _2660

        return self.__parent__._cast(_2660.RollingRingConnectionFELink)

    @property
    def shaft_hub_connection_fe_link(
        self: "CastSelf",
    ) -> "_2661.ShaftHubConnectionFELink":
        from mastapy._private.system_model.fe.links import _2661

        return self.__parent__._cast(_2661.ShaftHubConnectionFELink)

    @property
    def multi_node_fe_link(self: "CastSelf") -> "MultiNodeFELink":
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
class MultiNodeFELink(_2648.FELink):
    """MultiNodeFELink

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MULTI_NODE_FE_LINK

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_MultiNodeFELink":
        """Cast to another type.

        Returns:
            _Cast_MultiNodeFELink
        """
        return _Cast_MultiNodeFELink(self)
