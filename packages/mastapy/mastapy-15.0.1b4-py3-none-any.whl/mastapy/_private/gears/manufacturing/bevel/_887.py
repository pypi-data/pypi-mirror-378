"""ConicalMeshFlankNURBSMicroGeometryConfig"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.manufacturing.bevel import _886

_CONICAL_MESH_FLANK_NURBS_MICRO_GEOMETRY_CONFIG = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Bevel", "ConicalMeshFlankNURBSMicroGeometryConfig"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="ConicalMeshFlankNURBSMicroGeometryConfig")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConicalMeshFlankNURBSMicroGeometryConfig._Cast_ConicalMeshFlankNURBSMicroGeometryConfig",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalMeshFlankNURBSMicroGeometryConfig",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalMeshFlankNURBSMicroGeometryConfig:
    """Special nested class for casting ConicalMeshFlankNURBSMicroGeometryConfig to subclasses."""

    __parent__: "ConicalMeshFlankNURBSMicroGeometryConfig"

    @property
    def conical_mesh_flank_micro_geometry_config(
        self: "CastSelf",
    ) -> "_886.ConicalMeshFlankMicroGeometryConfig":
        return self.__parent__._cast(_886.ConicalMeshFlankMicroGeometryConfig)

    @property
    def conical_mesh_flank_nurbs_micro_geometry_config(
        self: "CastSelf",
    ) -> "ConicalMeshFlankNURBSMicroGeometryConfig":
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
class ConicalMeshFlankNURBSMicroGeometryConfig(
    _886.ConicalMeshFlankMicroGeometryConfig
):
    """ConicalMeshFlankNURBSMicroGeometryConfig

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_MESH_FLANK_NURBS_MICRO_GEOMETRY_CONFIG

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalMeshFlankNURBSMicroGeometryConfig":
        """Cast to another type.

        Returns:
            _Cast_ConicalMeshFlankNURBSMicroGeometryConfig
        """
        return _Cast_ConicalMeshFlankNURBSMicroGeometryConfig(self)
