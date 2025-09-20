"""LoadedBallBearingRow"""

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
from mastapy._private.bearings.bearing_results.rolling import _2247

_LOADED_BALL_BEARING_ROW = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling", "LoadedBallBearingRow"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.bearings.bearing_results.rolling import (
        _2197,
        _2200,
        _2214,
        _2215,
        _2226,
        _2231,
        _2250,
        _2265,
        _2268,
    )

    Self = TypeVar("Self", bound="LoadedBallBearingRow")
    CastSelf = TypeVar(
        "CastSelf", bound="LoadedBallBearingRow._Cast_LoadedBallBearingRow"
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedBallBearingRow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedBallBearingRow:
    """Special nested class for casting LoadedBallBearingRow to subclasses."""

    __parent__: "LoadedBallBearingRow"

    @property
    def loaded_rolling_bearing_row(self: "CastSelf") -> "_2247.LoadedRollingBearingRow":
        return self.__parent__._cast(_2247.LoadedRollingBearingRow)

    @property
    def loaded_angular_contact_ball_bearing_row(
        self: "CastSelf",
    ) -> "_2197.LoadedAngularContactBallBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2197

        return self.__parent__._cast(_2197.LoadedAngularContactBallBearingRow)

    @property
    def loaded_angular_contact_thrust_ball_bearing_row(
        self: "CastSelf",
    ) -> "_2200.LoadedAngularContactThrustBallBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2200

        return self.__parent__._cast(_2200.LoadedAngularContactThrustBallBearingRow)

    @property
    def loaded_deep_groove_ball_bearing_row(
        self: "CastSelf",
    ) -> "_2226.LoadedDeepGrooveBallBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2226

        return self.__parent__._cast(_2226.LoadedDeepGrooveBallBearingRow)

    @property
    def loaded_four_point_contact_ball_bearing_row(
        self: "CastSelf",
    ) -> "_2231.LoadedFourPointContactBallBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2231

        return self.__parent__._cast(_2231.LoadedFourPointContactBallBearingRow)

    @property
    def loaded_self_aligning_ball_bearing_row(
        self: "CastSelf",
    ) -> "_2250.LoadedSelfAligningBallBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2250

        return self.__parent__._cast(_2250.LoadedSelfAligningBallBearingRow)

    @property
    def loaded_three_point_contact_ball_bearing_row(
        self: "CastSelf",
    ) -> "_2265.LoadedThreePointContactBallBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2265

        return self.__parent__._cast(_2265.LoadedThreePointContactBallBearingRow)

    @property
    def loaded_thrust_ball_bearing_row(
        self: "CastSelf",
    ) -> "_2268.LoadedThrustBallBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2268

        return self.__parent__._cast(_2268.LoadedThrustBallBearingRow)

    @property
    def loaded_ball_bearing_row(self: "CastSelf") -> "LoadedBallBearingRow":
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
class LoadedBallBearingRow(_2247.LoadedRollingBearingRow):
    """LoadedBallBearingRow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_BALL_BEARING_ROW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def axial_ball_movement(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AxialBallMovement")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def dynamic_equivalent_load_inner(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DynamicEquivalentLoadInner")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def dynamic_equivalent_load_outer(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DynamicEquivalentLoadOuter")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def element_with_worst_track_truncation(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElementWithWorstTrackTruncation")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def hertzian_semi_major_dimension_highest_load_inner(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "HertzianSemiMajorDimensionHighestLoadInner"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def hertzian_semi_major_dimension_highest_load_outer(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "HertzianSemiMajorDimensionHighestLoadOuter"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def hertzian_semi_minor_dimension_highest_load_inner(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "HertzianSemiMinorDimensionHighestLoadInner"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def hertzian_semi_minor_dimension_highest_load_outer(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "HertzianSemiMinorDimensionHighestLoadOuter"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def smallest_arc_distance_of_raceway_edge_to_hertzian_contact(
        self: "Self",
    ) -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "SmallestArcDistanceOfRacewayEdgeToHertzianContact"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def track_truncation_occurring_beyond_permissible_limit(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "TrackTruncationOccurringBeyondPermissibleLimit"
        )

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def truncation_warning(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "TruncationWarning")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def worst_hertzian_ellipse_major_2b_track_truncation(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "WorstHertzianEllipseMajor2bTrackTruncation"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def loaded_bearing(self: "Self") -> "_2215.LoadedBallBearingResults":
        """mastapy.bearings.bearing_results.rolling.LoadedBallBearingResults

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "LoadedBearing")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def race_results(self: "Self") -> "List[_2214.LoadedBallBearingRaceResults]":
        """List[mastapy.bearings.bearing_results.rolling.LoadedBallBearingRaceResults]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RaceResults")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedBallBearingRow":
        """Cast to another type.

        Returns:
            _Cast_LoadedBallBearingRow
        """
        return _Cast_LoadedBallBearingRow(self)
