"""StraightBevelGearRating"""

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
from mastapy._private.gears.rating.bevel import _647

_STRAIGHT_BEVEL_GEAR_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating.StraightBevel", "StraightBevelGearRating"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1335
    from mastapy._private.gears.gear_designs.straight_bevel import _1065
    from mastapy._private.gears.rating import _445, _453
    from mastapy._private.gears.rating.agma_gleason_conical import _658
    from mastapy._private.gears.rating.conical import _632

    Self = TypeVar("Self", bound="StraightBevelGearRating")
    CastSelf = TypeVar(
        "CastSelf", bound="StraightBevelGearRating._Cast_StraightBevelGearRating"
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelGearRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelGearRating:
    """Special nested class for casting StraightBevelGearRating to subclasses."""

    __parent__: "StraightBevelGearRating"

    @property
    def bevel_gear_rating(self: "CastSelf") -> "_647.BevelGearRating":
        return self.__parent__._cast(_647.BevelGearRating)

    @property
    def agma_gleason_conical_gear_rating(
        self: "CastSelf",
    ) -> "_658.AGMAGleasonConicalGearRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _658

        return self.__parent__._cast(_658.AGMAGleasonConicalGearRating)

    @property
    def conical_gear_rating(self: "CastSelf") -> "_632.ConicalGearRating":
        from mastapy._private.gears.rating.conical import _632

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
    def straight_bevel_gear_rating(self: "CastSelf") -> "StraightBevelGearRating":
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
class StraightBevelGearRating(_647.BevelGearRating):
    """StraightBevelGearRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_GEAR_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def straight_bevel_gear(self: "Self") -> "_1065.StraightBevelGearDesign":
        """mastapy.gears.gear_designs.straight_bevel.StraightBevelGearDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelGear")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_StraightBevelGearRating":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelGearRating
        """
        return _Cast_StraightBevelGearRating(self)
