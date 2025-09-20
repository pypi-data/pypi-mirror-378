"""MeshedResultPlane"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.part_model.acoustics import _2883, _2887

_MESHED_RESULT_PLANE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Acoustics", "MeshedResultPlane"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.part_model.acoustics import _2884

    Self = TypeVar("Self", bound="MeshedResultPlane")
    CastSelf = TypeVar("CastSelf", bound="MeshedResultPlane._Cast_MeshedResultPlane")


__docformat__ = "restructuredtext en"
__all__ = ("MeshedResultPlane",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MeshedResultPlane:
    """Special nested class for casting MeshedResultPlane to subclasses."""

    __parent__: "MeshedResultPlane"

    @property
    def meshed_result_surface(self: "CastSelf") -> "_2883.MeshedResultSurface":
        return self.__parent__._cast(_2883.MeshedResultSurface)

    @property
    def meshed_result_surface_base(self: "CastSelf") -> "_2884.MeshedResultSurfaceBase":
        from mastapy._private.system_model.part_model.acoustics import _2884

        return self.__parent__._cast(_2884.MeshedResultSurfaceBase)

    @property
    def meshed_result_plane(self: "CastSelf") -> "MeshedResultPlane":
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
class MeshedResultPlane(_2883.MeshedResultSurface[_2887.ResultPlaneOptions]):
    """MeshedResultPlane

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MESHED_RESULT_PLANE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_MeshedResultPlane":
        """Cast to another type.

        Returns:
            _Cast_MeshedResultPlane
        """
        return _Cast_MeshedResultPlane(self)
