"""AxialGrooveJournalBearing"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.bearings.bearing_designs.fluid_film import _2397

_AXIAL_GROOVE_JOURNAL_BEARING = python_net_import(
    "SMT.MastaAPI.Bearings.BearingDesigns.FluidFilm", "AxialGrooveJournalBearing"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="AxialGrooveJournalBearing")
    CastSelf = TypeVar(
        "CastSelf", bound="AxialGrooveJournalBearing._Cast_AxialGrooveJournalBearing"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AxialGrooveJournalBearing",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AxialGrooveJournalBearing:
    """Special nested class for casting AxialGrooveJournalBearing to subclasses."""

    __parent__: "AxialGrooveJournalBearing"

    @property
    def axial_feed_journal_bearing(self: "CastSelf") -> "_2397.AxialFeedJournalBearing":
        return self.__parent__._cast(_2397.AxialFeedJournalBearing)

    @property
    def axial_groove_journal_bearing(self: "CastSelf") -> "AxialGrooveJournalBearing":
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
class AxialGrooveJournalBearing(_2397.AxialFeedJournalBearing):
    """AxialGrooveJournalBearing

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AXIAL_GROOVE_JOURNAL_BEARING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def groove_length(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "GrooveLength")

        if temp is None:
            return 0.0

        return temp

    @groove_length.setter
    @exception_bridge
    @enforce_parameter_types
    def groove_length(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "GrooveLength", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def groove_radial_dimension(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "GrooveRadialDimension")

        if temp is None:
            return 0.0

        return temp

    @groove_radial_dimension.setter
    @exception_bridge
    @enforce_parameter_types
    def groove_radial_dimension(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "GrooveRadialDimension",
            float(value) if value is not None else 0.0,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_AxialGrooveJournalBearing":
        """Cast to another type.

        Returns:
            _Cast_AxialGrooveJournalBearing
        """
        return _Cast_AxialGrooveJournalBearing(self)
