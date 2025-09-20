"""BearingLoadCaseResultsForPST"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.bearings import _2083

_BEARING_LOAD_CASE_RESULTS_FOR_PST = python_net_import(
    "SMT.MastaAPI.Bearings", "BearingLoadCaseResultsForPST"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="BearingLoadCaseResultsForPST")
    CastSelf = TypeVar(
        "CastSelf",
        bound="BearingLoadCaseResultsForPST._Cast_BearingLoadCaseResultsForPST",
    )


__docformat__ = "restructuredtext en"
__all__ = ("BearingLoadCaseResultsForPST",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BearingLoadCaseResultsForPST:
    """Special nested class for casting BearingLoadCaseResultsForPST to subclasses."""

    __parent__: "BearingLoadCaseResultsForPST"

    @property
    def bearing_load_case_results_lightweight(
        self: "CastSelf",
    ) -> "_2083.BearingLoadCaseResultsLightweight":
        return self.__parent__._cast(_2083.BearingLoadCaseResultsLightweight)

    @property
    def bearing_load_case_results_for_pst(
        self: "CastSelf",
    ) -> "BearingLoadCaseResultsForPST":
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
class BearingLoadCaseResultsForPST(_2083.BearingLoadCaseResultsLightweight):
    """BearingLoadCaseResultsForPST

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEARING_LOAD_CASE_RESULTS_FOR_PST

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def relative_misalignment(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RelativeMisalignment")

        if temp is None:
            return 0.0

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_BearingLoadCaseResultsForPST":
        """Cast to another type.

        Returns:
            _Cast_BearingLoadCaseResultsForPST
        """
        return _Cast_BearingLoadCaseResultsForPST(self)
