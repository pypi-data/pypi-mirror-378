"""LoadedAngularContactThrustBallBearingRow"""

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
from mastapy._private.bearings.bearing_results.rolling import _2197

_LOADED_ANGULAR_CONTACT_THRUST_BALL_BEARING_ROW = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling",
    "LoadedAngularContactThrustBallBearingRow",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results.rolling import _2199, _2216, _2247

    Self = TypeVar("Self", bound="LoadedAngularContactThrustBallBearingRow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="LoadedAngularContactThrustBallBearingRow._Cast_LoadedAngularContactThrustBallBearingRow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedAngularContactThrustBallBearingRow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedAngularContactThrustBallBearingRow:
    """Special nested class for casting LoadedAngularContactThrustBallBearingRow to subclasses."""

    __parent__: "LoadedAngularContactThrustBallBearingRow"

    @property
    def loaded_angular_contact_ball_bearing_row(
        self: "CastSelf",
    ) -> "_2197.LoadedAngularContactBallBearingRow":
        return self.__parent__._cast(_2197.LoadedAngularContactBallBearingRow)

    @property
    def loaded_ball_bearing_row(self: "CastSelf") -> "_2216.LoadedBallBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2216

        return self.__parent__._cast(_2216.LoadedBallBearingRow)

    @property
    def loaded_rolling_bearing_row(self: "CastSelf") -> "_2247.LoadedRollingBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2247

        return self.__parent__._cast(_2247.LoadedRollingBearingRow)

    @property
    def loaded_angular_contact_thrust_ball_bearing_row(
        self: "CastSelf",
    ) -> "LoadedAngularContactThrustBallBearingRow":
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
class LoadedAngularContactThrustBallBearingRow(
    _2197.LoadedAngularContactBallBearingRow
):
    """LoadedAngularContactThrustBallBearingRow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_ANGULAR_CONTACT_THRUST_BALL_BEARING_ROW

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
    ) -> "_2199.LoadedAngularContactThrustBallBearingResults":
        """mastapy.bearings.bearing_results.rolling.LoadedAngularContactThrustBallBearingResults

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "LoadedBearing")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedAngularContactThrustBallBearingRow":
        """Cast to another type.

        Returns:
            _Cast_LoadedAngularContactThrustBallBearingRow
        """
        return _Cast_LoadedAngularContactThrustBallBearingRow(self)
