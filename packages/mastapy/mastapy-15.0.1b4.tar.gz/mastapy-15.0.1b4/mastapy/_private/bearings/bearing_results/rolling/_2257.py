"""LoadedSphericalRollerThrustBearingRow"""

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
from mastapy._private.bearings.bearing_results.rolling import _2243

_LOADED_SPHERICAL_ROLLER_THRUST_BEARING_ROW = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling",
    "LoadedSphericalRollerThrustBearingRow",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results.rolling import _2247, _2256

    Self = TypeVar("Self", bound="LoadedSphericalRollerThrustBearingRow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="LoadedSphericalRollerThrustBearingRow._Cast_LoadedSphericalRollerThrustBearingRow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedSphericalRollerThrustBearingRow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedSphericalRollerThrustBearingRow:
    """Special nested class for casting LoadedSphericalRollerThrustBearingRow to subclasses."""

    __parent__: "LoadedSphericalRollerThrustBearingRow"

    @property
    def loaded_roller_bearing_row(self: "CastSelf") -> "_2243.LoadedRollerBearingRow":
        return self.__parent__._cast(_2243.LoadedRollerBearingRow)

    @property
    def loaded_rolling_bearing_row(self: "CastSelf") -> "_2247.LoadedRollingBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2247

        return self.__parent__._cast(_2247.LoadedRollingBearingRow)

    @property
    def loaded_spherical_roller_thrust_bearing_row(
        self: "CastSelf",
    ) -> "LoadedSphericalRollerThrustBearingRow":
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
class LoadedSphericalRollerThrustBearingRow(_2243.LoadedRollerBearingRow):
    """LoadedSphericalRollerThrustBearingRow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_SPHERICAL_ROLLER_THRUST_BEARING_ROW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def loaded_bearing(
        self: "Self",
    ) -> "_2256.LoadedSphericalRollerThrustBearingResults":
        """mastapy.bearings.bearing_results.rolling.LoadedSphericalRollerThrustBearingResults

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "LoadedBearing")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedSphericalRollerThrustBearingRow":
        """Cast to another type.

        Returns:
            _Cast_LoadedSphericalRollerThrustBearingRow
        """
        return _Cast_LoadedSphericalRollerThrustBearingRow(self)
