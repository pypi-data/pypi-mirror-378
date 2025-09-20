"""DutyCycleResultsForSingleBearing"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)

_DUTY_CYCLE_RESULTS_FOR_SINGLE_BEARING = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ParametricStudyTools",
    "DutyCycleResultsForSingleBearing",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results import _2159

    Self = TypeVar("Self", bound="DutyCycleResultsForSingleBearing")
    CastSelf = TypeVar(
        "CastSelf",
        bound="DutyCycleResultsForSingleBearing._Cast_DutyCycleResultsForSingleBearing",
    )


__docformat__ = "restructuredtext en"
__all__ = ("DutyCycleResultsForSingleBearing",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_DutyCycleResultsForSingleBearing:
    """Special nested class for casting DutyCycleResultsForSingleBearing to subclasses."""

    __parent__: "DutyCycleResultsForSingleBearing"

    @property
    def duty_cycle_results_for_single_bearing(
        self: "CastSelf",
    ) -> "DutyCycleResultsForSingleBearing":
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
class DutyCycleResultsForSingleBearing(_0.APIBase):
    """DutyCycleResultsForSingleBearing

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _DUTY_CYCLE_RESULTS_FOR_SINGLE_BEARING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def duty_cycle_results(self: "Self") -> "_2159.LoadedBearingDutyCycle":
        """mastapy.bearings.bearing_results.LoadedBearingDutyCycle

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DutyCycleResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_DutyCycleResultsForSingleBearing":
        """Cast to another type.

        Returns:
            _Cast_DutyCycleResultsForSingleBearing
        """
        return _Cast_DutyCycleResultsForSingleBearing(self)
