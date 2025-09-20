"""LoadedRollerElementChartReporter"""

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
from mastapy._private.utility.report import _1956

_LOADED_ROLLER_ELEMENT_CHART_REPORTER = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults", "LoadedRollerElementChartReporter"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility.report import _1963, _1969, _1970, _1971

    Self = TypeVar("Self", bound="LoadedRollerElementChartReporter")
    CastSelf = TypeVar(
        "CastSelf",
        bound="LoadedRollerElementChartReporter._Cast_LoadedRollerElementChartReporter",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedRollerElementChartReporter",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedRollerElementChartReporter:
    """Special nested class for casting LoadedRollerElementChartReporter to subclasses."""

    __parent__: "LoadedRollerElementChartReporter"

    @property
    def custom_report_chart(self: "CastSelf") -> "_1956.CustomReportChart":
        return self.__parent__._cast(_1956.CustomReportChart)

    @property
    def custom_report_multi_property_item(
        self: "CastSelf",
    ) -> "_1969.CustomReportMultiPropertyItem":
        pass

        from mastapy._private.utility.report import _1969

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
    def loaded_roller_element_chart_reporter(
        self: "CastSelf",
    ) -> "LoadedRollerElementChartReporter":
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
class LoadedRollerElementChartReporter(_1956.CustomReportChart):
    """LoadedRollerElementChartReporter

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_ROLLER_ELEMENT_CHART_REPORTER

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def only_show_roller_with_highest_load(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "OnlyShowRollerWithHighestLoad")

        if temp is None:
            return False

        return temp

    @only_show_roller_with_highest_load.setter
    @exception_bridge
    @enforce_parameter_types
    def only_show_roller_with_highest_load(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "OnlyShowRollerWithHighestLoad",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def start_y_axis_at_zero(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "StartYAxisAtZero")

        if temp is None:
            return False

        return temp

    @start_y_axis_at_zero.setter
    @exception_bridge
    @enforce_parameter_types
    def start_y_axis_at_zero(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "StartYAxisAtZero",
            bool(value) if value is not None else False,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedRollerElementChartReporter":
        """Cast to another type.

        Returns:
            _Cast_LoadedRollerElementChartReporter
        """
        return _Cast_LoadedRollerElementChartReporter(self)
