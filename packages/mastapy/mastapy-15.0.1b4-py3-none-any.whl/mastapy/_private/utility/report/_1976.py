"""CustomReportTabs"""

from __future__ import annotations

from enum import Enum
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
from mastapy._private.utility.report import _1965, _1975

_CUSTOM_REPORT_TABS = python_net_import(
    "SMT.MastaAPI.Utility.Report", "CustomReportTabs"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility.report import _1963, _1966

    Self = TypeVar("Self", bound="CustomReportTabs")
    CastSelf = TypeVar("CastSelf", bound="CustomReportTabs._Cast_CustomReportTabs")


__docformat__ = "restructuredtext en"
__all__ = ("CustomReportTabs",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CustomReportTabs:
    """Special nested class for casting CustomReportTabs to subclasses."""

    __parent__: "CustomReportTabs"

    @property
    def custom_report_item_container_collection(
        self: "CastSelf",
    ) -> "_1965.CustomReportItemContainerCollection":
        return self.__parent__._cast(_1965.CustomReportItemContainerCollection)

    @property
    def custom_report_item_container_collection_base(
        self: "CastSelf",
    ) -> "_1966.CustomReportItemContainerCollectionBase":
        from mastapy._private.utility.report import _1966

        return self.__parent__._cast(_1966.CustomReportItemContainerCollectionBase)

    @property
    def custom_report_item(self: "CastSelf") -> "_1963.CustomReportItem":
        from mastapy._private.utility.report import _1963

        return self.__parent__._cast(_1963.CustomReportItem)

    @property
    def custom_report_tabs(self: "CastSelf") -> "CustomReportTabs":
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
class CustomReportTabs(
    _1965.CustomReportItemContainerCollection[_1975.CustomReportTab]
):
    """CustomReportTabs

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CUSTOM_REPORT_TABS

    class ReportLayoutOrientation(Enum):
        """ReportLayoutOrientation is a nested enum."""

        @classmethod
        def type_(cls) -> "Type":
            return _CUSTOM_REPORT_TABS.ReportLayoutOrientation

        HORIZONTAL = 0
        VERTICAL = 1

    def __enum_setattr(self: "Self", attr: str, value: "Any") -> None:
        raise AttributeError("Cannot set the attributes of an Enum.") from None

    def __enum_delattr(self: "Self", attr: str) -> None:
        raise AttributeError("Cannot delete the attributes of an Enum.") from None

    ReportLayoutOrientation.__setattr__ = __enum_setattr
    ReportLayoutOrientation.__delattr__ = __enum_delattr

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def is_main_report_item(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "IsMainReportItem")

        if temp is None:
            return False

        return temp

    @is_main_report_item.setter
    @exception_bridge
    @enforce_parameter_types
    def is_main_report_item(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "IsMainReportItem",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def number_of_tabs(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfTabs")

        if temp is None:
            return 0

        return temp

    @number_of_tabs.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_tabs(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "NumberOfTabs", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def scroll_content(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "ScrollContent")

        if temp is None:
            return False

        return temp

    @scroll_content.setter
    @exception_bridge
    @enforce_parameter_types
    def scroll_content(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped, "ScrollContent", bool(value) if value is not None else False
        )

    @property
    def cast_to(self: "Self") -> "_Cast_CustomReportTabs":
        """Cast to another type.

        Returns:
            _Cast_CustomReportTabs
        """
        return _Cast_CustomReportTabs(self)
