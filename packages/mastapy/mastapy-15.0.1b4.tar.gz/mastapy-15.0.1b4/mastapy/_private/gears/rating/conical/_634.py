"""ConicalGearSetRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.gears.rating import _455

_CONICAL_GEAR_SET_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.Conical", "ConicalGearSetRating"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1337
    from mastapy._private.gears.gear_designs import _1047
    from mastapy._private.gears.rating import _446
    from mastapy._private.gears.rating.agma_gleason_conical import _659
    from mastapy._private.gears.rating.bevel import _648
    from mastapy._private.gears.rating.hypoid import _532
    from mastapy._private.gears.rating.klingelnberg_conical import _505
    from mastapy._private.gears.rating.klingelnberg_hypoid import _502
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _499
    from mastapy._private.gears.rating.spiral_bevel import _496
    from mastapy._private.gears.rating.straight_bevel import _489
    from mastapy._private.gears.rating.straight_bevel_diff import _492
    from mastapy._private.gears.rating.zerol_bevel import _463

    Self = TypeVar("Self", bound="ConicalGearSetRating")
    CastSelf = TypeVar(
        "CastSelf", bound="ConicalGearSetRating._Cast_ConicalGearSetRating"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearSetRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearSetRating:
    """Special nested class for casting ConicalGearSetRating to subclasses."""

    __parent__: "ConicalGearSetRating"

    @property
    def gear_set_rating(self: "CastSelf") -> "_455.GearSetRating":
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
    def straight_bevel_diff_gear_set_rating(
        self: "CastSelf",
    ) -> "_492.StraightBevelDiffGearSetRating":
        from mastapy._private.gears.rating.straight_bevel_diff import _492

        return self.__parent__._cast(_492.StraightBevelDiffGearSetRating)

    @property
    def spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_496.SpiralBevelGearSetRating":
        from mastapy._private.gears.rating.spiral_bevel import _496

        return self.__parent__._cast(_496.SpiralBevelGearSetRating)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_499.KlingelnbergCycloPalloidSpiralBevelGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _499

        return self.__parent__._cast(
            _499.KlingelnbergCycloPalloidSpiralBevelGearSetRating
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_rating(
        self: "CastSelf",
    ) -> "_502.KlingelnbergCycloPalloidHypoidGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _502

        return self.__parent__._cast(_502.KlingelnbergCycloPalloidHypoidGearSetRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_505.KlingelnbergCycloPalloidConicalGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_conical import _505

        return self.__parent__._cast(_505.KlingelnbergCycloPalloidConicalGearSetRating)

    @property
    def hypoid_gear_set_rating(self: "CastSelf") -> "_532.HypoidGearSetRating":
        from mastapy._private.gears.rating.hypoid import _532

        return self.__parent__._cast(_532.HypoidGearSetRating)

    @property
    def bevel_gear_set_rating(self: "CastSelf") -> "_648.BevelGearSetRating":
        from mastapy._private.gears.rating.bevel import _648

        return self.__parent__._cast(_648.BevelGearSetRating)

    @property
    def agma_gleason_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_659.AGMAGleasonConicalGearSetRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _659

        return self.__parent__._cast(_659.AGMAGleasonConicalGearSetRating)

    @property
    def conical_gear_set_rating(self: "CastSelf") -> "ConicalGearSetRating":
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
class ConicalGearSetRating(_455.GearSetRating):
    """ConicalGearSetRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_GEAR_SET_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def rating_settings(self: "Self") -> "_1047.BevelHypoidGearRatingSettingsItem":
        """mastapy.gears.gear_designs.BevelHypoidGearRatingSettingsItem

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RatingSettings")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalGearSetRating":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearSetRating
        """
        return _Cast_ConicalGearSetRating(self)
