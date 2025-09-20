"""StabilityAnalysisDrawStyle"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.analyses_and_results.rotor_dynamics import _4292

_STABILITY_ANALYSIS_DRAW_STYLE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StabilityAnalyses",
    "StabilityAnalysisDrawStyle",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.geometry import _398
    from mastapy._private.system_model.drawing import _2472

    Self = TypeVar("Self", bound="StabilityAnalysisDrawStyle")
    CastSelf = TypeVar(
        "CastSelf", bound="StabilityAnalysisDrawStyle._Cast_StabilityAnalysisDrawStyle"
    )


__docformat__ = "restructuredtext en"
__all__ = ("StabilityAnalysisDrawStyle",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StabilityAnalysisDrawStyle:
    """Special nested class for casting StabilityAnalysisDrawStyle to subclasses."""

    __parent__: "StabilityAnalysisDrawStyle"

    @property
    def rotor_dynamics_draw_style(self: "CastSelf") -> "_4292.RotorDynamicsDrawStyle":
        return self.__parent__._cast(_4292.RotorDynamicsDrawStyle)

    @property
    def contour_draw_style(self: "CastSelf") -> "_2472.ContourDrawStyle":
        from mastapy._private.system_model.drawing import _2472

        return self.__parent__._cast(_2472.ContourDrawStyle)

    @property
    def draw_style_base(self: "CastSelf") -> "_398.DrawStyleBase":
        from mastapy._private.geometry import _398

        return self.__parent__._cast(_398.DrawStyleBase)

    @property
    def stability_analysis_draw_style(self: "CastSelf") -> "StabilityAnalysisDrawStyle":
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
class StabilityAnalysisDrawStyle(_4292.RotorDynamicsDrawStyle):
    """StabilityAnalysisDrawStyle

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STABILITY_ANALYSIS_DRAW_STYLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_StabilityAnalysisDrawStyle":
        """Cast to another type.

        Returns:
            _Cast_StabilityAnalysisDrawStyle
        """
        return _Cast_StabilityAnalysisDrawStyle(self)
