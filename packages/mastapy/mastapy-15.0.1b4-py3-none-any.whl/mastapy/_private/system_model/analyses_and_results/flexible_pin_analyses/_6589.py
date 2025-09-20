"""FlexiblePinAnalysisGearAndBearingRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses import (
    _6586,
)

_FLEXIBLE_PIN_ANALYSIS_GEAR_AND_BEARING_RATING = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.FlexiblePinAnalyses",
    "FlexiblePinAnalysisGearAndBearingRating",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses import (
        _6585,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections.compound import (
        _3107,
        _3148,
    )

    Self = TypeVar("Self", bound="FlexiblePinAnalysisGearAndBearingRating")
    CastSelf = TypeVar(
        "CastSelf",
        bound="FlexiblePinAnalysisGearAndBearingRating._Cast_FlexiblePinAnalysisGearAndBearingRating",
    )


__docformat__ = "restructuredtext en"
__all__ = ("FlexiblePinAnalysisGearAndBearingRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_FlexiblePinAnalysisGearAndBearingRating:
    """Special nested class for casting FlexiblePinAnalysisGearAndBearingRating to subclasses."""

    __parent__: "FlexiblePinAnalysisGearAndBearingRating"

    @property
    def flexible_pin_analysis(self: "CastSelf") -> "_6586.FlexiblePinAnalysis":
        return self.__parent__._cast(_6586.FlexiblePinAnalysis)

    @property
    def combination_analysis(self: "CastSelf") -> "_6585.CombinationAnalysis":
        from mastapy._private.system_model.analyses_and_results.flexible_pin_analyses import (
            _6585,
        )

        return self.__parent__._cast(_6585.CombinationAnalysis)

    @property
    def flexible_pin_analysis_gear_and_bearing_rating(
        self: "CastSelf",
    ) -> "FlexiblePinAnalysisGearAndBearingRating":
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
class FlexiblePinAnalysisGearAndBearingRating(_6586.FlexiblePinAnalysis):
    """FlexiblePinAnalysisGearAndBearingRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _FLEXIBLE_PIN_ANALYSIS_GEAR_AND_BEARING_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def gear_set_analysis(
        self: "Self",
    ) -> "_3148.CylindricalGearSetCompoundSystemDeflection":
        """mastapy.system_model.analyses_and_results.system_deflections.compound.CylindricalGearSetCompoundSystemDeflection

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearSetAnalysis")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def bearing_analyses(self: "Self") -> "List[_3107.BearingCompoundSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.compound.BearingCompoundSystemDeflection]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BearingAnalyses")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_FlexiblePinAnalysisGearAndBearingRating":
        """Cast to another type.

        Returns:
            _Cast_FlexiblePinAnalysisGearAndBearingRating
        """
        return _Cast_FlexiblePinAnalysisGearAndBearingRating(self)
