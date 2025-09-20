"""CylindricalManufacturedGearDutyCycle"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.analysis import _1340

_CYLINDRICAL_MANUFACTURED_GEAR_DUTY_CYCLE = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Cylindrical",
    "CylindricalManufacturedGearDutyCycle",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1335, _1338

    Self = TypeVar("Self", bound="CylindricalManufacturedGearDutyCycle")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CylindricalManufacturedGearDutyCycle._Cast_CylindricalManufacturedGearDutyCycle",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalManufacturedGearDutyCycle",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalManufacturedGearDutyCycle:
    """Special nested class for casting CylindricalManufacturedGearDutyCycle to subclasses."""

    __parent__: "CylindricalManufacturedGearDutyCycle"

    @property
    def gear_implementation_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1340.GearImplementationAnalysisDutyCycle":
        return self.__parent__._cast(_1340.GearImplementationAnalysisDutyCycle)

    @property
    def gear_design_analysis(self: "CastSelf") -> "_1338.GearDesignAnalysis":
        from mastapy._private.gears.analysis import _1338

        return self.__parent__._cast(_1338.GearDesignAnalysis)

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1335.AbstractGearAnalysis":
        from mastapy._private.gears.analysis import _1335

        return self.__parent__._cast(_1335.AbstractGearAnalysis)

    @property
    def cylindrical_manufactured_gear_duty_cycle(
        self: "CastSelf",
    ) -> "CylindricalManufacturedGearDutyCycle":
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
class CylindricalManufacturedGearDutyCycle(_1340.GearImplementationAnalysisDutyCycle):
    """CylindricalManufacturedGearDutyCycle

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_MANUFACTURED_GEAR_DUTY_CYCLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_CylindricalManufacturedGearDutyCycle":
        """Cast to another type.

        Returns:
            _Cast_CylindricalManufacturedGearDutyCycle
        """
        return _Cast_CylindricalManufacturedGearDutyCycle(self)
