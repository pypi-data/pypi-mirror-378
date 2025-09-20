"""ParallelCoordinatesChartDefinition"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.utility_gui.charts import _2075

_PARALLEL_COORDINATES_CHART_DEFINITION = python_net_import(
    "SMT.MastaAPI.UtilityGUI.Charts", "ParallelCoordinatesChartDefinition"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility.report import _1948
    from mastapy._private.utility_gui.charts import _2067

    Self = TypeVar("Self", bound="ParallelCoordinatesChartDefinition")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ParallelCoordinatesChartDefinition._Cast_ParallelCoordinatesChartDefinition",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ParallelCoordinatesChartDefinition",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ParallelCoordinatesChartDefinition:
    """Special nested class for casting ParallelCoordinatesChartDefinition to subclasses."""

    __parent__: "ParallelCoordinatesChartDefinition"

    @property
    def two_d_chart_definition(self: "CastSelf") -> "_2075.TwoDChartDefinition":
        return self.__parent__._cast(_2075.TwoDChartDefinition)

    @property
    def nd_chart_definition(self: "CastSelf") -> "_2067.NDChartDefinition":
        from mastapy._private.utility_gui.charts import _2067

        return self.__parent__._cast(_2067.NDChartDefinition)

    @property
    def chart_definition(self: "CastSelf") -> "_1948.ChartDefinition":
        from mastapy._private.utility.report import _1948

        return self.__parent__._cast(_1948.ChartDefinition)

    @property
    def parallel_coordinates_chart_definition(
        self: "CastSelf",
    ) -> "ParallelCoordinatesChartDefinition":
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
class ParallelCoordinatesChartDefinition(_2075.TwoDChartDefinition):
    """ParallelCoordinatesChartDefinition

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PARALLEL_COORDINATES_CHART_DEFINITION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ParallelCoordinatesChartDefinition":
        """Cast to another type.

        Returns:
            _Cast_ParallelCoordinatesChartDefinition
        """
        return _Cast_ParallelCoordinatesChartDefinition(self)
