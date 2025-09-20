"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.utility.report._1942 import AdHocCustomTable
    from mastapy._private.utility.report._1943 import AxisSettings
    from mastapy._private.utility.report._1944 import BlankRow
    from mastapy._private.utility.report._1945 import CadPageOrientation
    from mastapy._private.utility.report._1946 import CadPageSize
    from mastapy._private.utility.report._1947 import CadTableBorderType
    from mastapy._private.utility.report._1948 import ChartDefinition
    from mastapy._private.utility.report._1949 import SMTChartPointShape
    from mastapy._private.utility.report._1950 import CustomChart
    from mastapy._private.utility.report._1951 import CustomDrawing
    from mastapy._private.utility.report._1952 import CustomGraphic
    from mastapy._private.utility.report._1953 import CustomImage
    from mastapy._private.utility.report._1954 import CustomReport
    from mastapy._private.utility.report._1955 import CustomReportCadDrawing
    from mastapy._private.utility.report._1956 import CustomReportChart
    from mastapy._private.utility.report._1957 import CustomReportChartItem
    from mastapy._private.utility.report._1958 import CustomReportColumn
    from mastapy._private.utility.report._1959 import CustomReportColumns
    from mastapy._private.utility.report._1960 import CustomReportDefinitionItem
    from mastapy._private.utility.report._1961 import CustomReportHorizontalLine
    from mastapy._private.utility.report._1962 import CustomReportHtmlItem
    from mastapy._private.utility.report._1963 import CustomReportItem
    from mastapy._private.utility.report._1964 import CustomReportItemContainer
    from mastapy._private.utility.report._1965 import (
        CustomReportItemContainerCollection,
    )
    from mastapy._private.utility.report._1966 import (
        CustomReportItemContainerCollectionBase,
    )
    from mastapy._private.utility.report._1967 import (
        CustomReportItemContainerCollectionItem,
    )
    from mastapy._private.utility.report._1968 import CustomReportKey
    from mastapy._private.utility.report._1969 import CustomReportMultiPropertyItem
    from mastapy._private.utility.report._1970 import CustomReportMultiPropertyItemBase
    from mastapy._private.utility.report._1971 import CustomReportNameableItem
    from mastapy._private.utility.report._1972 import CustomReportNamedItem
    from mastapy._private.utility.report._1973 import CustomReportPropertyItem
    from mastapy._private.utility.report._1974 import CustomReportStatusItem
    from mastapy._private.utility.report._1975 import CustomReportTab
    from mastapy._private.utility.report._1976 import CustomReportTabs
    from mastapy._private.utility.report._1977 import CustomReportText
    from mastapy._private.utility.report._1978 import CustomRow
    from mastapy._private.utility.report._1979 import CustomSubReport
    from mastapy._private.utility.report._1980 import CustomTable
    from mastapy._private.utility.report._1981 import DefinitionBooleanCheckOptions
    from mastapy._private.utility.report._1982 import DynamicCustomReportItem
    from mastapy._private.utility.report._1983 import FontStyle
    from mastapy._private.utility.report._1984 import FontWeight
    from mastapy._private.utility.report._1985 import HeadingSize
    from mastapy._private.utility.report._1986 import SimpleChartDefinition
    from mastapy._private.utility.report._1987 import UserTextRow
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.utility.report._1942": ["AdHocCustomTable"],
        "_private.utility.report._1943": ["AxisSettings"],
        "_private.utility.report._1944": ["BlankRow"],
        "_private.utility.report._1945": ["CadPageOrientation"],
        "_private.utility.report._1946": ["CadPageSize"],
        "_private.utility.report._1947": ["CadTableBorderType"],
        "_private.utility.report._1948": ["ChartDefinition"],
        "_private.utility.report._1949": ["SMTChartPointShape"],
        "_private.utility.report._1950": ["CustomChart"],
        "_private.utility.report._1951": ["CustomDrawing"],
        "_private.utility.report._1952": ["CustomGraphic"],
        "_private.utility.report._1953": ["CustomImage"],
        "_private.utility.report._1954": ["CustomReport"],
        "_private.utility.report._1955": ["CustomReportCadDrawing"],
        "_private.utility.report._1956": ["CustomReportChart"],
        "_private.utility.report._1957": ["CustomReportChartItem"],
        "_private.utility.report._1958": ["CustomReportColumn"],
        "_private.utility.report._1959": ["CustomReportColumns"],
        "_private.utility.report._1960": ["CustomReportDefinitionItem"],
        "_private.utility.report._1961": ["CustomReportHorizontalLine"],
        "_private.utility.report._1962": ["CustomReportHtmlItem"],
        "_private.utility.report._1963": ["CustomReportItem"],
        "_private.utility.report._1964": ["CustomReportItemContainer"],
        "_private.utility.report._1965": ["CustomReportItemContainerCollection"],
        "_private.utility.report._1966": ["CustomReportItemContainerCollectionBase"],
        "_private.utility.report._1967": ["CustomReportItemContainerCollectionItem"],
        "_private.utility.report._1968": ["CustomReportKey"],
        "_private.utility.report._1969": ["CustomReportMultiPropertyItem"],
        "_private.utility.report._1970": ["CustomReportMultiPropertyItemBase"],
        "_private.utility.report._1971": ["CustomReportNameableItem"],
        "_private.utility.report._1972": ["CustomReportNamedItem"],
        "_private.utility.report._1973": ["CustomReportPropertyItem"],
        "_private.utility.report._1974": ["CustomReportStatusItem"],
        "_private.utility.report._1975": ["CustomReportTab"],
        "_private.utility.report._1976": ["CustomReportTabs"],
        "_private.utility.report._1977": ["CustomReportText"],
        "_private.utility.report._1978": ["CustomRow"],
        "_private.utility.report._1979": ["CustomSubReport"],
        "_private.utility.report._1980": ["CustomTable"],
        "_private.utility.report._1981": ["DefinitionBooleanCheckOptions"],
        "_private.utility.report._1982": ["DynamicCustomReportItem"],
        "_private.utility.report._1983": ["FontStyle"],
        "_private.utility.report._1984": ["FontWeight"],
        "_private.utility.report._1985": ["HeadingSize"],
        "_private.utility.report._1986": ["SimpleChartDefinition"],
        "_private.utility.report._1987": ["UserTextRow"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AdHocCustomTable",
    "AxisSettings",
    "BlankRow",
    "CadPageOrientation",
    "CadPageSize",
    "CadTableBorderType",
    "ChartDefinition",
    "SMTChartPointShape",
    "CustomChart",
    "CustomDrawing",
    "CustomGraphic",
    "CustomImage",
    "CustomReport",
    "CustomReportCadDrawing",
    "CustomReportChart",
    "CustomReportChartItem",
    "CustomReportColumn",
    "CustomReportColumns",
    "CustomReportDefinitionItem",
    "CustomReportHorizontalLine",
    "CustomReportHtmlItem",
    "CustomReportItem",
    "CustomReportItemContainer",
    "CustomReportItemContainerCollection",
    "CustomReportItemContainerCollectionBase",
    "CustomReportItemContainerCollectionItem",
    "CustomReportKey",
    "CustomReportMultiPropertyItem",
    "CustomReportMultiPropertyItemBase",
    "CustomReportNameableItem",
    "CustomReportNamedItem",
    "CustomReportPropertyItem",
    "CustomReportStatusItem",
    "CustomReportTab",
    "CustomReportTabs",
    "CustomReportText",
    "CustomRow",
    "CustomSubReport",
    "CustomTable",
    "DefinitionBooleanCheckOptions",
    "DynamicCustomReportItem",
    "FontStyle",
    "FontWeight",
    "HeadingSize",
    "SimpleChartDefinition",
    "UserTextRow",
)
