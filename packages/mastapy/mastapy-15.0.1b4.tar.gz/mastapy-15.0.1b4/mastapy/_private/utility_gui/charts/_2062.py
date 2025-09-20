"""CustomLineChart"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
)
from mastapy._private.utility.report import _1956

_CUSTOM_LINE_CHART = python_net_import(
    "SMT.MastaAPI.UtilityGUI.Charts", "CustomLineChart"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility.report import _1963, _1969, _1970, _1971

    Self = TypeVar("Self", bound="CustomLineChart")
    CastSelf = TypeVar("CastSelf", bound="CustomLineChart._Cast_CustomLineChart")


__docformat__ = "restructuredtext en"
__all__ = ("CustomLineChart",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CustomLineChart:
    """Special nested class for casting CustomLineChart to subclasses."""

    __parent__: "CustomLineChart"

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
    def custom_line_chart(self: "CastSelf") -> "CustomLineChart":
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
class CustomLineChart(_1956.CustomReportChart):
    """CustomLineChart

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CUSTOM_LINE_CHART

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @exception_bridge
    def x_values(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "XValues")

    @exception_bridge
    def y_values(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "YValues")

    @property
    def cast_to(self: "Self") -> "_Cast_CustomLineChart":
        """Cast to another type.

        Returns:
            _Cast_CustomLineChart
        """
        return _Cast_CustomLineChart(self)
