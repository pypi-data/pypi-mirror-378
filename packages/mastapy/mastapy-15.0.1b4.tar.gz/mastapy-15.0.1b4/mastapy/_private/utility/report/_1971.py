"""CustomReportNameableItem"""

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
from mastapy._private.utility.report import _1963

_CUSTOM_REPORT_NAMEABLE_ITEM = python_net_import(
    "SMT.MastaAPI.Utility.Report", "CustomReportNameableItem"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results import _2157, _2158, _2161, _2169
    from mastapy._private.gears.gear_designs.cylindrical import _1145
    from mastapy._private.shafts import _20
    from mastapy._private.system_model.analyses_and_results.modal_analyses.reporting import (
        _4995,
        _4999,
    )
    from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
        _4658,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections.reporting import (
        _3097,
    )
    from mastapy._private.utility.report import (
        _1942,
        _1950,
        _1951,
        _1952,
        _1953,
        _1955,
        _1956,
        _1960,
        _1962,
        _1969,
        _1970,
        _1972,
        _1974,
        _1977,
        _1979,
        _1980,
        _1982,
    )
    from mastapy._private.utility_gui.charts import _2062, _2063

    Self = TypeVar("Self", bound="CustomReportNameableItem")
    CastSelf = TypeVar(
        "CastSelf", bound="CustomReportNameableItem._Cast_CustomReportNameableItem"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CustomReportNameableItem",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CustomReportNameableItem:
    """Special nested class for casting CustomReportNameableItem to subclasses."""

    __parent__: "CustomReportNameableItem"

    @property
    def custom_report_item(self: "CastSelf") -> "_1963.CustomReportItem":
        return self.__parent__._cast(_1963.CustomReportItem)

    @property
    def shaft_damage_results_table_and_chart(
        self: "CastSelf",
    ) -> "_20.ShaftDamageResultsTableAndChart":
        from mastapy._private.shafts import _20

        return self.__parent__._cast(_20.ShaftDamageResultsTableAndChart)

    @property
    def cylindrical_gear_table_with_mg_charts(
        self: "CastSelf",
    ) -> "_1145.CylindricalGearTableWithMGCharts":
        from mastapy._private.gears.gear_designs.cylindrical import _1145

        return self.__parent__._cast(_1145.CylindricalGearTableWithMGCharts)

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
    def custom_report_cad_drawing(self: "CastSelf") -> "_1955.CustomReportCadDrawing":
        from mastapy._private.utility.report import _1955

        return self.__parent__._cast(_1955.CustomReportCadDrawing)

    @property
    def custom_report_chart(self: "CastSelf") -> "_1956.CustomReportChart":
        from mastapy._private.utility.report import _1956

        return self.__parent__._cast(_1956.CustomReportChart)

    @property
    def custom_report_definition_item(
        self: "CastSelf",
    ) -> "_1960.CustomReportDefinitionItem":
        from mastapy._private.utility.report import _1960

        return self.__parent__._cast(_1960.CustomReportDefinitionItem)

    @property
    def custom_report_html_item(self: "CastSelf") -> "_1962.CustomReportHtmlItem":
        from mastapy._private.utility.report import _1962

        return self.__parent__._cast(_1962.CustomReportHtmlItem)

    @property
    def custom_report_multi_property_item(
        self: "CastSelf",
    ) -> "_1969.CustomReportMultiPropertyItem":
        from mastapy._private.utility.report import _1969

        return self.__parent__._cast(_1969.CustomReportMultiPropertyItem)

    @property
    def custom_report_multi_property_item_base(
        self: "CastSelf",
    ) -> "_1970.CustomReportMultiPropertyItemBase":
        from mastapy._private.utility.report import _1970

        return self.__parent__._cast(_1970.CustomReportMultiPropertyItemBase)

    @property
    def custom_report_named_item(self: "CastSelf") -> "_1972.CustomReportNamedItem":
        from mastapy._private.utility.report import _1972

        return self.__parent__._cast(_1972.CustomReportNamedItem)

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
    def custom_table(self: "CastSelf") -> "_1980.CustomTable":
        from mastapy._private.utility.report import _1980

        return self.__parent__._cast(_1980.CustomTable)

    @property
    def dynamic_custom_report_item(self: "CastSelf") -> "_1982.DynamicCustomReportItem":
        from mastapy._private.utility.report import _1982

        return self.__parent__._cast(_1982.DynamicCustomReportItem)

    @property
    def custom_line_chart(self: "CastSelf") -> "_2062.CustomLineChart":
        from mastapy._private.utility_gui.charts import _2062

        return self.__parent__._cast(_2062.CustomLineChart)

    @property
    def custom_table_and_chart(self: "CastSelf") -> "_2063.CustomTableAndChart":
        from mastapy._private.utility_gui.charts import _2063

        return self.__parent__._cast(_2063.CustomTableAndChart)

    @property
    def loaded_ball_element_chart_reporter(
        self: "CastSelf",
    ) -> "_2157.LoadedBallElementChartReporter":
        from mastapy._private.bearings.bearing_results import _2157

        return self.__parent__._cast(_2157.LoadedBallElementChartReporter)

    @property
    def loaded_bearing_chart_reporter(
        self: "CastSelf",
    ) -> "_2158.LoadedBearingChartReporter":
        from mastapy._private.bearings.bearing_results import _2158

        return self.__parent__._cast(_2158.LoadedBearingChartReporter)

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
    def parametric_study_histogram(
        self: "CastSelf",
    ) -> "_4658.ParametricStudyHistogram":
        from mastapy._private.system_model.analyses_and_results.parametric_study_tools import (
            _4658,
        )

        return self.__parent__._cast(_4658.ParametricStudyHistogram)

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
    def custom_report_nameable_item(self: "CastSelf") -> "CustomReportNameableItem":
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
class CustomReportNameableItem(_1963.CustomReportItem):
    """CustomReportNameableItem

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CUSTOM_REPORT_NAMEABLE_ITEM

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @name.setter
    @exception_bridge
    @enforce_parameter_types
    def name(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Name", str(value) if value is not None else ""
        )

    @property
    @exception_bridge
    def x_position_for_cad(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "XPositionForCAD")

        if temp is None:
            return 0.0

        return temp

    @x_position_for_cad.setter
    @exception_bridge
    @enforce_parameter_types
    def x_position_for_cad(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "XPositionForCAD", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def y_position_for_cad(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "YPositionForCAD")

        if temp is None:
            return 0.0

        return temp

    @y_position_for_cad.setter
    @exception_bridge
    @enforce_parameter_types
    def y_position_for_cad(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "YPositionForCAD", float(value) if value is not None else 0.0
        )

    @property
    def cast_to(self: "Self") -> "_Cast_CustomReportNameableItem":
        """Cast to another type.

        Returns:
            _Cast_CustomReportNameableItem
        """
        return _Cast_CustomReportNameableItem(self)
