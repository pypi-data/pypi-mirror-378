"""ThermalConnectorWithoutResistance"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.nodal_analysis.lumped_parameter_thermal_analysis import _216

_THERMAL_CONNECTOR_WITHOUT_RESISTANCE = python_net_import(
    "SMT.MastaAPI.NodalAnalysis.LumpedParameterThermalAnalysis",
    "ThermalConnectorWithoutResistance",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="ThermalConnectorWithoutResistance")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ThermalConnectorWithoutResistance._Cast_ThermalConnectorWithoutResistance",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ThermalConnectorWithoutResistance",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ThermalConnectorWithoutResistance:
    """Special nested class for casting ThermalConnectorWithoutResistance to subclasses."""

    __parent__: "ThermalConnectorWithoutResistance"

    @property
    def thermal_connector(self: "CastSelf") -> "_216.ThermalConnector":
        return self.__parent__._cast(_216.ThermalConnector)

    @property
    def thermal_connector_without_resistance(
        self: "CastSelf",
    ) -> "ThermalConnectorWithoutResistance":
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
class ThermalConnectorWithoutResistance(_216.ThermalConnector):
    """ThermalConnectorWithoutResistance

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _THERMAL_CONNECTOR_WITHOUT_RESISTANCE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ThermalConnectorWithoutResistance":
        """Cast to another type.

        Returns:
            _Cast_ThermalConnectorWithoutResistance
        """
        return _Cast_ThermalConnectorWithoutResistance(self)
