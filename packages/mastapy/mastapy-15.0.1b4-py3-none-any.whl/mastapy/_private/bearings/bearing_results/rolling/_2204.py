"""LoadedAsymmetricSphericalRollerBearingStripLoadResults"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.bearings.bearing_results.rolling import _2194

_LOADED_ASYMMETRIC_SPHERICAL_ROLLER_BEARING_STRIP_LOAD_RESULTS = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling",
    "LoadedAsymmetricSphericalRollerBearingStripLoadResults",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results.rolling import _2244

    Self = TypeVar(
        "Self", bound="LoadedAsymmetricSphericalRollerBearingStripLoadResults"
    )
    CastSelf = TypeVar(
        "CastSelf",
        bound="LoadedAsymmetricSphericalRollerBearingStripLoadResults._Cast_LoadedAsymmetricSphericalRollerBearingStripLoadResults",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedAsymmetricSphericalRollerBearingStripLoadResults",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedAsymmetricSphericalRollerBearingStripLoadResults:
    """Special nested class for casting LoadedAsymmetricSphericalRollerBearingStripLoadResults to subclasses."""

    __parent__: "LoadedAsymmetricSphericalRollerBearingStripLoadResults"

    @property
    def loaded_abstract_spherical_roller_bearing_strip_load_results(
        self: "CastSelf",
    ) -> "_2194.LoadedAbstractSphericalRollerBearingStripLoadResults":
        return self.__parent__._cast(
            _2194.LoadedAbstractSphericalRollerBearingStripLoadResults
        )

    @property
    def loaded_roller_strip_load_results(
        self: "CastSelf",
    ) -> "_2244.LoadedRollerStripLoadResults":
        from mastapy._private.bearings.bearing_results.rolling import _2244

        return self.__parent__._cast(_2244.LoadedRollerStripLoadResults)

    @property
    def loaded_asymmetric_spherical_roller_bearing_strip_load_results(
        self: "CastSelf",
    ) -> "LoadedAsymmetricSphericalRollerBearingStripLoadResults":
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
class LoadedAsymmetricSphericalRollerBearingStripLoadResults(
    _2194.LoadedAbstractSphericalRollerBearingStripLoadResults
):
    """LoadedAsymmetricSphericalRollerBearingStripLoadResults

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = (
        _LOADED_ASYMMETRIC_SPHERICAL_ROLLER_BEARING_STRIP_LOAD_RESULTS
    )

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_LoadedAsymmetricSphericalRollerBearingStripLoadResults":
        """Cast to another type.

        Returns:
            _Cast_LoadedAsymmetricSphericalRollerBearingStripLoadResults
        """
        return _Cast_LoadedAsymmetricSphericalRollerBearingStripLoadResults(self)
