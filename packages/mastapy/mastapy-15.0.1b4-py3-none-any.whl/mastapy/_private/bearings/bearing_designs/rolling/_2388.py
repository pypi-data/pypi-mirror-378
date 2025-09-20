"""ThreePointContactBallBearing"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.implicit import overridable
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.bearings.bearing_designs.rolling import _2374

_THREE_POINT_CONTACT_BALL_BEARING = python_net_import(
    "SMT.MastaAPI.Bearings.BearingDesigns.Rolling", "ThreePointContactBallBearing"
)

if TYPE_CHECKING:
    from typing import Any, Tuple, Type, TypeVar, Union

    from mastapy._private.bearings.bearing_designs import _2345, _2346, _2349
    from mastapy._private.bearings.bearing_designs.rolling import _2355, _2380

    Self = TypeVar("Self", bound="ThreePointContactBallBearing")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ThreePointContactBallBearing._Cast_ThreePointContactBallBearing",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ThreePointContactBallBearing",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ThreePointContactBallBearing:
    """Special nested class for casting ThreePointContactBallBearing to subclasses."""

    __parent__: "ThreePointContactBallBearing"

    @property
    def multi_point_contact_ball_bearing(
        self: "CastSelf",
    ) -> "_2374.MultiPointContactBallBearing":
        return self.__parent__._cast(_2374.MultiPointContactBallBearing)

    @property
    def ball_bearing(self: "CastSelf") -> "_2355.BallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2355

        return self.__parent__._cast(_2355.BallBearing)

    @property
    def rolling_bearing(self: "CastSelf") -> "_2380.RollingBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2380

        return self.__parent__._cast(_2380.RollingBearing)

    @property
    def detailed_bearing(self: "CastSelf") -> "_2346.DetailedBearing":
        from mastapy._private.bearings.bearing_designs import _2346

        return self.__parent__._cast(_2346.DetailedBearing)

    @property
    def non_linear_bearing(self: "CastSelf") -> "_2349.NonLinearBearing":
        from mastapy._private.bearings.bearing_designs import _2349

        return self.__parent__._cast(_2349.NonLinearBearing)

    @property
    def bearing_design(self: "CastSelf") -> "_2345.BearingDesign":
        from mastapy._private.bearings.bearing_designs import _2345

        return self.__parent__._cast(_2345.BearingDesign)

    @property
    def three_point_contact_ball_bearing(
        self: "CastSelf",
    ) -> "ThreePointContactBallBearing":
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
class ThreePointContactBallBearing(_2374.MultiPointContactBallBearing):
    """ThreePointContactBallBearing

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _THREE_POINT_CONTACT_BALL_BEARING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def assembly_radial_internal_clearance(
        self: "Self",
    ) -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "AssemblyRadialInternalClearance")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @assembly_radial_internal_clearance.setter
    @exception_bridge
    @enforce_parameter_types
    def assembly_radial_internal_clearance(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "AssemblyRadialInternalClearance", value)

    @property
    @exception_bridge
    def inner_shim_angle(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "InnerShimAngle")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @inner_shim_angle.setter
    @exception_bridge
    @enforce_parameter_types
    def inner_shim_angle(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "InnerShimAngle", value)

    @property
    @exception_bridge
    def inner_shim_width(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "InnerShimWidth")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @inner_shim_width.setter
    @exception_bridge
    @enforce_parameter_types
    def inner_shim_width(
        self: "Self", value: "Union[float, Tuple[float, bool]]"
    ) -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "InnerShimWidth", value)

    @property
    def cast_to(self: "Self") -> "_Cast_ThreePointContactBallBearing":
        """Cast to another type.

        Returns:
            _Cast_ThreePointContactBallBearing
        """
        return _Cast_ThreePointContactBallBearing(self)
