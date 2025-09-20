"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.nodal_analysis.component_mode_synthesis._310 import (
        AddNodeToGroupByID,
    )
    from mastapy._private.nodal_analysis.component_mode_synthesis._311 import (
        CMSElementFaceGroup,
    )
    from mastapy._private.nodal_analysis.component_mode_synthesis._312 import (
        CMSElementFaceGroupOfAllFreeFaces,
    )
    from mastapy._private.nodal_analysis.component_mode_synthesis._313 import CMSModel
    from mastapy._private.nodal_analysis.component_mode_synthesis._314 import (
        CMSNodeGroup,
    )
    from mastapy._private.nodal_analysis.component_mode_synthesis._315 import CMSOptions
    from mastapy._private.nodal_analysis.component_mode_synthesis._316 import CMSResults
    from mastapy._private.nodal_analysis.component_mode_synthesis._317 import (
        FESectionResults,
    )
    from mastapy._private.nodal_analysis.component_mode_synthesis._318 import (
        HarmonicCMSResults,
    )
    from mastapy._private.nodal_analysis.component_mode_synthesis._319 import (
        ModalCMSResults,
    )
    from mastapy._private.nodal_analysis.component_mode_synthesis._320 import (
        RealCMSResults,
    )
    from mastapy._private.nodal_analysis.component_mode_synthesis._321 import (
        ReductionModeType,
    )
    from mastapy._private.nodal_analysis.component_mode_synthesis._322 import (
        SoftwareUsedForReductionType,
    )
    from mastapy._private.nodal_analysis.component_mode_synthesis._323 import (
        StaticCMSResults,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.nodal_analysis.component_mode_synthesis._310": ["AddNodeToGroupByID"],
        "_private.nodal_analysis.component_mode_synthesis._311": [
            "CMSElementFaceGroup"
        ],
        "_private.nodal_analysis.component_mode_synthesis._312": [
            "CMSElementFaceGroupOfAllFreeFaces"
        ],
        "_private.nodal_analysis.component_mode_synthesis._313": ["CMSModel"],
        "_private.nodal_analysis.component_mode_synthesis._314": ["CMSNodeGroup"],
        "_private.nodal_analysis.component_mode_synthesis._315": ["CMSOptions"],
        "_private.nodal_analysis.component_mode_synthesis._316": ["CMSResults"],
        "_private.nodal_analysis.component_mode_synthesis._317": ["FESectionResults"],
        "_private.nodal_analysis.component_mode_synthesis._318": ["HarmonicCMSResults"],
        "_private.nodal_analysis.component_mode_synthesis._319": ["ModalCMSResults"],
        "_private.nodal_analysis.component_mode_synthesis._320": ["RealCMSResults"],
        "_private.nodal_analysis.component_mode_synthesis._321": ["ReductionModeType"],
        "_private.nodal_analysis.component_mode_synthesis._322": [
            "SoftwareUsedForReductionType"
        ],
        "_private.nodal_analysis.component_mode_synthesis._323": ["StaticCMSResults"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AddNodeToGroupByID",
    "CMSElementFaceGroup",
    "CMSElementFaceGroupOfAllFreeFaces",
    "CMSModel",
    "CMSNodeGroup",
    "CMSOptions",
    "CMSResults",
    "FESectionResults",
    "HarmonicCMSResults",
    "ModalCMSResults",
    "RealCMSResults",
    "ReductionModeType",
    "SoftwareUsedForReductionType",
    "StaticCMSResults",
)
