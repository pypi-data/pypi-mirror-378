"""AxialThrustCylindricalRollerBearing"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.bearings.bearing_designs.rolling import _2376

_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING = python_net_import(
    "SMT.MastaAPI.Bearings.BearingDesigns.Rolling",
    "AxialThrustCylindricalRollerBearing",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_designs import _2345, _2346, _2349
    from mastapy._private.bearings.bearing_designs.rolling import _2354, _2377, _2380

    Self = TypeVar("Self", bound="AxialThrustCylindricalRollerBearing")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AxialThrustCylindricalRollerBearing._Cast_AxialThrustCylindricalRollerBearing",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AxialThrustCylindricalRollerBearing",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AxialThrustCylindricalRollerBearing:
    """Special nested class for casting AxialThrustCylindricalRollerBearing to subclasses."""

    __parent__: "AxialThrustCylindricalRollerBearing"

    @property
    def non_barrel_roller_bearing(self: "CastSelf") -> "_2376.NonBarrelRollerBearing":
        return self.__parent__._cast(_2376.NonBarrelRollerBearing)

    @property
    def roller_bearing(self: "CastSelf") -> "_2377.RollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2377

        return self.__parent__._cast(_2377.RollerBearing)

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
    def axial_thrust_needle_roller_bearing(
        self: "CastSelf",
    ) -> "_2354.AxialThrustNeedleRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2354

        return self.__parent__._cast(_2354.AxialThrustNeedleRollerBearing)

    @property
    def axial_thrust_cylindrical_roller_bearing(
        self: "CastSelf",
    ) -> "AxialThrustCylindricalRollerBearing":
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
class AxialThrustCylindricalRollerBearing(_2376.NonBarrelRollerBearing):
    """AxialThrustCylindricalRollerBearing

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_AxialThrustCylindricalRollerBearing":
        """Cast to another type.

        Returns:
            _Cast_AxialThrustCylindricalRollerBearing
        """
        return _Cast_AxialThrustCylindricalRollerBearing(self)
