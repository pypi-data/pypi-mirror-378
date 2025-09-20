"""Stress"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.utility.units_and_measurements import _1802

_STRESS = python_net_import(
    "SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements", "Stress"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility.units_and_measurements.measurements import (
        _1897,
        _1899,
    )

    Self = TypeVar("Self", bound="Stress")
    CastSelf = TypeVar("CastSelf", bound="Stress._Cast_Stress")


__docformat__ = "restructuredtext en"
__all__ = ("Stress",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Stress:
    """Special nested class for casting Stress to subclasses."""

    __parent__: "Stress"

    @property
    def measurement_base(self: "CastSelf") -> "_1802.MeasurementBase":
        return self.__parent__._cast(_1802.MeasurementBase)

    @property
    def pressure(self: "CastSelf") -> "_1897.Pressure":
        from mastapy._private.utility.units_and_measurements.measurements import _1897

        return self.__parent__._cast(_1897.Pressure)

    @property
    def pressure_small(self: "CastSelf") -> "_1899.PressureSmall":
        from mastapy._private.utility.units_and_measurements.measurements import _1899

        return self.__parent__._cast(_1899.PressureSmall)

    @property
    def stress(self: "CastSelf") -> "Stress":
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
class Stress(_1802.MeasurementBase):
    """Stress

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRESS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_Stress":
        """Cast to another type.

        Returns:
            _Cast_Stress
        """
        return _Cast_Stress(self)
