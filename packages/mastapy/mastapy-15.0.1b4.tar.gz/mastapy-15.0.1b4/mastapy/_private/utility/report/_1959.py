"""CustomReportColumns"""

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
from mastapy._private.utility.report import _1958, _1965

_CUSTOM_REPORT_COLUMNS = python_net_import(
    "SMT.MastaAPI.Utility.Report", "CustomReportColumns"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility.report import _1963, _1966

    Self = TypeVar("Self", bound="CustomReportColumns")
    CastSelf = TypeVar(
        "CastSelf", bound="CustomReportColumns._Cast_CustomReportColumns"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CustomReportColumns",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CustomReportColumns:
    """Special nested class for casting CustomReportColumns to subclasses."""

    __parent__: "CustomReportColumns"

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
    def custom_report_columns(self: "CastSelf") -> "CustomReportColumns":
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
class CustomReportColumns(
    _1965.CustomReportItemContainerCollection[_1958.CustomReportColumn]
):
    """CustomReportColumns

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CUSTOM_REPORT_COLUMNS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def number_of_columns(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "NumberOfColumns")

        if temp is None:
            return 0

        return temp

    @number_of_columns.setter
    @exception_bridge
    @enforce_parameter_types
    def number_of_columns(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "NumberOfColumns", int(value) if value is not None else 0
        )

    @property
    @exception_bridge
    def show_adjustable_column_divider(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "ShowAdjustableColumnDivider")

        if temp is None:
            return False

        return temp

    @show_adjustable_column_divider.setter
    @exception_bridge
    @enforce_parameter_types
    def show_adjustable_column_divider(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "ShowAdjustableColumnDivider",
            bool(value) if value is not None else False,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_CustomReportColumns":
        """Cast to another type.

        Returns:
            _Cast_CustomReportColumns
        """
        return _Cast_CustomReportColumns(self)
