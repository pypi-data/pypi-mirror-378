"""AbstractGearSetRating"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.gears.analysis import _1337

_ABSTRACT_GEAR_SET_RATING = python_net_import(
    "SMT.MastaAPI.Gears.Rating", "AbstractGearSetRating"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears import _418
    from mastapy._private.gears.rating import _444, _445, _454, _455
    from mastapy._private.gears.rating.agma_gleason_conical import _659
    from mastapy._private.gears.rating.bevel import _648
    from mastapy._private.gears.rating.concept import _644, _645
    from mastapy._private.gears.rating.conical import _633, _634
    from mastapy._private.gears.rating.cylindrical import _555, _556, _572
    from mastapy._private.gears.rating.face import _541, _542
    from mastapy._private.gears.rating.hypoid import _532
    from mastapy._private.gears.rating.klingelnberg_conical import _505
    from mastapy._private.gears.rating.klingelnberg_hypoid import _502
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _499
    from mastapy._private.gears.rating.spiral_bevel import _496
    from mastapy._private.gears.rating.straight_bevel import _489
    from mastapy._private.gears.rating.straight_bevel_diff import _492
    from mastapy._private.gears.rating.worm import _467, _468
    from mastapy._private.gears.rating.zerol_bevel import _463

    Self = TypeVar("Self", bound="AbstractGearSetRating")
    CastSelf = TypeVar(
        "CastSelf", bound="AbstractGearSetRating._Cast_AbstractGearSetRating"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractGearSetRating",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractGearSetRating:
    """Special nested class for casting AbstractGearSetRating to subclasses."""

    __parent__: "AbstractGearSetRating"

    @property
    def abstract_gear_set_analysis(self: "CastSelf") -> "_1337.AbstractGearSetAnalysis":
        return self.__parent__._cast(_1337.AbstractGearSetAnalysis)

    @property
    def gear_set_duty_cycle_rating(self: "CastSelf") -> "_454.GearSetDutyCycleRating":
        from mastapy._private.gears.rating import _454

        return self.__parent__._cast(_454.GearSetDutyCycleRating)

    @property
    def gear_set_rating(self: "CastSelf") -> "_455.GearSetRating":
        from mastapy._private.gears.rating import _455

        return self.__parent__._cast(_455.GearSetRating)

    @property
    def zerol_bevel_gear_set_rating(self: "CastSelf") -> "_463.ZerolBevelGearSetRating":
        from mastapy._private.gears.rating.zerol_bevel import _463

        return self.__parent__._cast(_463.ZerolBevelGearSetRating)

    @property
    def worm_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_467.WormGearSetDutyCycleRating":
        from mastapy._private.gears.rating.worm import _467

        return self.__parent__._cast(_467.WormGearSetDutyCycleRating)

    @property
    def worm_gear_set_rating(self: "CastSelf") -> "_468.WormGearSetRating":
        from mastapy._private.gears.rating.worm import _468

        return self.__parent__._cast(_468.WormGearSetRating)

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
    def face_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_541.FaceGearSetDutyCycleRating":
        from mastapy._private.gears.rating.face import _541

        return self.__parent__._cast(_541.FaceGearSetDutyCycleRating)

    @property
    def face_gear_set_rating(self: "CastSelf") -> "_542.FaceGearSetRating":
        from mastapy._private.gears.rating.face import _542

        return self.__parent__._cast(_542.FaceGearSetRating)

    @property
    def cylindrical_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_555.CylindricalGearSetDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _555

        return self.__parent__._cast(_555.CylindricalGearSetDutyCycleRating)

    @property
    def cylindrical_gear_set_rating(
        self: "CastSelf",
    ) -> "_556.CylindricalGearSetRating":
        from mastapy._private.gears.rating.cylindrical import _556

        return self.__parent__._cast(_556.CylindricalGearSetRating)

    @property
    def reduced_cylindrical_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_572.ReducedCylindricalGearSetDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _572

        return self.__parent__._cast(_572.ReducedCylindricalGearSetDutyCycleRating)

    @property
    def conical_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_633.ConicalGearSetDutyCycleRating":
        from mastapy._private.gears.rating.conical import _633

        return self.__parent__._cast(_633.ConicalGearSetDutyCycleRating)

    @property
    def conical_gear_set_rating(self: "CastSelf") -> "_634.ConicalGearSetRating":
        from mastapy._private.gears.rating.conical import _634

        return self.__parent__._cast(_634.ConicalGearSetRating)

    @property
    def concept_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_644.ConceptGearSetDutyCycleRating":
        from mastapy._private.gears.rating.concept import _644

        return self.__parent__._cast(_644.ConceptGearSetDutyCycleRating)

    @property
    def concept_gear_set_rating(self: "CastSelf") -> "_645.ConceptGearSetRating":
        from mastapy._private.gears.rating.concept import _645

        return self.__parent__._cast(_645.ConceptGearSetRating)

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
    def abstract_gear_set_rating(self: "CastSelf") -> "AbstractGearSetRating":
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
class AbstractGearSetRating(_1337.AbstractGearSetAnalysis):
    """AbstractGearSetRating

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_GEAR_SET_RATING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def bending_safety_factor_for_fatigue(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BendingSafetyFactorForFatigue")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def bending_safety_factor_for_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "BendingSafetyFactorForStatic")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def contact_safety_factor_for_fatigue(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ContactSafetyFactorForFatigue")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def contact_safety_factor_for_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ContactSafetyFactorForStatic")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_bending_safety_factor_for_fatigue(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NormalisedBendingSafetyFactorForFatigue"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_bending_safety_factor_for_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NormalisedBendingSafetyFactorForStatic"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_contact_safety_factor_for_fatigue(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NormalisedContactSafetyFactorForFatigue"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_contact_safety_factor_for_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NormalisedContactSafetyFactorForStatic"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_safety_factor_for_fatigue(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalisedSafetyFactorForFatigue")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_safety_factor_for_fatigue_and_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "NormalisedSafetyFactorForFatigueAndStatic"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def normalised_safety_factor_for_static(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NormalisedSafetyFactorForStatic")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def total_gear_reliability(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TotalGearReliability")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def transmission_properties_gears(self: "Self") -> "_418.GearSetDesignGroup":
        """mastapy.gears.GearSetDesignGroup

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TransmissionPropertiesGears")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def gear_mesh_ratings(self: "Self") -> "List[_444.AbstractGearMeshRating]":
        """List[mastapy.gears.rating.AbstractGearMeshRating]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearMeshRatings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def gear_ratings(self: "Self") -> "List[_445.AbstractGearRating]":
        """List[mastapy.gears.rating.AbstractGearRating]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "GearRatings")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_AbstractGearSetRating":
        """Cast to another type.

        Returns:
            _Cast_AbstractGearSetRating
        """
        return _Cast_AbstractGearSetRating(self)
