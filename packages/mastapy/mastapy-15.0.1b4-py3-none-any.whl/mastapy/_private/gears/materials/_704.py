"""MisharinCoefficientOfFrictionCalculator"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.materials import _692

_MISHARIN_COEFFICIENT_OF_FRICTION_CALCULATOR = python_net_import(
    "SMT.MastaAPI.Gears.Materials", "MisharinCoefficientOfFrictionCalculator"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.materials import _682

    Self = TypeVar("Self", bound="MisharinCoefficientOfFrictionCalculator")
    CastSelf = TypeVar(
        "CastSelf",
        bound="MisharinCoefficientOfFrictionCalculator._Cast_MisharinCoefficientOfFrictionCalculator",
    )


__docformat__ = "restructuredtext en"
__all__ = ("MisharinCoefficientOfFrictionCalculator",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MisharinCoefficientOfFrictionCalculator:
    """Special nested class for casting MisharinCoefficientOfFrictionCalculator to subclasses."""

    __parent__: "MisharinCoefficientOfFrictionCalculator"

    @property
    def instantaneous_coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "_692.InstantaneousCoefficientOfFrictionCalculator":
        return self.__parent__._cast(_692.InstantaneousCoefficientOfFrictionCalculator)

    @property
    def coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "_682.CoefficientOfFrictionCalculator":
        from mastapy._private.gears.materials import _682

        return self.__parent__._cast(_682.CoefficientOfFrictionCalculator)

    @property
    def misharin_coefficient_of_friction_calculator(
        self: "CastSelf",
    ) -> "MisharinCoefficientOfFrictionCalculator":
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
class MisharinCoefficientOfFrictionCalculator(
    _692.InstantaneousCoefficientOfFrictionCalculator
):
    """MisharinCoefficientOfFrictionCalculator

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MISHARIN_COEFFICIENT_OF_FRICTION_CALCULATOR

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_MisharinCoefficientOfFrictionCalculator":
        """Cast to another type.

        Returns:
            _Cast_MisharinCoefficientOfFrictionCalculator
        """
        return _Cast_MisharinCoefficientOfFrictionCalculator(self)
