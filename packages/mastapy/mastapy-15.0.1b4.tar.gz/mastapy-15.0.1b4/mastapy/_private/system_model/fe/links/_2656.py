"""PlanetaryConnectorMultiNodeFELink"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.fe.links import _2657

_PLANETARY_CONNECTOR_MULTI_NODE_FE_LINK = python_net_import(
    "SMT.MastaAPI.SystemModel.FE.Links", "PlanetaryConnectorMultiNodeFELink"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.fe.links import _2648, _2655

    Self = TypeVar("Self", bound="PlanetaryConnectorMultiNodeFELink")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PlanetaryConnectorMultiNodeFELink._Cast_PlanetaryConnectorMultiNodeFELink",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PlanetaryConnectorMultiNodeFELink",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PlanetaryConnectorMultiNodeFELink:
    """Special nested class for casting PlanetaryConnectorMultiNodeFELink to subclasses."""

    __parent__: "PlanetaryConnectorMultiNodeFELink"

    @property
    def planet_based_fe_link(self: "CastSelf") -> "_2657.PlanetBasedFELink":
        return self.__parent__._cast(_2657.PlanetBasedFELink)

    @property
    def multi_node_fe_link(self: "CastSelf") -> "_2655.MultiNodeFELink":
        from mastapy._private.system_model.fe.links import _2655

        return self.__parent__._cast(_2655.MultiNodeFELink)

    @property
    def fe_link(self: "CastSelf") -> "_2648.FELink":
        from mastapy._private.system_model.fe.links import _2648

        return self.__parent__._cast(_2648.FELink)

    @property
    def planetary_connector_multi_node_fe_link(
        self: "CastSelf",
    ) -> "PlanetaryConnectorMultiNodeFELink":
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
class PlanetaryConnectorMultiNodeFELink(_2657.PlanetBasedFELink):
    """PlanetaryConnectorMultiNodeFELink

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PLANETARY_CONNECTOR_MULTI_NODE_FE_LINK

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_PlanetaryConnectorMultiNodeFELink":
        """Cast to another type.

        Returns:
            _Cast_PlanetaryConnectorMultiNodeFELink
        """
        return _Cast_PlanetaryConnectorMultiNodeFELink(self)
