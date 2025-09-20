"""HypoidGearSetCreationOptions"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.gear_designs.creation_options import _1267
from mastapy._private.gears.gear_designs.hypoid import _1091

_HYPOID_GEAR_SET_CREATION_OPTIONS = python_net_import(
    "SMT.MastaAPI.Gears.GearDesigns.CreationOptions", "HypoidGearSetCreationOptions"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="HypoidGearSetCreationOptions")
    CastSelf = TypeVar(
        "CastSelf",
        bound="HypoidGearSetCreationOptions._Cast_HypoidGearSetCreationOptions",
    )


__docformat__ = "restructuredtext en"
__all__ = ("HypoidGearSetCreationOptions",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_HypoidGearSetCreationOptions:
    """Special nested class for casting HypoidGearSetCreationOptions to subclasses."""

    __parent__: "HypoidGearSetCreationOptions"

    @property
    def gear_set_creation_options(self: "CastSelf") -> "_1267.GearSetCreationOptions":
        return self.__parent__._cast(_1267.GearSetCreationOptions)

    @property
    def hypoid_gear_set_creation_options(
        self: "CastSelf",
    ) -> "HypoidGearSetCreationOptions":
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
class HypoidGearSetCreationOptions(
    _1267.GearSetCreationOptions[_1091.HypoidGearSetDesign]
):
    """HypoidGearSetCreationOptions

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _HYPOID_GEAR_SET_CREATION_OPTIONS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_HypoidGearSetCreationOptions":
        """Cast to another type.

        Returns:
            _Cast_HypoidGearSetCreationOptions
        """
        return _Cast_HypoidGearSetCreationOptions(self)
