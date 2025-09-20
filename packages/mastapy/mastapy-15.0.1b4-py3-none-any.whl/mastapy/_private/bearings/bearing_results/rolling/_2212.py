"""LoadedBallBearingDutyCycle"""

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
from mastapy._private.bearings.bearing_results import _2170
from mastapy._private.bearings.bearing_results.rolling import _2215

_LOADED_BALL_BEARING_DUTY_CYCLE = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling", "LoadedBallBearingDutyCycle"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results import _2159, _2167
    from mastapy._private.utility.property import _2047

    Self = TypeVar("Self", bound="LoadedBallBearingDutyCycle")
    CastSelf = TypeVar(
        "CastSelf", bound="LoadedBallBearingDutyCycle._Cast_LoadedBallBearingDutyCycle"
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedBallBearingDutyCycle",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedBallBearingDutyCycle:
    """Special nested class for casting LoadedBallBearingDutyCycle to subclasses."""

    __parent__: "LoadedBallBearingDutyCycle"

    @property
    def loaded_rolling_bearing_duty_cycle(
        self: "CastSelf",
    ) -> "_2170.LoadedRollingBearingDutyCycle":
        return self.__parent__._cast(_2170.LoadedRollingBearingDutyCycle)

    @property
    def loaded_non_linear_bearing_duty_cycle_results(
        self: "CastSelf",
    ) -> "_2167.LoadedNonLinearBearingDutyCycleResults":
        from mastapy._private.bearings.bearing_results import _2167

        return self.__parent__._cast(_2167.LoadedNonLinearBearingDutyCycleResults)

    @property
    def loaded_bearing_duty_cycle(self: "CastSelf") -> "_2159.LoadedBearingDutyCycle":
        from mastapy._private.bearings.bearing_results import _2159

        return self.__parent__._cast(_2159.LoadedBearingDutyCycle)

    @property
    def loaded_ball_bearing_duty_cycle(
        self: "CastSelf",
    ) -> "LoadedBallBearingDutyCycle":
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
class LoadedBallBearingDutyCycle(_2170.LoadedRollingBearingDutyCycle):
    """LoadedBallBearingDutyCycle

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_BALL_BEARING_DUTY_CYCLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def track_truncation_safety_factor(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TrackTruncationSafetyFactor")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def track_truncation_inner_summary(
        self: "Self",
    ) -> "_2047.DutyCyclePropertySummaryPercentage[_2215.LoadedBallBearingResults]":
        """mastapy.utility.property.DutyCyclePropertySummaryPercentage[mastapy.bearings.bearing_results.rolling.LoadedBallBearingResults]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TrackTruncationInnerSummary")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)[
            _2215.LoadedBallBearingResults
        ](temp)

    @property
    @exception_bridge
    def track_truncation_outer_summary(
        self: "Self",
    ) -> "_2047.DutyCyclePropertySummaryPercentage[_2215.LoadedBallBearingResults]":
        """mastapy.utility.property.DutyCyclePropertySummaryPercentage[mastapy.bearings.bearing_results.rolling.LoadedBallBearingResults]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TrackTruncationOuterSummary")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)[
            _2215.LoadedBallBearingResults
        ](temp)

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedBallBearingDutyCycle":
        """Cast to another type.

        Returns:
            _Cast_LoadedBallBearingDutyCycle
        """
        return _Cast_LoadedBallBearingDutyCycle(self)
