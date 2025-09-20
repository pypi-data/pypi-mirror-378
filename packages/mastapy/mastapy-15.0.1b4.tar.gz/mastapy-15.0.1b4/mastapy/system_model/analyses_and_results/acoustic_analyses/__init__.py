"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7666 import (
        AcousticAnalysisRunType,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7667 import (
        AcousticPreconditionerType,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7668 import (
        AcousticSurfaceSelectionList,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7669 import (
        AcousticSurfaceWithSelection,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7670 import (
        HarmonicAcousticAnalysis,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7671 import (
        InitialGuessOption,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7672 import (
        M2LHfCacheType,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7673 import (
        NearFieldIntegralsCacheType,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7674 import (
        OctreeCreationMethod,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7675 import (
        SingleExcitationDetails,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7676 import (
        SingleHarmonicExcitationAnalysisDetail,
    )
    from mastapy._private.system_model.analyses_and_results.acoustic_analyses._7677 import (
        UnitForceExcitationAnalysisDetail,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.analyses_and_results.acoustic_analyses._7666": [
            "AcousticAnalysisRunType"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7667": [
            "AcousticPreconditionerType"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7668": [
            "AcousticSurfaceSelectionList"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7669": [
            "AcousticSurfaceWithSelection"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7670": [
            "HarmonicAcousticAnalysis"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7671": [
            "InitialGuessOption"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7672": [
            "M2LHfCacheType"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7673": [
            "NearFieldIntegralsCacheType"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7674": [
            "OctreeCreationMethod"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7675": [
            "SingleExcitationDetails"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7676": [
            "SingleHarmonicExcitationAnalysisDetail"
        ],
        "_private.system_model.analyses_and_results.acoustic_analyses._7677": [
            "UnitForceExcitationAnalysisDetail"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AcousticAnalysisRunType",
    "AcousticPreconditionerType",
    "AcousticSurfaceSelectionList",
    "AcousticSurfaceWithSelection",
    "HarmonicAcousticAnalysis",
    "InitialGuessOption",
    "M2LHfCacheType",
    "NearFieldIntegralsCacheType",
    "OctreeCreationMethod",
    "SingleExcitationDetails",
    "SingleHarmonicExcitationAnalysisDetail",
    "UnitForceExcitationAnalysisDetail",
)
