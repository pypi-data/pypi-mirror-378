"""SingleNodePeriodicExcitationWithReferenceShaft"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.analyses_and_results.harmonic_analyses import _6093

_SINGLE_NODE_PERIODIC_EXCITATION_WITH_REFERENCE_SHAFT = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses",
    "SingleNodePeriodicExcitationWithReferenceShaft",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _5974,
        _6055,
        _6136,
    )

    Self = TypeVar("Self", bound="SingleNodePeriodicExcitationWithReferenceShaft")
    CastSelf = TypeVar(
        "CastSelf",
        bound="SingleNodePeriodicExcitationWithReferenceShaft._Cast_SingleNodePeriodicExcitationWithReferenceShaft",
    )


__docformat__ = "restructuredtext en"
__all__ = ("SingleNodePeriodicExcitationWithReferenceShaft",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SingleNodePeriodicExcitationWithReferenceShaft:
    """Special nested class for casting SingleNodePeriodicExcitationWithReferenceShaft to subclasses."""

    __parent__: "SingleNodePeriodicExcitationWithReferenceShaft"

    @property
    def periodic_excitation_with_reference_shaft(
        self: "CastSelf",
    ) -> "_6093.PeriodicExcitationWithReferenceShaft":
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
    def general_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_6055.GeneralPeriodicExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6055,
        )

        return self.__parent__._cast(_6055.GeneralPeriodicExcitationDetail)

    @property
    def unbalanced_mass_excitation_detail(
        self: "CastSelf",
    ) -> "_6136.UnbalancedMassExcitationDetail":
        from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
            _6136,
        )

        return self.__parent__._cast(_6136.UnbalancedMassExcitationDetail)

    @property
    def single_node_periodic_excitation_with_reference_shaft(
        self: "CastSelf",
    ) -> "SingleNodePeriodicExcitationWithReferenceShaft":
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
class SingleNodePeriodicExcitationWithReferenceShaft(
    _6093.PeriodicExcitationWithReferenceShaft
):
    """SingleNodePeriodicExcitationWithReferenceShaft

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SINGLE_NODE_PERIODIC_EXCITATION_WITH_REFERENCE_SHAFT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_SingleNodePeriodicExcitationWithReferenceShaft":
        """Cast to another type.

        Returns:
            _Cast_SingleNodePeriodicExcitationWithReferenceShaft
        """
        return _Cast_SingleNodePeriodicExcitationWithReferenceShaft(self)
