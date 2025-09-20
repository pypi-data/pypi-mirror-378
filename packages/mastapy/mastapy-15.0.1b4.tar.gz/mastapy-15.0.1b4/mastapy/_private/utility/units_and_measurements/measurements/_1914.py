"""Temperature"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.utility.units_and_measurements import _1802

_TEMPERATURE = python_net_import(
    "SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements", "Temperature"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="Temperature")
    CastSelf = TypeVar("CastSelf", bound="Temperature._Cast_Temperature")


__docformat__ = "restructuredtext en"
__all__ = ("Temperature",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Temperature:
    """Special nested class for casting Temperature to subclasses."""

    __parent__: "Temperature"

    @property
    def measurement_base(self: "CastSelf") -> "_1802.MeasurementBase":
        return self.__parent__._cast(_1802.MeasurementBase)

    @property
    def temperature(self: "CastSelf") -> "Temperature":
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
class Temperature(_1802.MeasurementBase):
    """Temperature

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _TEMPERATURE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_Temperature":
        """Cast to another type.

        Returns:
            _Cast_Temperature
        """
        return _Cast_Temperature(self)
