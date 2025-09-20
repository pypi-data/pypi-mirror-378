"""LoadedRollerStripLoadResults"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

_LOADED_ROLLER_STRIP_LOAD_RESULTS = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling", "LoadedRollerStripLoadResults"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results.rolling import (
        _2194,
        _2204,
        _2239,
        _2255,
        _2272,
    )

    Self = TypeVar("Self", bound="LoadedRollerStripLoadResults")
    CastSelf = TypeVar(
        "CastSelf",
        bound="LoadedRollerStripLoadResults._Cast_LoadedRollerStripLoadResults",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedRollerStripLoadResults",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedRollerStripLoadResults:
    """Special nested class for casting LoadedRollerStripLoadResults to subclasses."""

    __parent__: "LoadedRollerStripLoadResults"

    @property
    def loaded_abstract_spherical_roller_bearing_strip_load_results(
        self: "CastSelf",
    ) -> "_2194.LoadedAbstractSphericalRollerBearingStripLoadResults":
        from mastapy._private.bearings.bearing_results.rolling import _2194

        return self.__parent__._cast(
            _2194.LoadedAbstractSphericalRollerBearingStripLoadResults
        )

    @property
    def loaded_asymmetric_spherical_roller_bearing_strip_load_results(
        self: "CastSelf",
    ) -> "_2204.LoadedAsymmetricSphericalRollerBearingStripLoadResults":
        from mastapy._private.bearings.bearing_results.rolling import _2204

        return self.__parent__._cast(
            _2204.LoadedAsymmetricSphericalRollerBearingStripLoadResults
        )

    @property
    def loaded_non_barrel_roller_bearing_strip_load_results(
        self: "CastSelf",
    ) -> "_2239.LoadedNonBarrelRollerBearingStripLoadResults":
        from mastapy._private.bearings.bearing_results.rolling import _2239

        return self.__parent__._cast(_2239.LoadedNonBarrelRollerBearingStripLoadResults)

    @property
    def loaded_spherical_roller_radial_bearing_strip_load_results(
        self: "CastSelf",
    ) -> "_2255.LoadedSphericalRollerRadialBearingStripLoadResults":
        from mastapy._private.bearings.bearing_results.rolling import _2255

        return self.__parent__._cast(
            _2255.LoadedSphericalRollerRadialBearingStripLoadResults
        )

    @property
    def loaded_toroidal_roller_bearing_strip_load_results(
        self: "CastSelf",
    ) -> "_2272.LoadedToroidalRollerBearingStripLoadResults":
        from mastapy._private.bearings.bearing_results.rolling import _2272

        return self.__parent__._cast(_2272.LoadedToroidalRollerBearingStripLoadResults)

    @property
    def loaded_roller_strip_load_results(
        self: "CastSelf",
    ) -> "LoadedRollerStripLoadResults":
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
class LoadedRollerStripLoadResults(_0.APIBase):
    """LoadedRollerStripLoadResults

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_ROLLER_STRIP_LOAD_RESULTS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedRollerStripLoadResults":
        """Cast to another type.

        Returns:
            _Cast_LoadedRollerStripLoadResults
        """
        return _Cast_LoadedRollerStripLoadResults(self)
