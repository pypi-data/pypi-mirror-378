"""UnbalancedMassExcitationDetail"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.analyses_and_results.harmonic_analyses import _6110

_UNBALANCED_MASS_EXCITATION_DETAIL = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses",
    "UnbalancedMassExcitationDetail",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _5974,
        _6093,
    )

    Self = TypeVar("Self", bound="UnbalancedMassExcitationDetail")
    CastSelf = TypeVar(
        "CastSelf",
        bound="UnbalancedMassExcitationDetail._Cast_UnbalancedMassExcitationDetail",
    )


__docformat__ = "restructuredtext en"
__all__ = ("UnbalancedMassExcitationDetail",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_UnbalancedMassExcitationDetail:
    """Special nested class for casting UnbalancedMassExcitationDetail to subclasses."""

    __parent__: "UnbalancedMassExcitationDetail"

    @property
    def single_node_periodic_excitation_with_reference_shaft(
        self: "CastSelf",
    ) -> "_6110.SingleNodePeriodicExcitationWithReferenceShaft":
        return self.__parent__._cast(
            _6110.SingleNodePeriodicExcitationWithReferenceShaft
        )

    @property
    def periodic_excitation_with_reference_shaft(
        self: "CastSelf",
    ) -> "_6093.PeriodicExcitationWithReferenceShaft":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6093,
        )

        return self.__parent__._cast(_6093.PeriodicExcitationWithReferenceShaft)

    @property
    def abstract_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_5974.AbstractPeriodicExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _5974,
        )

        return self.__parent__._cast(_5974.AbstractPeriodicExcitationDetail)

    @property
    def unbalanced_mass_excitation_detail(
        self: "CastSelf",
    ) -> "UnbalancedMassExcitationDetail":
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
class UnbalancedMassExcitationDetail(
    _6110.SingleNodePeriodicExcitationWithReferenceShaft
):
    """UnbalancedMassExcitationDetail

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _UNBALANCED_MASS_EXCITATION_DETAIL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_UnbalancedMassExcitationDetail":
        """Cast to another type.

        Returns:
            _Cast_UnbalancedMassExcitationDetail
        """
        return _Cast_UnbalancedMassExcitationDetail(self)
