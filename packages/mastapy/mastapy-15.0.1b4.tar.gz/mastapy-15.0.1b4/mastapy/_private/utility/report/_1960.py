"""CustomReportDefinitionItem"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.utility.report import _1971

_CUSTOM_REPORT_DEFINITION_ITEM = python_net_import(
    "SMT.MastaAPI.Utility.Report", "CustomReportDefinitionItem"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results import _2158
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4658,
    )
    from mastapy._private.utility.report import (
        _1942,
        _1950,
        _1951,
        _1952,
        _1953,
        _1962,
        _1963,
        _1974,
        _1977,
        _1979,
    )

    Self = TypeVar("Self", bound="CustomReportDefinitionItem")
    CastSelf = TypeVar(
        "CastSelf", bound="CustomReportDefinitionItem._Cast_CustomReportDefinitionItem"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CustomReportDefinitionItem",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CustomReportDefinitionItem:
    """Special nested class for casting CustomReportDefinitionItem to subclasses."""

    __parent__: "CustomReportDefinitionItem"

    @property
    def custom_report_nameable_item(
        self: "CastSelf",
    ) -> "_1971.CustomReportNameableItem":
        return self.__parent__._cast(_1971.CustomReportNameableItem)

    @property
    def custom_report_item(self: "CastSelf") -> "_1963.CustomReportItem":
        from mastapy._private.utility.report import _1963

        return self.__parent__._cast(_1963.CustomReportItem)

    @property
    def ad_hoc_custom_table(self: "CastSelf") -> "_1942.AdHocCustomTable":
        from mastapy._private.utility.report import _1942

        return self.__parent__._cast(_1942.AdHocCustomTable)

    @property
    def custom_chart(self: "CastSelf") -> "_1950.CustomChart":
        from mastapy._private.utility.report import _1950

        return self.__parent__._cast(_1950.CustomChart)

    @property
    def custom_drawing(self: "CastSelf") -> "_1951.CustomDrawing":
        from mastapy._private.utility.report import _1951

        return self.__parent__._cast(_1951.CustomDrawing)

    @property
    def custom_graphic(self: "CastSelf") -> "_1952.CustomGraphic":
        from mastapy._private.utility.report import _1952

        return self.__parent__._cast(_1952.CustomGraphic)

    @property
    def custom_image(self: "CastSelf") -> "_1953.CustomImage":
        from mastapy._private.utility.report import _1953

        return self.__parent__._cast(_1953.CustomImage)

    @property
    def custom_report_html_item(self: "CastSelf") -> "_1962.CustomReportHtmlItem":
        from mastapy._private.utility.report import _1962

        return self.__parent__._cast(_1962.CustomReportHtmlItem)

    @property
    def custom_report_status_item(self: "CastSelf") -> "_1974.CustomReportStatusItem":
        from mastapy._private.utility.report import _1974

        return self.__parent__._cast(_1974.CustomReportStatusItem)

    @property
    def custom_report_text(self: "CastSelf") -> "_1977.CustomReportText":
        from mastapy._private.utility.report import _1977

        return self.__parent__._cast(_1977.CustomReportText)

    @property
    def custom_sub_report(self: "CastSelf") -> "_1979.CustomSubReport":
        from mastapy._private.utility.report import _1979

        return self.__parent__._cast(_1979.CustomSubReport)

    @property
    def loaded_bearing_chart_reporter(
        self: "CastSelf",
    ) -> "_2158.LoadedBearingChartReporter":
        from mastapy._private.bearings.bearing_results import _2158

        return self.__parent__._cast(_2158.LoadedBearingChartReporter)

    @property
    def parametric_study_histogram(
        self: "CastSelf",
    ) -> "_4658.ParametricStudyHistogram":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4658,
        )

        return self.__parent__._cast(_4658.ParametricStudyHistogram)

    @property
    def custom_report_definition_item(self: "CastSelf") -> "CustomReportDefinitionItem":
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
class CustomReportDefinitionItem(_1971.CustomReportNameableItem):
    """CustomReportDefinitionItem

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CUSTOM_REPORT_DEFINITION_ITEM

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CustomReportDefinitionItem":
        """Cast to another type.

        Returns:
            _Cast_CustomReportDefinitionItem
        """
        return _Cast_CustomReportDefinitionItem(self)
