"""CVTBeltConnectionCompoundModalAnalysisAtAStiffness"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
    _5279,
)

_CVT_BELT_CONNECTION_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.ModalAnalysesAtAStiffness.Compound",
    "CVTBeltConnectionCompoundModalAnalysisAtAStiffness",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7886,
        _7890,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness import (
        _5177,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
        _5305,
        _5335,
    )

    Self = TypeVar("Self", bound="CVTBeltConnectionCompoundModalAnalysisAtAStiffness")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CVTBeltConnectionCompoundModalAnalysisAtAStiffness._Cast_CVTBeltConnectionCompoundModalAnalysisAtAStiffness",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CVTBeltConnectionCompoundModalAnalysisAtAStiffness",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CVTBeltConnectionCompoundModalAnalysisAtAStiffness:
    """Special nested class for casting CVTBeltConnectionCompoundModalAnalysisAtAStiffness to subclasses."""

    __parent__: "CVTBeltConnectionCompoundModalAnalysisAtAStiffness"

    @property
    def belt_connection_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5279.BeltConnectionCompoundModalAnalysisAtAStiffness":
        return self.__parent__._cast(
            _5279.BeltConnectionCompoundModalAnalysisAtAStiffness
        )

    @property
    def inter_mountable_component_connection_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5335.InterMountableComponentConnectionCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5335,
        )

        return self.__parent__._cast(
            _5335.InterMountableComponentConnectionCompoundModalAnalysisAtAStiffness
        )

    @property
    def connection_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_5305.ConnectionCompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results.modal_analyses_at_a_stiffness.compound import (
            _5305,
        )

        return self.__parent__._cast(_5305.ConnectionCompoundModalAnalysisAtAStiffness)

    @property
    def connection_compound_analysis(
        self: "CastSelf",
    ) -> "_7886.ConnectionCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7886,
        )

        return self.__parent__._cast(_7886.ConnectionCompoundAnalysis)

    @property
    def design_entity_compound_analysis(
        self: "CastSelf",
    ) -> "_7890.DesignEntityCompoundAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7890,
        )

        return self.__parent__._cast(_7890.DesignEntityCompoundAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2897.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2897

        return self.__parent__._cast(_2897.DesignEntityAnalysis)

    @property
    def cvt_belt_connection_compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "CVTBeltConnectionCompoundModalAnalysisAtAStiffness":
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
class CVTBeltConnectionCompoundModalAnalysisAtAStiffness(
    _5279.BeltConnectionCompoundModalAnalysisAtAStiffness
):
    """CVTBeltConnectionCompoundModalAnalysisAtAStiffness

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CVT_BELT_CONNECTION_COMPOUND_MODAL_ANALYSIS_AT_A_STIFFNESS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def connection_analysis_cases_ready(
        self: "Self",
    ) -> "List[_5177.CVTBeltConnectionModalAnalysisAtAStiffness]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.CVTBeltConnectionModalAnalysisAtAStiffness]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCasesReady")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def connection_analysis_cases(
        self: "Self",
    ) -> "List[_5177.CVTBeltConnectionModalAnalysisAtAStiffness]":
        """List[mastapy.system_model.analyses_and_results.modal_analyses_at_a_stiffness.CVTBeltConnectionModalAnalysisAtAStiffness]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConnectionAnalysisCases")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_CVTBeltConnectionCompoundModalAnalysisAtAStiffness":
        """Cast to another type.

        Returns:
            _Cast_CVTBeltConnectionCompoundModalAnalysisAtAStiffness
        """
        return _Cast_CVTBeltConnectionCompoundModalAnalysisAtAStiffness(self)
