"""CustomImage"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.utility.report import _1952

_CUSTOM_IMAGE = python_net_import("SMT.MastaAPI.Utility.Report", "CustomImage")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results import _2158
    from mastapy._private.utility.report import _1960, _1963, _1971

    Self = TypeVar("Self", bound="CustomImage")
    CastSelf = TypeVar("CastSelf", bound="CustomImage._Cast_CustomImage")


__docformat__ = "restructuredtext en"
__all__ = ("CustomImage",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CustomImage:
    """Special nested class for casting CustomImage to subclasses."""

    __parent__: "CustomImage"

    @property
    def custom_graphic(self: "CastSelf") -> "_1952.CustomGraphic":
        return self.__parent__._cast(_1952.CustomGraphic)

    @property
    def custom_report_definition_item(
        self: "CastSelf",
    ) -> "_1960.CustomReportDefinitionItem":
        from mastapy._private.utility.report import _1960

        return self.__parent__._cast(_1960.CustomReportDefinitionItem)

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
    def loaded_bearing_chart_reporter(
        self: "CastSelf",
    ) -> "_2158.LoadedBearingChartReporter":
        from mastapy._private.bearings.bearing_results import _2158

        return self.__parent__._cast(_2158.LoadedBearingChartReporter)

    @property
    def custom_image(self: "CastSelf") -> "CustomImage":
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
class CustomImage(_1952.CustomGraphic):
    """CustomImage

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CUSTOM_IMAGE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CustomImage":
        """Cast to another type.

        Returns:
            _Cast_CustomImage
        """
        return _Cast_CustomImage(self)
