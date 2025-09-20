"""CompoundModalAnalysisAtASpeed"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.analyses_and_results import _2893

_COMPOUND_MODAL_ANALYSIS_AT_A_SPEED = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults", "CompoundModalAnalysisAtASpeed"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private import _7900

    Self = TypeVar("Self", bound="CompoundModalAnalysisAtASpeed")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CompoundModalAnalysisAtASpeed._Cast_CompoundModalAnalysisAtASpeed",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CompoundModalAnalysisAtASpeed",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CompoundModalAnalysisAtASpeed:
    """Special nested class for casting CompoundModalAnalysisAtASpeed to subclasses."""

    __parent__: "CompoundModalAnalysisAtASpeed"

    @property
    def compound_analysis(self: "CastSelf") -> "_2893.CompoundAnalysis":
        return self.__parent__._cast(_2893.CompoundAnalysis)

    @property
    def marshal_by_ref_object_permanent(
        self: "CastSelf",
    ) -> "_7900.MarshalByRefObjectPermanent":
        from mastapy._private import _7900

        return self.__parent__._cast(_7900.MarshalByRefObjectPermanent)

    @property
    def compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "CompoundModalAnalysisAtASpeed":
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
class CompoundModalAnalysisAtASpeed(_2893.CompoundAnalysis):
    """CompoundModalAnalysisAtASpeed

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPOUND_MODAL_ANALYSIS_AT_A_SPEED

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CompoundModalAnalysisAtASpeed":
        """Cast to another type.

        Returns:
            _Cast_CompoundModalAnalysisAtASpeed
        """
        return _Cast_CompoundModalAnalysisAtASpeed(self)
