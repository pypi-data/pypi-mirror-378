"""DynamicAnalysisDrawStyle"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.system_model.drawing import _2472

_DYNAMIC_ANALYSIS_DRAW_STYLE = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.DynamicAnalyses",
    "DynamicAnalysisDrawStyle",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.geometry import _398
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _6059,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import _4934

    Self = TypeVar("Self", bound="DynamicAnalysisDrawStyle")
    CastSelf = TypeVar(
        "CastSelf", bound="DynamicAnalysisDrawStyle._Cast_DynamicAnalysisDrawStyle"
    )


__docformat__ = "restructuredtext en"
__all__ = ("DynamicAnalysisDrawStyle",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_DynamicAnalysisDrawStyle:
    """Special nested class for casting DynamicAnalysisDrawStyle to subclasses."""

    __parent__: "DynamicAnalysisDrawStyle"

    @property
    def contour_draw_style(self: "CastSelf") -> "_2472.ContourDrawStyle":
        return self.__parent__._cast(_2472.ContourDrawStyle)

    @property
    def draw_style_base(self: "CastSelf") -> "_398.DrawStyleBase":
        from mastapy._private.geometry import _398

        return self.__parent__._cast(_398.DrawStyleBase)

    @property
    def modal_analysis_draw_style(self: "CastSelf") -> "_4934.ModalAnalysisDrawStyle":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4934,
        )

        return self.__parent__._cast(_4934.ModalAnalysisDrawStyle)

    @property
    def harmonic_analysis_draw_style(
        self: "CastSelf",
    ) -> "_6059.HarmonicAnalysisDrawStyle":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6059,
        )

        return self.__parent__._cast(_6059.HarmonicAnalysisDrawStyle)

    @property
    def dynamic_analysis_draw_style(self: "CastSelf") -> "DynamicAnalysisDrawStyle":
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
class DynamicAnalysisDrawStyle(_2472.ContourDrawStyle):
    """DynamicAnalysisDrawStyle

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _DYNAMIC_ANALYSIS_DRAW_STYLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def animate_contour(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "AnimateContour")

        if temp is None:
            return False

        return temp

    @animate_contour.setter
    @exception_bridge
    @enforce_parameter_types
    def animate_contour(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped, "AnimateContour", bool(value) if value is not None else False
        )

    @property
    @exception_bridge
    def show_microphones(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "ShowMicrophones")

        if temp is None:
            return False

        return temp

    @show_microphones.setter
    @exception_bridge
    @enforce_parameter_types
    def show_microphones(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped, "ShowMicrophones", bool(value) if value is not None else False
        )

    @property
    def cast_to(self: "Self") -> "_Cast_DynamicAnalysisDrawStyle":
        """Cast to another type.

        Returns:
            _Cast_DynamicAnalysisDrawStyle
        """
        return _Cast_DynamicAnalysisDrawStyle(self)
