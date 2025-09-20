"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.drawing.options._2487 import (
        AdvancedTimeSteppingAnalysisForModulationModeViewOptions,
    )
    from mastapy._private.system_model.drawing.options._2488 import (
        ExcitationAnalysisViewOption,
    )
    from mastapy._private.system_model.drawing.options._2489 import (
        ModalContributionViewOptions,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.drawing.options._2487": [
            "AdvancedTimeSteppingAnalysisForModulationModeViewOptions"
        ],
        "_private.system_model.drawing.options._2488": ["ExcitationAnalysisViewOption"],
        "_private.system_model.drawing.options._2489": ["ModalContributionViewOptions"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AdvancedTimeSteppingAnalysisForModulationModeViewOptions",
    "ExcitationAnalysisViewOption",
    "ModalContributionViewOptions",
)
