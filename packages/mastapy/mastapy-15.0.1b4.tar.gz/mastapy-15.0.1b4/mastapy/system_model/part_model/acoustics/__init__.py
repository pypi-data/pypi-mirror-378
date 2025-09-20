"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.acoustics._2871 import (
        AcousticAnalysisOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2872 import (
        AcousticAnalysisSetup,
    )
    from mastapy._private.system_model.part_model.acoustics._2873 import (
        AcousticAnalysisSetupCacheReporting,
    )
    from mastapy._private.system_model.part_model.acoustics._2874 import (
        AcousticAnalysisSetupCollection,
    )
    from mastapy._private.system_model.part_model.acoustics._2875 import (
        AcousticEnvelopeType,
    )
    from mastapy._private.system_model.part_model.acoustics._2876 import (
        AcousticInputSurfaceOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2877 import (
        CacheMemoryEstimates,
    )
    from mastapy._private.system_model.part_model.acoustics._2878 import (
        FEPartInputSurfaceOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2879 import (
        FESurfaceSelectionForAcousticEnvelope,
    )
    from mastapy._private.system_model.part_model.acoustics._2880 import HoleInFaceGroup
    from mastapy._private.system_model.part_model.acoustics._2881 import (
        MeshedResultPlane,
    )
    from mastapy._private.system_model.part_model.acoustics._2882 import (
        MeshedResultSphere,
    )
    from mastapy._private.system_model.part_model.acoustics._2883 import (
        MeshedResultSurface,
    )
    from mastapy._private.system_model.part_model.acoustics._2884 import (
        MeshedResultSurfaceBase,
    )
    from mastapy._private.system_model.part_model.acoustics._2885 import (
        MicrophoneArrayDesign,
    )
    from mastapy._private.system_model.part_model.acoustics._2886 import (
        PartSelectionForAcousticEnvelope,
    )
    from mastapy._private.system_model.part_model.acoustics._2887 import (
        ResultPlaneOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2888 import (
        ResultSphereOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2889 import (
        ResultSurfaceCollection,
    )
    from mastapy._private.system_model.part_model.acoustics._2890 import (
        ResultSurfaceOptions,
    )
    from mastapy._private.system_model.part_model.acoustics._2891 import (
        SphericalEnvelopeCentreDefinition,
    )
    from mastapy._private.system_model.part_model.acoustics._2892 import (
        SphericalEnvelopeType,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.acoustics._2871": ["AcousticAnalysisOptions"],
        "_private.system_model.part_model.acoustics._2872": ["AcousticAnalysisSetup"],
        "_private.system_model.part_model.acoustics._2873": [
            "AcousticAnalysisSetupCacheReporting"
        ],
        "_private.system_model.part_model.acoustics._2874": [
            "AcousticAnalysisSetupCollection"
        ],
        "_private.system_model.part_model.acoustics._2875": ["AcousticEnvelopeType"],
        "_private.system_model.part_model.acoustics._2876": [
            "AcousticInputSurfaceOptions"
        ],
        "_private.system_model.part_model.acoustics._2877": ["CacheMemoryEstimates"],
        "_private.system_model.part_model.acoustics._2878": [
            "FEPartInputSurfaceOptions"
        ],
        "_private.system_model.part_model.acoustics._2879": [
            "FESurfaceSelectionForAcousticEnvelope"
        ],
        "_private.system_model.part_model.acoustics._2880": ["HoleInFaceGroup"],
        "_private.system_model.part_model.acoustics._2881": ["MeshedResultPlane"],
        "_private.system_model.part_model.acoustics._2882": ["MeshedResultSphere"],
        "_private.system_model.part_model.acoustics._2883": ["MeshedResultSurface"],
        "_private.system_model.part_model.acoustics._2884": ["MeshedResultSurfaceBase"],
        "_private.system_model.part_model.acoustics._2885": ["MicrophoneArrayDesign"],
        "_private.system_model.part_model.acoustics._2886": [
            "PartSelectionForAcousticEnvelope"
        ],
        "_private.system_model.part_model.acoustics._2887": ["ResultPlaneOptions"],
        "_private.system_model.part_model.acoustics._2888": ["ResultSphereOptions"],
        "_private.system_model.part_model.acoustics._2889": ["ResultSurfaceCollection"],
        "_private.system_model.part_model.acoustics._2890": ["ResultSurfaceOptions"],
        "_private.system_model.part_model.acoustics._2891": [
            "SphericalEnvelopeCentreDefinition"
        ],
        "_private.system_model.part_model.acoustics._2892": ["SphericalEnvelopeType"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AcousticAnalysisOptions",
    "AcousticAnalysisSetup",
    "AcousticAnalysisSetupCacheReporting",
    "AcousticAnalysisSetupCollection",
    "AcousticEnvelopeType",
    "AcousticInputSurfaceOptions",
    "CacheMemoryEstimates",
    "FEPartInputSurfaceOptions",
    "FESurfaceSelectionForAcousticEnvelope",
    "HoleInFaceGroup",
    "MeshedResultPlane",
    "MeshedResultSphere",
    "MeshedResultSurface",
    "MeshedResultSurfaceBase",
    "MicrophoneArrayDesign",
    "PartSelectionForAcousticEnvelope",
    "ResultPlaneOptions",
    "ResultSphereOptions",
    "ResultSurfaceCollection",
    "ResultSurfaceOptions",
    "SphericalEnvelopeCentreDefinition",
    "SphericalEnvelopeType",
)
