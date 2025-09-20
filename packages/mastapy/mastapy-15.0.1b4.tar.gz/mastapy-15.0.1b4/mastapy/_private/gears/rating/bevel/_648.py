"""BevelGearSetRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.gears.rating.agma_gleason_conical import _659

_BEVEL_GEAR_SET_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.Bevel", "BevelGearSetRating"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1337
    from mastapy._private.gears.rating import _446, _455
    from mastapy._private.gears.rating.conical import _634
    from mastapy._private.gears.rating.spiral_bevel import _496
    from mastapy._private.gears.rating.straight_bevel import _489
    from mastapy._private.gears.rating.zerol_bevel import _463

    Self = TypeVar("Self", bound="BevelGearSetRating")
    CastSelf = TypeVar("CastSelf", bound="BevelGearSetRating._Cast_BevelGearSetRating")


__docformat__ = "restructuredtext en"
__all__ = ("BevelGearSetRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BevelGearSetRating:
    """Special nested class for casting BevelGearSetRating to subclasses."""

    __parent__: "BevelGearSetRating"

    @property
    def agma_gleason_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_659.AGMAGleasonConicalGearSetRating":
        return self.__parent__._cast(_659.AGMAGleasonConicalGearSetRating)

    @property
    def conical_gear_set_rating(self: "CastSelf") -> "_634.ConicalGearSetRating":
        from mastapy._private.gears.rating.conical import _634

        return self.__parent__._cast(_634.ConicalGearSetRating)

    @property
    def gear_set_rating(self: "CastSelf") -> "_455.GearSetRating":
        from mastapy._private.gears.rating import _455

        return self.__parent__._cast(_455.GearSetRating)

    @property
    def abstract_gear_set_rating(self: "CastSelf") -> "_446.AbstractGearSetRating":
        from mastapy._private.gears.rating import _446

        return self.__parent__._cast(_446.AbstractGearSetRating)

    @property
    def abstract_gear_set_analysis(self: "CastSelf") -> "_1337.AbstractGearSetAnalysis":
        from mastapy._private.gears.analysis import _1337

        return self.__parent__._cast(_1337.AbstractGearSetAnalysis)

    @property
    def zerol_bevel_gear_set_rating(self: "CastSelf") -> "_463.ZerolBevelGearSetRating":
        from mastapy._private.gears.rating.zerol_bevel import _463

        return self.__parent__._cast(_463.ZerolBevelGearSetRating)

    @property
    def straight_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_489.StraightBevelGearSetRating":
        from mastapy._private.gears.rating.straight_bevel import _489

        return self.__parent__._cast(_489.StraightBevelGearSetRating)

    @property
    def spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_496.SpiralBevelGearSetRating":
        from mastapy._private.gears.rating.spiral_bevel import _496

        return self.__parent__._cast(_496.SpiralBevelGearSetRating)

    @property
    def bevel_gear_set_rating(self: "CastSelf") -> "BevelGearSetRating":
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
class BevelGearSetRating(_659.AGMAGleasonConicalGearSetRating):
    """BevelGearSetRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEVEL_GEAR_SET_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def rating(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Rating")

        if temp is None:
            return ""

        return temp

    @property
    def cast_to(self: "Self") -> "_Cast_BevelGearSetRating":
        """Cast to another type.

        Returns:
            _Cast_BevelGearSetRating
        """
        return _Cast_BevelGearSetRating(self)
