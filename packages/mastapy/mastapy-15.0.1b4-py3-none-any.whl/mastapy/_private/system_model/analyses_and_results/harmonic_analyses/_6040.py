"""ElectricMachineTorqueRipplePeriodicExcitationDetail"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.analyses_and_results.harmonic_analyses import _6029

_ELECTRIC_MACHINE_TORQUE_RIPPLE_PERIODIC_EXCITATION_DETAIL = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.HarmonicAnalyses",
    "ElectricMachineTorqueRipplePeriodicExcitationDetail",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results.harmonic_analyses import (
        _5974,
        _6093,
    )

    Self = TypeVar("Self", bound="ElectricMachineTorqueRipplePeriodicExcitationDetail")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ElectricMachineTorqueRipplePeriodicExcitationDetail._Cast_ElectricMachineTorqueRipplePeriodicExcitationDetail",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ElectricMachineTorqueRipplePeriodicExcitationDetail",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ElectricMachineTorqueRipplePeriodicExcitationDetail:
    """Special nested class for casting ElectricMachineTorqueRipplePeriodicExcitationDetail to subclasses."""

    __parent__: "ElectricMachineTorqueRipplePeriodicExcitationDetail"

    @property
    def electric_machine_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "_6029.ElectricMachinePeriodicExcitationDetail":
        return self.__parent__._cast(_6029.ElectricMachinePeriodicExcitationDetail)

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
    def electric_machine_torque_ripple_periodic_excitation_detail(
        self: "CastSelf",
    ) -> "ElectricMachineTorqueRipplePeriodicExcitationDetail":
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
class ElectricMachineTorqueRipplePeriodicExcitationDetail(
    _6029.ElectricMachinePeriodicExcitationDetail
):
    """ElectricMachineTorqueRipplePeriodicExcitationDetail

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ELECTRIC_MACHINE_TORQUE_RIPPLE_PERIODIC_EXCITATION_DETAIL

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_ElectricMachineTorqueRipplePeriodicExcitationDetail":
        """Cast to another type.

        Returns:
            _Cast_ElectricMachineTorqueRipplePeriodicExcitationDetail
        """
        return _Cast_ElectricMachineTorqueRipplePeriodicExcitationDetail(self)
