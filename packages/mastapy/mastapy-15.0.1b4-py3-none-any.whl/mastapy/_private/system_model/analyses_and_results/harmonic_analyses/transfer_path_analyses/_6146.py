"""ModalAnalysisForTransferPathAnalysis"""

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
from mastapy._private.system_model.analyses_and_results.harmonic_analyses_single_excitation import (
    _6401,
)

_MODAL_ANALYSIS_FOR_TRANSFER_PATH_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses.TransferPathAnalyses",
    "ModalAnalysisForTransferPathAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2896
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7882,
        _7897,
    )
    from mastapy._private.system_model.analyses_and_results.harmonic_analyses.transfer_path_analyses import (
        _6145,
    )
    from mastapy._private.system_model.analyses_and_results.modal_analyses import _4931

    Self = TypeVar("Self", bound="ModalAnalysisForTransferPathAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ModalAnalysisForTransferPathAnalysis._Cast_ModalAnalysisForTransferPathAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ModalAnalysisForTransferPathAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ModalAnalysisForTransferPathAnalysis:
    """Special nested class for casting ModalAnalysisForTransferPathAnalysis to subclasses."""

    __parent__: "ModalAnalysisForTransferPathAnalysis"

    @property
    def modal_analysis_for_harmonic_analysis(
        self: "CastSelf",
    ) -> "_6401.ModalAnalysisForHarmonicAnalysis":
        return self.__parent__._cast(_6401.ModalAnalysisForHarmonicAnalysis)

    @property
    def modal_analysis(self: "CastSelf") -> "_4931.ModalAnalysis":
        from mastapy._private.system_model.analyses_and_results.modal_analyses import (
            _4931,
        )

        return self.__parent__._cast(_4931.ModalAnalysis)

    @property
    def static_load_analysis_case(self: "CastSelf") -> "_7897.StaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7897,
        )

        return self.__parent__._cast(_7897.StaticLoadAnalysisCase)

    @property
    def analysis_case(self: "CastSelf") -> "_7882.AnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7882,
        )

        return self.__parent__._cast(_7882.AnalysisCase)

    @property
    def context(self: "CastSelf") -> "_2896.Context":
        from mastapy._private.system_model.analyses_and_results import _2896

        return self.__parent__._cast(_2896.Context)

    @property
    def modal_analysis_for_transfer_path_analysis(
        self: "CastSelf",
    ) -> "ModalAnalysisForTransferPathAnalysis":
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
class ModalAnalysisForTransferPathAnalysis(_6401.ModalAnalysisForHarmonicAnalysis):
    """ModalAnalysisForTransferPathAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MODAL_ANALYSIS_FOR_TRANSFER_PATH_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def modal_analysis_results(
        self: "Self",
    ) -> "_6145.DynamicModelForTransferPathAnalysis":
        """mastapy.system_model.analyses_and_results.harmonic_analyses.transfer_path_analyses.DynamicModelForTransferPathAnalysis

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ModalAnalysisResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ModalAnalysisForTransferPathAnalysis":
        """Cast to another type.

        Returns:
            _Cast_ModalAnalysisForTransferPathAnalysis
        """
        return _Cast_ModalAnalysisForTransferPathAnalysis(self)
