"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.nodal_analysis.elmer._249 import ContactType
    from mastapy._private.nodal_analysis.elmer._250 import ElectricMachineAnalysisPeriod
    from mastapy._private.nodal_analysis.elmer._251 import ElmerResultEntityType
    from mastapy._private.nodal_analysis.elmer._252 import ElmerResults
    from mastapy._private.nodal_analysis.elmer._253 import (
        ElmerResultsFromElectromagneticAnalysis,
    )
    from mastapy._private.nodal_analysis.elmer._254 import (
        ElmerResultsFromMechanicalAnalysis,
    )
    from mastapy._private.nodal_analysis.elmer._255 import ElmerResultsViewable
    from mastapy._private.nodal_analysis.elmer._256 import ElmerResultType
    from mastapy._private.nodal_analysis.elmer._257 import (
        MechanicalContactSpecification,
    )
    from mastapy._private.nodal_analysis.elmer._258 import MechanicalSolverType
    from mastapy._private.nodal_analysis.elmer._259 import NodalAverageType
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.nodal_analysis.elmer._249": ["ContactType"],
        "_private.nodal_analysis.elmer._250": ["ElectricMachineAnalysisPeriod"],
        "_private.nodal_analysis.elmer._251": ["ElmerResultEntityType"],
        "_private.nodal_analysis.elmer._252": ["ElmerResults"],
        "_private.nodal_analysis.elmer._253": [
            "ElmerResultsFromElectromagneticAnalysis"
        ],
        "_private.nodal_analysis.elmer._254": ["ElmerResultsFromMechanicalAnalysis"],
        "_private.nodal_analysis.elmer._255": ["ElmerResultsViewable"],
        "_private.nodal_analysis.elmer._256": ["ElmerResultType"],
        "_private.nodal_analysis.elmer._257": ["MechanicalContactSpecification"],
        "_private.nodal_analysis.elmer._258": ["MechanicalSolverType"],
        "_private.nodal_analysis.elmer._259": ["NodalAverageType"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ContactType",
    "ElectricMachineAnalysisPeriod",
    "ElmerResultEntityType",
    "ElmerResults",
    "ElmerResultsFromElectromagneticAnalysis",
    "ElmerResultsFromMechanicalAnalysis",
    "ElmerResultsViewable",
    "ElmerResultType",
    "MechanicalContactSpecification",
    "MechanicalSolverType",
    "NodalAverageType",
)
