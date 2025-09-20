"""LoadedBearingResults"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.bearings import _2083

_LOADED_BEARING_RESULTS = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults", "LoadedBearingResults"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.bearings.bearing_designs import _2345
    from mastapy._private.bearings.bearing_results import (
        _2162,
        _2163,
        _2164,
        _2165,
        _2166,
        _2168,
        _2171,
    )
    from mastapy._private.bearings.bearing_results.fluid_film import (
        _2334,
        _2335,
        _2336,
        _2337,
        _2339,
        _2342,
        _2343,
    )
    from mastapy._private.bearings.bearing_results.rolling import (
        _2196,
        _2199,
        _2202,
        _2207,
        _2210,
        _2215,
        _2218,
        _2222,
        _2225,
        _2230,
        _2234,
        _2237,
        _2242,
        _2246,
        _2249,
        _2253,
        _2256,
        _2261,
        _2264,
        _2267,
        _2270,
        _2281,
    )
    from mastapy._private.math_utility.measured_vectors import _1753

    Self = TypeVar("Self", bound="LoadedBearingResults")
    CastSelf = TypeVar(
        "CastSelf", bound="LoadedBearingResults._Cast_LoadedBearingResults"
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedBearingResults",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedBearingResults:
    """Special nested class for casting LoadedBearingResults to subclasses."""

    __parent__: "LoadedBearingResults"

    @property
    def bearing_load_case_results_lightweight(
        self: "CastSelf",
    ) -> "_2083.BearingLoadCaseResultsLightweight":
        return self.__parent__._cast(_2083.BearingLoadCaseResultsLightweight)

    @property
    def loaded_concept_axial_clearance_bearing_results(
        self: "CastSelf",
    ) -> "_2162.LoadedConceptAxialClearanceBearingResults":
        from mastapy._private.bearings.bearing_results import _2162

        return self.__parent__._cast(_2162.LoadedConceptAxialClearanceBearingResults)

    @property
    def loaded_concept_clearance_bearing_results(
        self: "CastSelf",
    ) -> "_2163.LoadedConceptClearanceBearingResults":
        from mastapy._private.bearings.bearing_results import _2163

        return self.__parent__._cast(_2163.LoadedConceptClearanceBearingResults)

    @property
    def loaded_concept_radial_clearance_bearing_results(
        self: "CastSelf",
    ) -> "_2164.LoadedConceptRadialClearanceBearingResults":
        from mastapy._private.bearings.bearing_results import _2164

        return self.__parent__._cast(_2164.LoadedConceptRadialClearanceBearingResults)

    @property
    def loaded_detailed_bearing_results(
        self: "CastSelf",
    ) -> "_2165.LoadedDetailedBearingResults":
        from mastapy._private.bearings.bearing_results import _2165

        return self.__parent__._cast(_2165.LoadedDetailedBearingResults)

    @property
    def loaded_linear_bearing_results(
        self: "CastSelf",
    ) -> "_2166.LoadedLinearBearingResults":
        from mastapy._private.bearings.bearing_results import _2166

        return self.__parent__._cast(_2166.LoadedLinearBearingResults)

    @property
    def loaded_non_linear_bearing_results(
        self: "CastSelf",
    ) -> "_2168.LoadedNonLinearBearingResults":
        from mastapy._private.bearings.bearing_results import _2168

        return self.__parent__._cast(_2168.LoadedNonLinearBearingResults)

    @property
    def loaded_angular_contact_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2196.LoadedAngularContactBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2196

        return self.__parent__._cast(_2196.LoadedAngularContactBallBearingResults)

    @property
    def loaded_angular_contact_thrust_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2199.LoadedAngularContactThrustBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2199

        return self.__parent__._cast(_2199.LoadedAngularContactThrustBallBearingResults)

    @property
    def loaded_asymmetric_spherical_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2202.LoadedAsymmetricSphericalRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2202

        return self.__parent__._cast(
            _2202.LoadedAsymmetricSphericalRollerBearingResults
        )

    @property
    def loaded_axial_thrust_cylindrical_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2207.LoadedAxialThrustCylindricalRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2207

        return self.__parent__._cast(
            _2207.LoadedAxialThrustCylindricalRollerBearingResults
        )

    @property
    def loaded_axial_thrust_needle_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2210.LoadedAxialThrustNeedleRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2210

        return self.__parent__._cast(_2210.LoadedAxialThrustNeedleRollerBearingResults)

    @property
    def loaded_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2215.LoadedBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2215

        return self.__parent__._cast(_2215.LoadedBallBearingResults)

    @property
    def loaded_crossed_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2218.LoadedCrossedRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2218

        return self.__parent__._cast(_2218.LoadedCrossedRollerBearingResults)

    @property
    def loaded_cylindrical_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2222.LoadedCylindricalRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2222

        return self.__parent__._cast(_2222.LoadedCylindricalRollerBearingResults)

    @property
    def loaded_deep_groove_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2225.LoadedDeepGrooveBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2225

        return self.__parent__._cast(_2225.LoadedDeepGrooveBallBearingResults)

    @property
    def loaded_four_point_contact_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2230.LoadedFourPointContactBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2230

        return self.__parent__._cast(_2230.LoadedFourPointContactBallBearingResults)

    @property
    def loaded_needle_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2234.LoadedNeedleRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2234

        return self.__parent__._cast(_2234.LoadedNeedleRollerBearingResults)

    @property
    def loaded_non_barrel_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2237.LoadedNonBarrelRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2237

        return self.__parent__._cast(_2237.LoadedNonBarrelRollerBearingResults)

    @property
    def loaded_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2242.LoadedRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2242

        return self.__parent__._cast(_2242.LoadedRollerBearingResults)

    @property
    def loaded_rolling_bearing_results(
        self: "CastSelf",
    ) -> "_2246.LoadedRollingBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2246

        return self.__parent__._cast(_2246.LoadedRollingBearingResults)

    @property
    def loaded_self_aligning_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2249.LoadedSelfAligningBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2249

        return self.__parent__._cast(_2249.LoadedSelfAligningBallBearingResults)

    @property
    def loaded_spherical_roller_radial_bearing_results(
        self: "CastSelf",
    ) -> "_2253.LoadedSphericalRollerRadialBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2253

        return self.__parent__._cast(_2253.LoadedSphericalRollerRadialBearingResults)

    @property
    def loaded_spherical_roller_thrust_bearing_results(
        self: "CastSelf",
    ) -> "_2256.LoadedSphericalRollerThrustBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2256

        return self.__parent__._cast(_2256.LoadedSphericalRollerThrustBearingResults)

    @property
    def loaded_taper_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2261.LoadedTaperRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2261

        return self.__parent__._cast(_2261.LoadedTaperRollerBearingResults)

    @property
    def loaded_three_point_contact_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2264.LoadedThreePointContactBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2264

        return self.__parent__._cast(_2264.LoadedThreePointContactBallBearingResults)

    @property
    def loaded_thrust_ball_bearing_results(
        self: "CastSelf",
    ) -> "_2267.LoadedThrustBallBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2267

        return self.__parent__._cast(_2267.LoadedThrustBallBearingResults)

    @property
    def loaded_toroidal_roller_bearing_results(
        self: "CastSelf",
    ) -> "_2270.LoadedToroidalRollerBearingResults":
        from mastapy._private.bearings.bearing_results.rolling import _2270

        return self.__parent__._cast(_2270.LoadedToroidalRollerBearingResults)

    @property
    def loaded_fluid_film_bearing_results(
        self: "CastSelf",
    ) -> "_2334.LoadedFluidFilmBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2334

        return self.__parent__._cast(_2334.LoadedFluidFilmBearingResults)

    @property
    def loaded_grease_filled_journal_bearing_results(
        self: "CastSelf",
    ) -> "_2335.LoadedGreaseFilledJournalBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2335

        return self.__parent__._cast(_2335.LoadedGreaseFilledJournalBearingResults)

    @property
    def loaded_pad_fluid_film_bearing_results(
        self: "CastSelf",
    ) -> "_2336.LoadedPadFluidFilmBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2336

        return self.__parent__._cast(_2336.LoadedPadFluidFilmBearingResults)

    @property
    def loaded_plain_journal_bearing_results(
        self: "CastSelf",
    ) -> "_2337.LoadedPlainJournalBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2337

        return self.__parent__._cast(_2337.LoadedPlainJournalBearingResults)

    @property
    def loaded_plain_oil_fed_journal_bearing(
        self: "CastSelf",
    ) -> "_2339.LoadedPlainOilFedJournalBearing":
        from mastapy._private.bearings.bearing_results.fluid_film import _2339

        return self.__parent__._cast(_2339.LoadedPlainOilFedJournalBearing)

    @property
    def loaded_tilting_pad_journal_bearing_results(
        self: "CastSelf",
    ) -> "_2342.LoadedTiltingPadJournalBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2342

        return self.__parent__._cast(_2342.LoadedTiltingPadJournalBearingResults)

    @property
    def loaded_tilting_pad_thrust_bearing_results(
        self: "CastSelf",
    ) -> "_2343.LoadedTiltingPadThrustBearingResults":
        from mastapy._private.bearings.bearing_results.fluid_film import _2343

        return self.__parent__._cast(_2343.LoadedTiltingPadThrustBearingResults)

    @property
    def loaded_bearing_results(self: "CastSelf") -> "LoadedBearingResults":
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
class LoadedBearingResults(_2083.BearingLoadCaseResultsLightweight):
    """LoadedBearingResults

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_BEARING_RESULTS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def angle_of_gravity_from_z_axis(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AngleOfGravityFromZAxis")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def axial_displacement_preload(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "AxialDisplacementPreload")

        if temp is None:
            return 0.0

        return temp

    @axial_displacement_preload.setter
    @exception_bridge
    @enforce_parameter_types
    def axial_displacement_preload(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "AxialDisplacementPreload",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def duration(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "Duration")

        if temp is None:
            return 0.0

        return temp

    @duration.setter
    @exception_bridge
    @enforce_parameter_types
    def duration(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "Duration", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def force_results_are_overridden(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ForceResultsAreOverridden")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def inner_ring_angular_rotation(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "InnerRingAngularRotation")

        if temp is None:
            return 0.0

        return temp

    @inner_ring_angular_rotation.setter
    @exception_bridge
    @enforce_parameter_types
    def inner_ring_angular_rotation(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "InnerRingAngularRotation",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def inner_ring_angular_velocity(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "InnerRingAngularVelocity")

        if temp is None:
            return 0.0

        return temp

    @inner_ring_angular_velocity.setter
    @exception_bridge
    @enforce_parameter_types
    def inner_ring_angular_velocity(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "InnerRingAngularVelocity",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def orientation(self: "Self") -> "_2171.Orientations":
        """mastapy.bearings.bearing_results.Orientations"""
        temp = pythonnet_property_get(self.wrapped, "Orientation")

        if temp is None:
            return None

        value = conversion.pn_to_mp_enum(
            temp, "SMT.MastaAPI.Bearings.BearingResults.Orientations"
        )

        if value is None:
            return None

        return constructor.new_from_mastapy(
            "mastapy._private.bearings.bearing_results._2171", "Orientations"
        )(value)

    @orientation.setter
    @exception_bridge
    @enforce_parameter_types
    def orientation(self: "Self", value: "_2171.Orientations") -> None:
        value = conversion.mp_to_pn_enum(
            value, "SMT.MastaAPI.Bearings.BearingResults.Orientations"
        )
        pythonnet_property_set(self.wrapped, "Orientation", value)

    @property
    @exception_bridge
    def outer_ring_angular_rotation(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "OuterRingAngularRotation")

        if temp is None:
            return 0.0

        return temp

    @outer_ring_angular_rotation.setter
    @exception_bridge
    @enforce_parameter_types
    def outer_ring_angular_rotation(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "OuterRingAngularRotation",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def outer_ring_angular_velocity(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "OuterRingAngularVelocity")

        if temp is None:
            return 0.0

        return temp

    @outer_ring_angular_velocity.setter
    @exception_bridge
    @enforce_parameter_types
    def outer_ring_angular_velocity(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "OuterRingAngularVelocity",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def relative_angular_velocity(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RelativeAngularVelocity")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def relative_axial_displacement(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RelativeAxialDisplacement")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def relative_radial_displacement(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RelativeRadialDisplacement")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def signed_relative_angular_velocity(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SignedRelativeAngularVelocity")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def specified_axial_internal_clearance(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "SpecifiedAxialInternalClearance")

        if temp is None:
            return 0.0

        return temp

    @specified_axial_internal_clearance.setter
    @exception_bridge
    @enforce_parameter_types
    def specified_axial_internal_clearance(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "SpecifiedAxialInternalClearance",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def specified_radial_internal_clearance(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "SpecifiedRadialInternalClearance")

        if temp is None:
            return 0.0

        return temp

    @specified_radial_internal_clearance.setter
    @exception_bridge
    @enforce_parameter_types
    def specified_radial_internal_clearance(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "SpecifiedRadialInternalClearance",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def bearing(self: "Self") -> "_2345.BearingDesign":
        """mastapy.bearings.bearing_designs.BearingDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Bearing")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def force_on_inner_race(
        self: "Self",
    ) -> "_1753.VectorWithLinearAndAngularComponents":
        """mastapy.math_utility.measured_vectors.VectorWithLinearAndAngularComponents

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ForceOnInnerRace")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def ring_results(self: "Self") -> "List[_2281.RingForceAndDisplacement]":
        """List[mastapy.bearings.bearing_results.rolling.RingForceAndDisplacement]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RingResults")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedBearingResults":
        """Cast to another type.

        Returns:
            _Cast_LoadedBearingResults
        """
        return _Cast_LoadedBearingResults(self)
