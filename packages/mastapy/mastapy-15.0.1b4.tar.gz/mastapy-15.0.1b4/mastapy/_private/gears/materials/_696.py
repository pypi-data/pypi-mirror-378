"""ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.materials import _695

_ISO14179_PART_2_COEFFICIENT_OF_FRICTION_CALCULATOR_WITH_MARTINS_MODIFICATION = (
    python_net_import(
        "SMT.MastaAPI.Gears.Materials",
        "ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification",
    )
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.materials import _682

    Self = TypeVar(
        "Self",
        bound="ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification",
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification._Cast_ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification:
    """Special nested class for casting ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification to subclasses."""

    __parent__: "ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification"

    @property
    def iso14179_part_2_coefficient_of_friction_calculator_base(
        self: "CastSelf",
    ) -> "_695.ISO14179Part2CoefficientOfFrictionCalculatorBase":
        return self.__parent__._cast(
            _695.ISO14179Part2CoefficientOfFrictionCalculatorBase
        )

    @property
    def coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "_682.CoefficientOfFrictionCalculator":
        from mastapy._private.gears.materials import _682

        return self.__parent__._cast(_682.CoefficientOfFrictionCalculator)

    @property
    def iso14179_part_2_coefficient_of_friction_calculator_with_martins_modification(
        self: "CastSelf",
    ) -> "ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification":
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
class ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification(
    _695.ISO14179Part2CoefficientOfFrictionCalculatorBase
):
    """ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _ISO14179_PART_2_COEFFICIENT_OF_FRICTION_CALCULATOR_WITH_MARTINS_MODIFICATION
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification":
        """Cast to another type.

        Returns:
            _Cast_ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification
        """
        return (
            _Cast_ISO14179Part2CoefficientOfFrictionCalculatorWithMartinsModification(
                self
            )
        )
