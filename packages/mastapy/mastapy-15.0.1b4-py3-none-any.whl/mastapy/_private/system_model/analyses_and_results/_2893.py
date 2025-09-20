"""CompoundAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _7900
from mastapy._private._internal import conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_method_call_overload,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

_TASK_PROGRESS = python_net_import("SMT.MastaAPIUtility", "TaskProgress")
_COMPOUND_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults", "CompoundAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Iterable, Type, TypeVar

    from mastapy._private import _7906
    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.analyses_and_results import (
        _2904,
        _2905,
        _2906,
        _2907,
        _2908,
        _2909,
        _2910,
        _2911,
        _2912,
        _2913,
        _2914,
        _2915,
        _2916,
        _2917,
        _2918,
        _2919,
        _2920,
        _2921,
        _2922,
        _2923,
        _2924,
        _2925,
        _2926,
        _2927,
        _2928,
    )
    from mastapy._private.system_model.analyses_and_results.analysis_cases import _7890

    Self = TypeVar("Self", bound="CompoundAnalysis")
    CastSelf = TypeVar("CastSelf", bound="CompoundAnalysis._Cast_CompoundAnalysis")


__docformat__ = "restructuredtext en"
__all__ = ("CompoundAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CompoundAnalysis:
    """Special nested class for casting CompoundAnalysis to subclasses."""

    __parent__: "CompoundAnalysis"

    @property
    def marshal_by_ref_object_permanent(
        self: "CastSelf",
    ) -> "_7900.MarshalByRefObjectPermanent":
        return self.__parent__._cast(_7900.MarshalByRefObjectPermanent)

    @property
    def compound_advanced_system_deflection(
        self: "CastSelf",
    ) -> "_2904.CompoundAdvancedSystemDeflection":
        from mastapy._private.system_model.analyses_and_results import _2904

        return self.__parent__._cast(_2904.CompoundAdvancedSystemDeflection)

    @property
    def compound_advanced_system_deflection_sub_analysis(
        self: "CastSelf",
    ) -> "_2905.CompoundAdvancedSystemDeflectionSubAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2905

        return self.__parent__._cast(_2905.CompoundAdvancedSystemDeflectionSubAnalysis)

    @property
    def compound_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_2906.CompoundAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results import _2906

        return self.__parent__._cast(
            _2906.CompoundAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def compound_critical_speed_analysis(
        self: "CastSelf",
    ) -> "_2907.CompoundCriticalSpeedAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2907

        return self.__parent__._cast(_2907.CompoundCriticalSpeedAnalysis)

    @property
    def compound_dynamic_analysis(self: "CastSelf") -> "_2908.CompoundDynamicAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2908

        return self.__parent__._cast(_2908.CompoundDynamicAnalysis)

    @property
    def compound_dynamic_model_at_a_stiffness(
        self: "CastSelf",
    ) -> "_2909.CompoundDynamicModelAtAStiffness":
        from mastapy._private.system_model.analyses_and_results import _2909

        return self.__parent__._cast(_2909.CompoundDynamicModelAtAStiffness)

    @property
    def compound_dynamic_model_for_harmonic_analysis(
        self: "CastSelf",
    ) -> "_2910.CompoundDynamicModelForHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2910

        return self.__parent__._cast(_2910.CompoundDynamicModelForHarmonicAnalysis)

    @property
    def compound_dynamic_model_for_modal_analysis(
        self: "CastSelf",
    ) -> "_2911.CompoundDynamicModelForModalAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2911

        return self.__parent__._cast(_2911.CompoundDynamicModelForModalAnalysis)

    @property
    def compound_dynamic_model_for_stability_analysis(
        self: "CastSelf",
    ) -> "_2912.CompoundDynamicModelForStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2912

        return self.__parent__._cast(_2912.CompoundDynamicModelForStabilityAnalysis)

    @property
    def compound_dynamic_model_for_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_2913.CompoundDynamicModelForSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results import _2913

        return self.__parent__._cast(
            _2913.CompoundDynamicModelForSteadyStateSynchronousResponse
        )

    @property
    def compound_harmonic_analysis(
        self: "CastSelf",
    ) -> "_2914.CompoundHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2914

        return self.__parent__._cast(_2914.CompoundHarmonicAnalysis)

    @property
    def compound_harmonic_analysis_for_advanced_time_stepping_analysis_for_modulation(
        self: "CastSelf",
    ) -> "_2915.CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation":
        from mastapy._private.system_model.analyses_and_results import _2915

        return self.__parent__._cast(
            _2915.CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation
        )

    @property
    def compound_harmonic_analysis_of_single_excitation(
        self: "CastSelf",
    ) -> "_2916.CompoundHarmonicAnalysisOfSingleExcitation":
        from mastapy._private.system_model.analyses_and_results import _2916

        return self.__parent__._cast(_2916.CompoundHarmonicAnalysisOfSingleExcitation)

    @property
    def compound_modal_analysis(self: "CastSelf") -> "_2917.CompoundModalAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2917

        return self.__parent__._cast(_2917.CompoundModalAnalysis)

    @property
    def compound_modal_analysis_at_a_speed(
        self: "CastSelf",
    ) -> "_2918.CompoundModalAnalysisAtASpeed":
        from mastapy._private.system_model.analyses_and_results import _2918

        return self.__parent__._cast(_2918.CompoundModalAnalysisAtASpeed)

    @property
    def compound_modal_analysis_at_a_stiffness(
        self: "CastSelf",
    ) -> "_2919.CompoundModalAnalysisAtAStiffness":
        from mastapy._private.system_model.analyses_and_results import _2919

        return self.__parent__._cast(_2919.CompoundModalAnalysisAtAStiffness)

    @property
    def compound_modal_analysis_for_harmonic_analysis(
        self: "CastSelf",
    ) -> "_2920.CompoundModalAnalysisForHarmonicAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2920

        return self.__parent__._cast(_2920.CompoundModalAnalysisForHarmonicAnalysis)

    @property
    def compound_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_2921.CompoundMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2921

        return self.__parent__._cast(_2921.CompoundMultibodyDynamicsAnalysis)

    @property
    def compound_power_flow(self: "CastSelf") -> "_2922.CompoundPowerFlow":
        from mastapy._private.system_model.analyses_and_results import _2922

        return self.__parent__._cast(_2922.CompoundPowerFlow)

    @property
    def compound_stability_analysis(
        self: "CastSelf",
    ) -> "_2923.CompoundStabilityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2923

        return self.__parent__._cast(_2923.CompoundStabilityAnalysis)

    @property
    def compound_steady_state_synchronous_response(
        self: "CastSelf",
    ) -> "_2924.CompoundSteadyStateSynchronousResponse":
        from mastapy._private.system_model.analyses_and_results import _2924

        return self.__parent__._cast(_2924.CompoundSteadyStateSynchronousResponse)

    @property
    def compound_steady_state_synchronous_response_at_a_speed(
        self: "CastSelf",
    ) -> "_2925.CompoundSteadyStateSynchronousResponseAtASpeed":
        from mastapy._private.system_model.analyses_and_results import _2925

        return self.__parent__._cast(
            _2925.CompoundSteadyStateSynchronousResponseAtASpeed
        )

    @property
    def compound_steady_state_synchronous_response_on_a_shaft(
        self: "CastSelf",
    ) -> "_2926.CompoundSteadyStateSynchronousResponseOnAShaft":
        from mastapy._private.system_model.analyses_and_results import _2926

        return self.__parent__._cast(
            _2926.CompoundSteadyStateSynchronousResponseOnAShaft
        )

    @property
    def compound_system_deflection(
        self: "CastSelf",
    ) -> "_2927.CompoundSystemDeflection":
        from mastapy._private.system_model.analyses_and_results import _2927

        return self.__parent__._cast(_2927.CompoundSystemDeflection)

    @property
    def compound_torsional_system_deflection(
        self: "CastSelf",
    ) -> "_2928.CompoundTorsionalSystemDeflection":
        from mastapy._private.system_model.analyses_and_results import _2928

        return self.__parent__._cast(_2928.CompoundTorsionalSystemDeflection)

    @property
    def compound_analysis(self: "CastSelf") -> "CompoundAnalysis":
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
class CompoundAnalysis(_7900.MarshalByRefObjectPermanent):
    """CompoundAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPOUND_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def results_ready(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ResultsReady")

        if temp is None:
            return False

        return temp

    @exception_bridge
    def perform_analysis(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "PerformAnalysis")

    @exception_bridge
    @enforce_parameter_types
    def perform_analysis_with_progress(
        self: "Self", progress: "_7906.TaskProgress"
    ) -> None:
        """Method does not return.

        Args:
            progress (mastapy.TaskProgress)
        """
        pythonnet_method_call_overload(
            self.wrapped,
            "PerformAnalysis",
            [_TASK_PROGRESS],
            progress.wrapped if progress else None,
        )

    @exception_bridge
    @enforce_parameter_types
    def results_for(
        self: "Self", design_entity: "_2419.DesignEntity"
    ) -> "Iterable[_7890.DesignEntityCompoundAnalysis]":
        """Iterable[mastapy.system_model.analyses_and_results.analysis_cases.DesignEntityCompoundAnalysis]

        Args:
            design_entity (mastapy.system_model.DesignEntity)
        """
        return conversion.pn_to_mp_objects_in_iterable(
            pythonnet_method_call(
                self.wrapped,
                "ResultsFor",
                design_entity.wrapped if design_entity else None,
            )
        )

    @property
    def cast_to(self: "Self") -> "_Cast_CompoundAnalysis":
        """Cast to another type.

        Returns:
            _Cast_CompoundAnalysis
        """
        return _Cast_CompoundAnalysis(self)
