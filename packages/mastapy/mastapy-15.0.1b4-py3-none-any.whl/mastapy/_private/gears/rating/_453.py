"""GearRating"""

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
from mastapy._private.gears.rating import _445

_GEAR_RATING = python_net_import("SMT.MastaAPI.Gears.Rating", "GearRating")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1335
    from mastapy._private.gears.rating import _447
    from mastapy._private.gears.rating.agma_gleason_conical import _658
    from mastapy._private.gears.rating.bevel import _647
    from mastapy._private.gears.rating.concept import _643
    from mastapy._private.gears.rating.conical import _632
    from mastapy._private.gears.rating.cylindrical import _552
    from mastapy._private.gears.rating.face import _540
    from mastapy._private.gears.rating.hypoid import _531
    from mastapy._private.gears.rating.klingelnberg_conical import _504
    from mastapy._private.gears.rating.klingelnberg_hypoid import _501
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _498
    from mastapy._private.gears.rating.spiral_bevel import _495
    from mastapy._private.gears.rating.straight_bevel import _488
    from mastapy._private.gears.rating.straight_bevel_diff import _491
    from mastapy._private.gears.rating.worm import _466
    from mastapy._private.gears.rating.zerol_bevel import _462
    from mastapy._private.materials import _370

    Self = TypeVar("Self", bound="GearRating")
    CastSelf = TypeVar("CastSelf", bound="GearRating._Cast_GearRating")


__docformat__ = "restructuredtext en"
__all__ = ("GearRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearRating:
    """Special nested class for casting GearRating to subclasses."""

    __parent__: "GearRating"

    @property
    def abstract_gear_rating(self: "CastSelf") -> "_445.AbstractGearRating":
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
    def worm_gear_rating(self: "CastSelf") -> "_466.WormGearRating":
        from mastapy._private.gears.rating.worm import _466

        return self.__parent__._cast(_466.WormGearRating)

    @property
    def straight_bevel_gear_rating(self: "CastSelf") -> "_488.StraightBevelGearRating":
        from mastapy._private.gears.rating.straight_bevel import _488

        return self.__parent__._cast(_488.StraightBevelGearRating)

    @property
    def straight_bevel_diff_gear_rating(
        self: "CastSelf",
    ) -> "_491.StraightBevelDiffGearRating":
        from mastapy._private.gears.rating.straight_bevel_diff import _491

        return self.__parent__._cast(_491.StraightBevelDiffGearRating)

    @property
    def spiral_bevel_gear_rating(self: "CastSelf") -> "_495.SpiralBevelGearRating":
        from mastapy._private.gears.rating.spiral_bevel import _495

        return self.__parent__._cast(_495.SpiralBevelGearRating)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_rating(
        self: "CastSelf",
    ) -> "_498.KlingelnbergCycloPalloidSpiralBevelGearRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _498

        return self.__parent__._cast(_498.KlingelnbergCycloPalloidSpiralBevelGearRating)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_rating(
        self: "CastSelf",
    ) -> "_501.KlingelnbergCycloPalloidHypoidGearRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _501

        return self.__parent__._cast(_501.KlingelnbergCycloPalloidHypoidGearRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_rating(
        self: "CastSelf",
    ) -> "_504.KlingelnbergCycloPalloidConicalGearRating":
        from mastapy._private.gears.rating.klingelnberg_conical import _504

        return self.__parent__._cast(_504.KlingelnbergCycloPalloidConicalGearRating)

    @property
    def hypoid_gear_rating(self: "CastSelf") -> "_531.HypoidGearRating":
        from mastapy._private.gears.rating.hypoid import _531

        return self.__parent__._cast(_531.HypoidGearRating)

    @property
    def face_gear_rating(self: "CastSelf") -> "_540.FaceGearRating":
        from mastapy._private.gears.rating.face import _540

        return self.__parent__._cast(_540.FaceGearRating)

    @property
    def cylindrical_gear_rating(self: "CastSelf") -> "_552.CylindricalGearRating":
        from mastapy._private.gears.rating.cylindrical import _552

        return self.__parent__._cast(_552.CylindricalGearRating)

    @property
    def conical_gear_rating(self: "CastSelf") -> "_632.ConicalGearRating":
        from mastapy._private.gears.rating.conical import _632

        return self.__parent__._cast(_632.ConicalGearRating)

    @property
    def concept_gear_rating(self: "CastSelf") -> "_643.ConceptGearRating":
        from mastapy._private.gears.rating.concept import _643

        return self.__parent__._cast(_643.ConceptGearRating)

    @property
    def bevel_gear_rating(self: "CastSelf") -> "_647.BevelGearRating":
        from mastapy._private.gears.rating.bevel import _647

        return self.__parent__._cast(_647.BevelGearRating)

    @property
    def agma_gleason_conical_gear_rating(
        self: "CastSelf",
    ) -> "_658.AGMAGleasonConicalGearRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _658

        return self.__parent__._cast(_658.AGMAGleasonConicalGearRating)

    @property
    def gear_rating(self: "CastSelf") -> "GearRating":
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
class GearRating(_445.AbstractGearRating):
    """GearRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def bending_safety_factor_results(self: "Self") -> "_370.SafetyFactorItem":
        """mastapy.materials.SafetyFactorItem

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BendingSafetyFactorResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def contact_safety_factor_results(self: "Self") -> "_370.SafetyFactorItem":
        """mastapy.materials.SafetyFactorItem

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ContactSafetyFactorResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def static_safety_factor(self: "Self") -> "_447.BendingAndContactReportingObject":
        """mastapy.gears.rating.BendingAndContactReportingObject

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StaticSafetyFactor")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_GearRating":
        """Cast to another type.

        Returns:
            _Cast_GearRating
        """
        return _Cast_GearRating(self)
