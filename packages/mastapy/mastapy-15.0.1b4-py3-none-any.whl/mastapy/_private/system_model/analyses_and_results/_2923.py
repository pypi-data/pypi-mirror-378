"""CompoundStabilityAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.analyses_and_results import _2893

_COMPOUND_STABILITY_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults", "CompoundStabilityAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private import _7900

    Self = TypeVar("Self", bound="CompoundStabilityAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="CompoundStabilityAnalysis._Cast_CompoundStabilityAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("CompoundStabilityAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CompoundStabilityAnalysis:
    """Special nested class for casting CompoundStabilityAnalysis to subclasses."""

    __parent__: "CompoundStabilityAnalysis"

    @property
    def compound_analysis(self: "CastSelf") -> "_2893.CompoundAnalysis":
        return self.__parent__._cast(_2893.CompoundAnalysis)

    @property
    def marshal_by_ref_object_permanent(
        self: "CastSelf",
    ) -> "_7900.MarshalByRefObjectPermanent":
        from mastapy._private import _7900

        return self.__parent__._cast(_7900.MarshalByRefObjectPermanent)

    @property
    def compound_stability_analysis(self: "CastSelf") -> "CompoundStabilityAnalysis":
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
class CompoundStabilityAnalysis(_2893.CompoundAnalysis):
    """CompoundStabilityAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COMPOUND_STABILITY_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CompoundStabilityAnalysis":
        """Cast to another type.

        Returns:
            _Cast_CompoundStabilityAnalysis
        """
        return _Cast_CompoundStabilityAnalysis(self)
