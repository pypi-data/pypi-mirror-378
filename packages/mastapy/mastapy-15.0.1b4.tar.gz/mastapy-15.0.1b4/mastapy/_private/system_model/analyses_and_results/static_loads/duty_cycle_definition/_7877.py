"""SpeedInputOptions"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.analyses_and_results.static_loads.duty_cycle_definition import (
    _7875,
)

_SPEED_INPUT_OPTIONS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.StaticLoads.DutyCycleDefinition",
    "SpeedInputOptions",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.utility_gui import _2055

    Self = TypeVar("Self", bound="SpeedInputOptions")
    CastSelf = TypeVar("CastSelf", bound="SpeedInputOptions._Cast_SpeedInputOptions")


__docformat__ = "restructuredtext en"
__all__ = ("SpeedInputOptions",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SpeedInputOptions:
    """Special nested class for casting SpeedInputOptions to subclasses."""

    __parent__: "SpeedInputOptions"

    @property
    def power_load_input_options(self: "CastSelf") -> "_7875.PowerLoadInputOptions":
        return self.__parent__._cast(_7875.PowerLoadInputOptions)

    @property
    def column_input_options(self: "CastSelf") -> "_2055.ColumnInputOptions":
        from mastapy._private.utility_gui import _2055

        return self.__parent__._cast(_2055.ColumnInputOptions)

    @property
    def speed_input_options(self: "CastSelf") -> "SpeedInputOptions":
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
class SpeedInputOptions(_7875.PowerLoadInputOptions):
    """SpeedInputOptions

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SPEED_INPUT_OPTIONS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_SpeedInputOptions":
        """Cast to another type.

        Returns:
            _Cast_SpeedInputOptions
        """
        return _Cast_SpeedInputOptions(self)
