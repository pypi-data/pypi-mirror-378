"""CustomReportChart"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.utility.report import _1957, _1969

_CUSTOM_REPORT_CHART = python_net_import(
    "SMT.MastaAPI.Utility.Report", "CustomReportChart"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results import _2157, _2161, _2169
    from mastapy._private.shafts import _20
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting import (
        _4995,
        _4999,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections.reporting import (
        _3097,
    )
    from mastapy._private.utility.report import _1963, _1970, _1971
    from mastapy._private.utility_gui.charts import _2062

    Self = TypeVar("Self", bound="CustomReportChart")
    CastSelf = TypeVar("CastSelf", bound="CustomReportChart._Cast_CustomReportChart")


__docformat__ = "restructuredtext en"
__all__ = ("CustomReportChart",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CustomReportChart:
    """Special nested class for casting CustomReportChart to subclasses."""

    __parent__: "CustomReportChart"

    @property
    def custom_report_multi_property_item(
        self: "CastSelf",
    ) -> "_1969.CustomReportMultiPropertyItem":
        return self.__parent__._cast(_1969.CustomReportMultiPropertyItem)

    @property
    def custom_report_multi_property_item_base(
        self: "CastSelf",
    ) -> "_1970.CustomReportMultiPropertyItemBase":
        from mastapy._private.utility.report import _1970

        return self.__parent__._cast(_1970.CustomReportMultiPropertyItemBase)

    @property
    def custom_report_nameable_item(
        self: "CastSelf",
    ) -> "_1971.CustomReportNameableItem":
        from mastapy._private.utility.report import _1971

        return self.__parent__._cast(_1971.CustomReportNameableItem)

    @property
    def custom_report_item(self: "CastSelf") -> "_1963.CustomReportItem":
        from mastapy._private.utility.report import _1963

        return self.__parent__._cast(_1963.CustomReportItem)

    @property
    def shaft_damage_results_table_and_chart(
        self: "CastSelf",
    ) -> "_20.ShaftDamageResultsTableAndChart":
        from mastapy._private.shafts import _20

        return self.__parent__._cast(_20.ShaftDamageResultsTableAndChart)

    @property
    def custom_line_chart(self: "CastSelf") -> "_2062.CustomLineChart":
        from mastapy._private.utility_gui.charts import _2062

        return self.__parent__._cast(_2062.CustomLineChart)

    @property
    def loaded_ball_element_chart_reporter(
        self: "CastSelf",
    ) -> "_2157.LoadedBallElementChartReporter":
        from mastapy._private.bearings.bearing_results import _2157

        return self.__parent__._cast(_2157.LoadedBallElementChartReporter)

    @property
    def loaded_bearing_temperature_chart(
        self: "CastSelf",
    ) -> "_2161.LoadedBearingTemperatureChart":
        from mastapy._private.bearings.bearing_results import _2161

        return self.__parent__._cast(_2161.LoadedBearingTemperatureChart)

    @property
    def loaded_roller_element_chart_reporter(
        self: "CastSelf",
    ) -> "_2169.LoadedRollerElementChartReporter":
        from mastapy._private.bearings.bearing_results import _2169

        return self.__parent__._cast(_2169.LoadedRollerElementChartReporter)

    @property
    def shaft_system_deflection_sections_report(
        self: "CastSelf",
    ) -> "_3097.ShaftSystemDeflectionSectionsReport":
        from mastapy._private.system_model.analyses_and_results.system_deflections.reporting import (
            _3097,
        )

        return self.__parent__._cast(_3097.ShaftSystemDeflectionSectionsReport)

    @property
    def campbell_diagram_report(self: "CastSelf") -> "_4995.CampbellDiagramReport":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting import (
            _4995,
        )

        return self.__parent__._cast(_4995.CampbellDiagramReport)

    @property
    def per_mode_results_report(self: "CastSelf") -> "_4999.PerModeResultsReport":
        from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting import (
            _4999,
        )

        return self.__parent__._cast(_4999.PerModeResultsReport)

    @property
    def custom_report_chart(self: "CastSelf") -> "CustomReportChart":
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
class CustomReportChart(
    _1969.CustomReportMultiPropertyItem[_1957.CustomReportChartItem]
):
    """CustomReportChart

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CUSTOM_REPORT_CHART

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def height(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "Height")

        if temp is None:
            return 0

        return temp

    @height.setter
    @exception_bridge
    @enforce_parameter_types
    def height(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "Height", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def width(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "Width")

        if temp is None:
            return 0

        return temp

    @width.setter
    @exception_bridge
    @enforce_parameter_types
    def width(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "Width", int(value) if value is not None else 0
        )

    @property
    def cast_to(self: "Self") -> "_Cast_CustomReportChart":
        """Cast to another type.

        Returns:
            _Cast_CustomReportChart
        """
        return _Cast_CustomReportChart(self)
