"""ISO63362019MeshSingleFlankRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.gears.rating.cylindrical.iso6336 import _606

_ISO63362019_MESH_SINGLE_FLANK_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.Cylindrical.ISO6336", "ISO63362019MeshSingleFlankRating"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.rating import _458
    from mastapy._private.gears.rating.cylindrical import _559
    from mastapy._private.gears.rating.cylindrical.iso6336 import _610, _612

    Self = TypeVar("Self", bound="ISO63362019MeshSingleFlankRating")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ISO63362019MeshSingleFlankRating._Cast_ISO63362019MeshSingleFlankRating",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ISO63362019MeshSingleFlankRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ISO63362019MeshSingleFlankRating:
    """Special nested class for casting ISO63362019MeshSingleFlankRating to subclasses."""

    __parent__: "ISO63362019MeshSingleFlankRating"

    @property
    def iso63362006_mesh_single_flank_rating(
        self: "CastSelf",
    ) -> "_606.ISO63362006MeshSingleFlankRating":
        return self.__parent__._cast(_606.ISO63362006MeshSingleFlankRating)

    @property
    def iso6336_abstract_metal_mesh_single_flank_rating(
        self: "CastSelf",
    ) -> "_612.ISO6336AbstractMetalMeshSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical.iso6336 import _612

        return self.__parent__._cast(_612.ISO6336AbstractMetalMeshSingleFlankRating)

    @property
    def iso6336_abstract_mesh_single_flank_rating(
        self: "CastSelf",
    ) -> "_610.ISO6336AbstractMeshSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical.iso6336 import _610

        return self.__parent__._cast(_610.ISO6336AbstractMeshSingleFlankRating)

    @property
    def cylindrical_mesh_single_flank_rating(
        self: "CastSelf",
    ) -> "_559.CylindricalMeshSingleFlankRating":
        from mastapy._private.gears.rating.cylindrical import _559

        return self.__parent__._cast(_559.CylindricalMeshSingleFlankRating)

    @property
    def mesh_single_flank_rating(self: "CastSelf") -> "_458.MeshSingleFlankRating":
        from mastapy._private.gears.rating import _458

        return self.__parent__._cast(_458.MeshSingleFlankRating)

    @property
    def iso63362019_mesh_single_flank_rating(
        self: "CastSelf",
    ) -> "ISO63362019MeshSingleFlankRating":
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
class ISO63362019MeshSingleFlankRating(_606.ISO63362006MeshSingleFlankRating):
    """ISO63362019MeshSingleFlankRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ISO63362019_MESH_SINGLE_FLANK_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def micro_geometry_factor(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MicroGeometryFactor")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def rating_standard_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RatingStandardName")

        if temp is None:
            return ""

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_ISO63362019MeshSingleFlankRating":
        """Cast to another type.

        Returns:
            _Cast_ISO63362019MeshSingleFlankRating
        """
        return _Cast_ISO63362019MeshSingleFlankRating(self)
