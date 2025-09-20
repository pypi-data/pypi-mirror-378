"""PlungeShavingDynamicsCalculationForHobbedGears"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import (
    _859,
    _872,
)

_PLUNGE_SHAVING_DYNAMICS_CALCULATION_FOR_HOBBED_GEARS = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Cylindrical.AxialAndPlungeShavingDynamics",
    "PlungeShavingDynamicsCalculationForHobbedGears",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import (
        _870,
    )

    Self = TypeVar("Self", bound="PlungeShavingDynamicsCalculationForHobbedGears")
    CastSelf = TypeVar(
        "CastSelf",
        bound="PlungeShavingDynamicsCalculationForHobbedGears._Cast_PlungeShavingDynamicsCalculationForHobbedGears",
    )


__docformat__ = "restructuredtext en"
__all__ = ("PlungeShavingDynamicsCalculationForHobbedGears",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PlungeShavingDynamicsCalculationForHobbedGears:
    """Special nested class for casting PlungeShavingDynamicsCalculationForHobbedGears to subclasses."""

    __parent__: "PlungeShavingDynamicsCalculationForHobbedGears"

    @property
    def shaving_dynamics_calculation_for_hobbed_gears(
        self: "CastSelf",
    ) -> "_872.ShavingDynamicsCalculationForHobbedGears":
        return self.__parent__._cast(_872.ShavingDynamicsCalculationForHobbedGears)

    @property
    def shaving_dynamics_calculation(
        self: "CastSelf",
    ) -> "_870.ShavingDynamicsCalculation":
        from mastapy._private.gears.manufacturing.cylindrical.axial_and_plunge_shaving_dynamics import (
            _870,
        )

        return self.__parent__._cast(_870.ShavingDynamicsCalculation)

    @property
    def plunge_shaving_dynamics_calculation_for_hobbed_gears(
        self: "CastSelf",
    ) -> "PlungeShavingDynamicsCalculationForHobbedGears":
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
class PlungeShavingDynamicsCalculationForHobbedGears(
    _872.ShavingDynamicsCalculationForHobbedGears[_859.PlungeShaverDynamics]
):
    """PlungeShavingDynamicsCalculationForHobbedGears

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PLUNGE_SHAVING_DYNAMICS_CALCULATION_FOR_HOBBED_GEARS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_PlungeShavingDynamicsCalculationForHobbedGears":
        """Cast to another type.

        Returns:
            _Cast_PlungeShavingDynamicsCalculationForHobbedGears
        """
        return _Cast_PlungeShavingDynamicsCalculationForHobbedGears(self)
