"""DetailedBearing"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.bearings.bearing_designs import _2349

_DETAILED_BEARING = python_net_import(
    "SMT.MastaAPI.Bearings.BearingDesigns", "DetailedBearing"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_designs import _2345
    from mastapy._private.bearings.bearing_designs.fluid_film import (
        _2403,
        _2405,
        _2407,
        _2409,
        _2410,
        _2411,
    )
    from mastapy._private.bearings.bearing_designs.rolling import (
        _2350,
        _2351,
        _2352,
        _2353,
        _2354,
        _2355,
        _2357,
        _2363,
        _2364,
        _2365,
        _2369,
        _2374,
        _2375,
        _2376,
        _2377,
        _2380,
        _2382,
        _2385,
        _2386,
        _2387,
        _2388,
        _2389,
        _2390,
    )

    Self = TypeVar("Self", bound="DetailedBearing")
    CastSelf = TypeVar("CastSelf", bound="DetailedBearing._Cast_DetailedBearing")


__docformat__ = "restructuredtext en"
__all__ = ("DetailedBearing",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_DetailedBearing:
    """Special nested class for casting DetailedBearing to subclasses."""

    __parent__: "DetailedBearing"

    @property
    def non_linear_bearing(self: "CastSelf") -> "_2349.NonLinearBearing":
        return self.__parent__._cast(_2349.NonLinearBearing)

    @property
    def bearing_design(self: "CastSelf") -> "_2345.BearingDesign":
        from mastapy._private.bearings.bearing_designs import _2345

        return self.__parent__._cast(_2345.BearingDesign)

    @property
    def angular_contact_ball_bearing(
        self: "CastSelf",
    ) -> "_2350.AngularContactBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2350

        return self.__parent__._cast(_2350.AngularContactBallBearing)

    @property
    def angular_contact_thrust_ball_bearing(
        self: "CastSelf",
    ) -> "_2351.AngularContactThrustBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2351

        return self.__parent__._cast(_2351.AngularContactThrustBallBearing)

    @property
    def asymmetric_spherical_roller_bearing(
        self: "CastSelf",
    ) -> "_2352.AsymmetricSphericalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2352

        return self.__parent__._cast(_2352.AsymmetricSphericalRollerBearing)

    @property
    def axial_thrust_cylindrical_roller_bearing(
        self: "CastSelf",
    ) -> "_2353.AxialThrustCylindricalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2353

        return self.__parent__._cast(_2353.AxialThrustCylindricalRollerBearing)

    @property
    def axial_thrust_needle_roller_bearing(
        self: "CastSelf",
    ) -> "_2354.AxialThrustNeedleRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2354

        return self.__parent__._cast(_2354.AxialThrustNeedleRollerBearing)

    @property
    def ball_bearing(self: "CastSelf") -> "_2355.BallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2355

        return self.__parent__._cast(_2355.BallBearing)

    @property
    def barrel_roller_bearing(self: "CastSelf") -> "_2357.BarrelRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2357

        return self.__parent__._cast(_2357.BarrelRollerBearing)

    @property
    def crossed_roller_bearing(self: "CastSelf") -> "_2363.CrossedRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2363

        return self.__parent__._cast(_2363.CrossedRollerBearing)

    @property
    def cylindrical_roller_bearing(
        self: "CastSelf",
    ) -> "_2364.CylindricalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2364

        return self.__parent__._cast(_2364.CylindricalRollerBearing)

    @property
    def deep_groove_ball_bearing(self: "CastSelf") -> "_2365.DeepGrooveBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2365

        return self.__parent__._cast(_2365.DeepGrooveBallBearing)

    @property
    def four_point_contact_ball_bearing(
        self: "CastSelf",
    ) -> "_2369.FourPointContactBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2369

        return self.__parent__._cast(_2369.FourPointContactBallBearing)

    @property
    def multi_point_contact_ball_bearing(
        self: "CastSelf",
    ) -> "_2374.MultiPointContactBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2374

        return self.__parent__._cast(_2374.MultiPointContactBallBearing)

    @property
    def needle_roller_bearing(self: "CastSelf") -> "_2375.NeedleRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2375

        return self.__parent__._cast(_2375.NeedleRollerBearing)

    @property
    def non_barrel_roller_bearing(self: "CastSelf") -> "_2376.NonBarrelRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2376

        return self.__parent__._cast(_2376.NonBarrelRollerBearing)

    @property
    def roller_bearing(self: "CastSelf") -> "_2377.RollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2377

        return self.__parent__._cast(_2377.RollerBearing)

    @property
    def rolling_bearing(self: "CastSelf") -> "_2380.RollingBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2380

        return self.__parent__._cast(_2380.RollingBearing)

    @property
    def self_aligning_ball_bearing(self: "CastSelf") -> "_2382.SelfAligningBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2382

        return self.__parent__._cast(_2382.SelfAligningBallBearing)

    @property
    def spherical_roller_bearing(self: "CastSelf") -> "_2385.SphericalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2385

        return self.__parent__._cast(_2385.SphericalRollerBearing)

    @property
    def spherical_roller_thrust_bearing(
        self: "CastSelf",
    ) -> "_2386.SphericalRollerThrustBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2386

        return self.__parent__._cast(_2386.SphericalRollerThrustBearing)

    @property
    def taper_roller_bearing(self: "CastSelf") -> "_2387.TaperRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2387

        return self.__parent__._cast(_2387.TaperRollerBearing)

    @property
    def three_point_contact_ball_bearing(
        self: "CastSelf",
    ) -> "_2388.ThreePointContactBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2388

        return self.__parent__._cast(_2388.ThreePointContactBallBearing)

    @property
    def thrust_ball_bearing(self: "CastSelf") -> "_2389.ThrustBallBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2389

        return self.__parent__._cast(_2389.ThrustBallBearing)

    @property
    def toroidal_roller_bearing(self: "CastSelf") -> "_2390.ToroidalRollerBearing":
        from mastapy._private.bearings.bearing_designs.rolling import _2390

        return self.__parent__._cast(_2390.ToroidalRollerBearing)

    @property
    def pad_fluid_film_bearing(self: "CastSelf") -> "_2403.PadFluidFilmBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2403

        return self.__parent__._cast(_2403.PadFluidFilmBearing)

    @property
    def plain_grease_filled_journal_bearing(
        self: "CastSelf",
    ) -> "_2405.PlainGreaseFilledJournalBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2405

        return self.__parent__._cast(_2405.PlainGreaseFilledJournalBearing)

    @property
    def plain_journal_bearing(self: "CastSelf") -> "_2407.PlainJournalBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2407

        return self.__parent__._cast(_2407.PlainJournalBearing)

    @property
    def plain_oil_fed_journal_bearing(
        self: "CastSelf",
    ) -> "_2409.PlainOilFedJournalBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2409

        return self.__parent__._cast(_2409.PlainOilFedJournalBearing)

    @property
    def tilting_pad_journal_bearing(
        self: "CastSelf",
    ) -> "_2410.TiltingPadJournalBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2410

        return self.__parent__._cast(_2410.TiltingPadJournalBearing)

    @property
    def tilting_pad_thrust_bearing(self: "CastSelf") -> "_2411.TiltingPadThrustBearing":
        from mastapy._private.bearings.bearing_designs.fluid_film import _2411

        return self.__parent__._cast(_2411.TiltingPadThrustBearing)

    @property
    def detailed_bearing(self: "CastSelf") -> "DetailedBearing":
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
class DetailedBearing(_2349.NonLinearBearing):
    """DetailedBearing

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _DETAILED_BEARING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_DetailedBearing":
        """Cast to another type.

        Returns:
            _Cast_DetailedBearing
        """
        return _Cast_DetailedBearing(self)
