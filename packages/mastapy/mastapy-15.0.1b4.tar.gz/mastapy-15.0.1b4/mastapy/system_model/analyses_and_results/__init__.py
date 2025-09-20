"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.analyses_and_results._2893 import (
        CompoundAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2894 import (
        AnalysisCaseVariable,
    )
    from mastapy._private.system_model.analyses_and_results._2895 import (
        ConnectionAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2896 import Context
    from mastapy._private.system_model.analyses_and_results._2897 import (
        DesignEntityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2898 import (
        DesignEntityGroupAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2899 import (
        DesignEntitySingleContextAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2903 import PartAnalysis
    from mastapy._private.system_model.analyses_and_results._2904 import (
        CompoundAdvancedSystemDeflection,
    )
    from mastapy._private.system_model.analyses_and_results._2905 import (
        CompoundAdvancedSystemDeflectionSubAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2906 import (
        CompoundAdvancedTimeSteppingAnalysisForModulation,
    )
    from mastapy._private.system_model.analyses_and_results._2907 import (
        CompoundCriticalSpeedAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2908 import (
        CompoundDynamicAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2909 import (
        CompoundDynamicModelAtAStiffness,
    )
    from mastapy._private.system_model.analyses_and_results._2910 import (
        CompoundDynamicModelForHarmonicAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2911 import (
        CompoundDynamicModelForModalAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2912 import (
        CompoundDynamicModelForStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2913 import (
        CompoundDynamicModelForSteadyStateSynchronousResponse,
    )
    from mastapy._private.system_model.analyses_and_results._2914 import (
        CompoundHarmonicAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2915 import (
        CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation,
    )
    from mastapy._private.system_model.analyses_and_results._2916 import (
        CompoundHarmonicAnalysisOfSingleExcitation,
    )
    from mastapy._private.system_model.analyses_and_results._2917 import (
        CompoundModalAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2918 import (
        CompoundModalAnalysisAtASpeed,
    )
    from mastapy._private.system_model.analyses_and_results._2919 import (
        CompoundModalAnalysisAtAStiffness,
    )
    from mastapy._private.system_model.analyses_and_results._2920 import (
        CompoundModalAnalysisForHarmonicAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2921 import (
        CompoundMultibodyDynamicsAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2922 import (
        CompoundPowerFlow,
    )
    from mastapy._private.system_model.analyses_and_results._2923 import (
        CompoundStabilityAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results._2924 import (
        CompoundSteadyStateSynchronousResponse,
    )
    from mastapy._private.system_model.analyses_and_results._2925 import (
        CompoundSteadyStateSynchronousResponseAtASpeed,
    )
    from mastapy._private.system_model.analyses_and_results._2926 import (
        CompoundSteadyStateSynchronousResponseOnAShaft,
    )
    from mastapy._private.system_model.analyses_and_results._2927 import (
        CompoundSystemDeflection,
    )
    from mastapy._private.system_model.analyses_and_results._2928 import (
        CompoundTorsionalSystemDeflection,
    )
    from mastapy._private.system_model.analyses_and_results._2929 import (
        TESetUpForDynamicAnalysisOptions,
    )
    from mastapy._private.system_model.analyses_and_results._2930 import TimeOptions
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.analyses_and_results._2893": ["CompoundAnalysis"],
        "_private.system_model.analyses_and_results._2894": ["AnalysisCaseVariable"],
        "_private.system_model.analyses_and_results._2895": ["ConnectionAnalysis"],
        "_private.system_model.analyses_and_results._2896": ["Context"],
        "_private.system_model.analyses_and_results._2897": ["DesignEntityAnalysis"],
        "_private.system_model.analyses_and_results._2898": [
            "DesignEntityGroupAnalysis"
        ],
        "_private.system_model.analyses_and_results._2899": [
            "DesignEntitySingleContextAnalysis"
        ],
        "_private.system_model.analyses_and_results._2903": ["PartAnalysis"],
        "_private.system_model.analyses_and_results._2904": [
            "CompoundAdvancedSystemDeflection"
        ],
        "_private.system_model.analyses_and_results._2905": [
            "CompoundAdvancedSystemDeflectionSubAnalysis"
        ],
        "_private.system_model.analyses_and_results._2906": [
            "CompoundAdvancedTimeSteppingAnalysisForModulation"
        ],
        "_private.system_model.analyses_and_results._2907": [
            "CompoundCriticalSpeedAnalysis"
        ],
        "_private.system_model.analyses_and_results._2908": ["CompoundDynamicAnalysis"],
        "_private.system_model.analyses_and_results._2909": [
            "CompoundDynamicModelAtAStiffness"
        ],
        "_private.system_model.analyses_and_results._2910": [
            "CompoundDynamicModelForHarmonicAnalysis"
        ],
        "_private.system_model.analyses_and_results._2911": [
            "CompoundDynamicModelForModalAnalysis"
        ],
        "_private.system_model.analyses_and_results._2912": [
            "CompoundDynamicModelForStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results._2913": [
            "CompoundDynamicModelForSteadyStateSynchronousResponse"
        ],
        "_private.system_model.analyses_and_results._2914": [
            "CompoundHarmonicAnalysis"
        ],
        "_private.system_model.analyses_and_results._2915": [
            "CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation"
        ],
        "_private.system_model.analyses_and_results._2916": [
            "CompoundHarmonicAnalysisOfSingleExcitation"
        ],
        "_private.system_model.analyses_and_results._2917": ["CompoundModalAnalysis"],
        "_private.system_model.analyses_and_results._2918": [
            "CompoundModalAnalysisAtASpeed"
        ],
        "_private.system_model.analyses_and_results._2919": [
            "CompoundModalAnalysisAtAStiffness"
        ],
        "_private.system_model.analyses_and_results._2920": [
            "CompoundModalAnalysisForHarmonicAnalysis"
        ],
        "_private.system_model.analyses_and_results._2921": [
            "CompoundMultibodyDynamicsAnalysis"
        ],
        "_private.system_model.analyses_and_results._2922": ["CompoundPowerFlow"],
        "_private.system_model.analyses_and_results._2923": [
            "CompoundStabilityAnalysis"
        ],
        "_private.system_model.analyses_and_results._2924": [
            "CompoundSteadyStateSynchronousResponse"
        ],
        "_private.system_model.analyses_and_results._2925": [
            "CompoundSteadyStateSynchronousResponseAtASpeed"
        ],
        "_private.system_model.analyses_and_results._2926": [
            "CompoundSteadyStateSynchronousResponseOnAShaft"
        ],
        "_private.system_model.analyses_and_results._2927": [
            "CompoundSystemDeflection"
        ],
        "_private.system_model.analyses_and_results._2928": [
            "CompoundTorsionalSystemDeflection"
        ],
        "_private.system_model.analyses_and_results._2929": [
            "TESetUpForDynamicAnalysisOptions"
        ],
        "_private.system_model.analyses_and_results._2930": ["TimeOptions"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CompoundAnalysis",
    "AnalysisCaseVariable",
    "ConnectionAnalysis",
    "Context",
    "DesignEntityAnalysis",
    "DesignEntityGroupAnalysis",
    "DesignEntitySingleContextAnalysis",
    "PartAnalysis",
    "CompoundAdvancedSystemDeflection",
    "CompoundAdvancedSystemDeflectionSubAnalysis",
    "CompoundAdvancedTimeSteppingAnalysisForModulation",
    "CompoundCriticalSpeedAnalysis",
    "CompoundDynamicAnalysis",
    "CompoundDynamicModelAtAStiffness",
    "CompoundDynamicModelForHarmonicAnalysis",
    "CompoundDynamicModelForModalAnalysis",
    "CompoundDynamicModelForStabilityAnalysis",
    "CompoundDynamicModelForSteadyStateSynchronousResponse",
    "CompoundHarmonicAnalysis",
    "CompoundHarmonicAnalysisForAdvancedTimeSteppingAnalysisForModulation",
    "CompoundHarmonicAnalysisOfSingleExcitation",
    "CompoundModalAnalysis",
    "CompoundModalAnalysisAtASpeed",
    "CompoundModalAnalysisAtAStiffness",
    "CompoundModalAnalysisForHarmonicAnalysis",
    "CompoundMultibodyDynamicsAnalysis",
    "CompoundPowerFlow",
    "CompoundStabilityAnalysis",
    "CompoundSteadyStateSynchronousResponse",
    "CompoundSteadyStateSynchronousResponseAtASpeed",
    "CompoundSteadyStateSynchronousResponseOnAShaft",
    "CompoundSystemDeflection",
    "CompoundTorsionalSystemDeflection",
    "TESetUpForDynamicAnalysisOptions",
    "TimeOptions",
)
