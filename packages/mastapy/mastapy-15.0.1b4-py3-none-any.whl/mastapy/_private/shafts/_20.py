"""ShaftDamageResultsTableAndChart"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
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

_SHAFT_DAMAGE_RESULTS_TABLE_AND_CHART = python_net_import(
    "SMT.MastaAPI.Shafts", "ShaftDamageResultsTableAndChart"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility.enums import _2023
    from mastapy._private.utility.report import _1963, _1969, _1970, _1971

    Self = TypeVar("Self", bound="ShaftDamageResultsTableAndChart")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ShaftDamageResultsTableAndChart._Cast_ShaftDamageResultsTableAndChart",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ShaftDamageResultsTableAndChart",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ShaftDamageResultsTableAndChart:
    """Special nested class for casting ShaftDamageResultsTableAndChart to subclasses."""

    __parent__: "ShaftDamageResultsTableAndChart"

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
    def shaft_damage_results_table_and_chart(
        self: "CastSelf",
    ) -> "ShaftDamageResultsTableAndChart":
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
class ShaftDamageResultsTableAndChart(_1956.CustomReportChart):
    """ShaftDamageResultsTableAndChart

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SHAFT_DAMAGE_RESULTS_TABLE_AND_CHART

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def display(self: "Self") -> "_2023.TableAndChartOptions":
        """mastapy.utility.enums.TableAndChartOptions"""
        temp = pythonnet_property_get(self.wrapped, "Display")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Utility.Enums.TableAndChartOptions"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.utility.enums._2023", "TableAndChartOptions"
        )(value)

    @display.setter
    @exception_bridge
    @enforce_parameter_types
    def display(self: "Self", value: "_2023.TableAndChartOptions") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Utility.Enums.TableAndChartOptions"
        )
        pythonnet_property_set(self.wrapped, "Display", value)

    @property
    def cast_to(self: "Self") -> "_Cast_ShaftDamageResultsTableAndChart":
        """Cast to another type.

        Returns:
            _Cast_ShaftDamageResultsTableAndChart
        """
        return _Cast_ShaftDamageResultsTableAndChart(self)
