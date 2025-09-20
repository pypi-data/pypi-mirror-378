"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility_gui.charts._2060 import BubbleChartDefinition
    from mastapy._private.utility_gui.charts._2061 import ConstantLine
    from mastapy._private.utility_gui.charts._2062 import CustomLineChart
    from mastapy._private.utility_gui.charts._2063 import CustomTableAndChart
    from mastapy._private.utility_gui.charts._2064 import LegacyChartMathChartDefinition
    from mastapy._private.utility_gui.charts._2065 import MatrixVisualisationDefinition
    from mastapy._private.utility_gui.charts._2066 import ModeConstantLine
    from mastapy._private.utility_gui.charts._2067 import NDChartDefinition
    from mastapy._private.utility_gui.charts._2068 import (
        ParallelCoordinatesChartDefinition,
    )
    from mastapy._private.utility_gui.charts._2069 import PointsForSurface
    from mastapy._private.utility_gui.charts._2070 import ScatterChartDefinition
    from mastapy._private.utility_gui.charts._2071 import Series2D
    from mastapy._private.utility_gui.charts._2072 import SMTAxis
    from mastapy._private.utility_gui.charts._2073 import ThreeDChartDefinition
    from mastapy._private.utility_gui.charts._2074 import ThreeDVectorChartDefinition
    from mastapy._private.utility_gui.charts._2075 import TwoDChartDefinition
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility_gui.charts._2060": ["BubbleChartDefinition"],
        "_private.utility_gui.charts._2061": ["ConstantLine"],
        "_private.utility_gui.charts._2062": ["CustomLineChart"],
        "_private.utility_gui.charts._2063": ["CustomTableAndChart"],
        "_private.utility_gui.charts._2064": ["LegacyChartMathChartDefinition"],
        "_private.utility_gui.charts._2065": ["MatrixVisualisationDefinition"],
        "_private.utility_gui.charts._2066": ["ModeConstantLine"],
        "_private.utility_gui.charts._2067": ["NDChartDefinition"],
        "_private.utility_gui.charts._2068": ["ParallelCoordinatesChartDefinition"],
        "_private.utility_gui.charts._2069": ["PointsForSurface"],
        "_private.utility_gui.charts._2070": ["ScatterChartDefinition"],
        "_private.utility_gui.charts._2071": ["Series2D"],
        "_private.utility_gui.charts._2072": ["SMTAxis"],
        "_private.utility_gui.charts._2073": ["ThreeDChartDefinition"],
        "_private.utility_gui.charts._2074": ["ThreeDVectorChartDefinition"],
        "_private.utility_gui.charts._2075": ["TwoDChartDefinition"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "BubbleChartDefinition",
    "ConstantLine",
    "CustomLineChart",
    "CustomTableAndChart",
    "LegacyChartMathChartDefinition",
    "MatrixVisualisationDefinition",
    "ModeConstantLine",
    "NDChartDefinition",
    "ParallelCoordinatesChartDefinition",
    "PointsForSurface",
    "ScatterChartDefinition",
    "Series2D",
    "SMTAxis",
    "ThreeDChartDefinition",
    "ThreeDVectorChartDefinition",
    "TwoDChartDefinition",
)
