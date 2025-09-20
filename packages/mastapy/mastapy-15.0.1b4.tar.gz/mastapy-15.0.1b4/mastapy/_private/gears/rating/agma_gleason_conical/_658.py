"""AGMAGleasonConicalGearRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.rating.conical import _632

_AGMA_GLEASON_CONICAL_GEAR_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.AGMAGleasonConical", "AGMAGleasonConicalGearRating"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1335
    from mastapy._private.gears.rating import _445, _453
    from mastapy._private.gears.rating.bevel import _647
    from mastapy._private.gears.rating.hypoid import _531
    from mastapy._private.gears.rating.spiral_bevel import _495
    from mastapy._private.gears.rating.straight_bevel import _488
    from mastapy._private.gears.rating.zerol_bevel import _462

    Self = TypeVar("Self", bound="AGMAGleasonConicalGearRating")
    CastSelf = TypeVar(
        "CastSelf",
        bound="AGMAGleasonConicalGearRating._Cast_AGMAGleasonConicalGearRating",
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGearRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGearRating:
    """Special nested class for casting AGMAGleasonConicalGearRating to subclasses."""

    __parent__: "AGMAGleasonConicalGearRating"

    @property
    def conical_gear_rating(self: "CastSelf") -> "_632.ConicalGearRating":
        return self.__parent__._cast(_632.ConicalGearRating)

    @property
    def gear_rating(self: "CastSelf") -> "_453.GearRating":
        from mastapy._private.gears.rating import _453

        return self.__parent__._cast(_453.GearRating)

    @property
    def abstract_gear_rating(self: "CastSelf") -> "_445.AbstractGearRating":
        from mastapy._private.gears.rating import _445

        return self.__parent__._cast(_445.AbstractGearRating)

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1335.AbstractGearAnalysis":
        from mastapy._private.gears.analysis import _1335

        return self.__parent__._cast(_1335.AbstractGearAnalysis)

    @property
    def zerol_bevel_gear_rating(self: "CastSelf") -> "_462.ZerolBevelGearRating":
        from mastapy._private.gears.rating.zerol_bevel import _462

        return self.__parent__._cast(_462.ZerolBevelGearRating)

    @property
    def straight_bevel_gear_rating(self: "CastSelf") -> "_488.StraightBevelGearRating":
        from mastapy._private.gears.rating.straight_bevel import _488

        return self.__parent__._cast(_488.StraightBevelGearRating)

    @property
    def spiral_bevel_gear_rating(self: "CastSelf") -> "_495.SpiralBevelGearRating":
        from mastapy._private.gears.rating.spiral_bevel import _495

        return self.__parent__._cast(_495.SpiralBevelGearRating)

    @property
    def hypoid_gear_rating(self: "CastSelf") -> "_531.HypoidGearRating":
        from mastapy._private.gears.rating.hypoid import _531

        return self.__parent__._cast(_531.HypoidGearRating)

    @property
    def bevel_gear_rating(self: "CastSelf") -> "_647.BevelGearRating":
        from mastapy._private.gears.rating.bevel import _647

        return self.__parent__._cast(_647.BevelGearRating)

    @property
    def agma_gleason_conical_gear_rating(
        self: "CastSelf",
    ) -> "AGMAGleasonConicalGearRating":
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
class AGMAGleasonConicalGearRating(_632.ConicalGearRating):
    """AGMAGleasonConicalGearRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGearRating":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGearRating
        """
        return _Cast_AGMAGleasonConicalGearRating(self)
