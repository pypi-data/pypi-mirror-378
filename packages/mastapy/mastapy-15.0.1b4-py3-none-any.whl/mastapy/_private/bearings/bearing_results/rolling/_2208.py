"""LoadedAxialThrustCylindricalRollerBearingRow"""

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
from mastapy._private.bearings.bearing_results.rolling import _2238

_LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_ROW = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling",
    "LoadedAxialThrustCylindricalRollerBearingRow",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results.rolling import (
        _2207,
        _2211,
        _2243,
        _2247,
    )

    Self = TypeVar("Self", bound="LoadedAxialThrustCylindricalRollerBearingRow")
    CastSelf = TypeVar(
        "CastSelf",
        bound="LoadedAxialThrustCylindricalRollerBearingRow._Cast_LoadedAxialThrustCylindricalRollerBearingRow",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedAxialThrustCylindricalRollerBearingRow",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedAxialThrustCylindricalRollerBearingRow:
    """Special nested class for casting LoadedAxialThrustCylindricalRollerBearingRow to subclasses."""

    __parent__: "LoadedAxialThrustCylindricalRollerBearingRow"

    @property
    def loaded_non_barrel_roller_bearing_row(
        self: "CastSelf",
    ) -> "_2238.LoadedNonBarrelRollerBearingRow":
        return self.__parent__._cast(_2238.LoadedNonBarrelRollerBearingRow)

    @property
    def loaded_roller_bearing_row(self: "CastSelf") -> "_2243.LoadedRollerBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2243

        return self.__parent__._cast(_2243.LoadedRollerBearingRow)

    @property
    def loaded_rolling_bearing_row(self: "CastSelf") -> "_2247.LoadedRollingBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2247

        return self.__parent__._cast(_2247.LoadedRollingBearingRow)

    @property
    def loaded_axial_thrust_needle_roller_bearing_row(
        self: "CastSelf",
    ) -> "_2211.LoadedAxialThrustNeedleRollerBearingRow":
        from mastapy._private.bearings.bearing_results.rolling import _2211

        return self.__parent__._cast(_2211.LoadedAxialThrustNeedleRollerBearingRow)

    @property
    def loaded_axial_thrust_cylindrical_roller_bearing_row(
        self: "CastSelf",
    ) -> "LoadedAxialThrustCylindricalRollerBearingRow":
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
class LoadedAxialThrustCylindricalRollerBearingRow(
    _2238.LoadedNonBarrelRollerBearingRow
):
    """LoadedAxialThrustCylindricalRollerBearingRow

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_AXIAL_THRUST_CYLINDRICAL_ROLLER_BEARING_ROW

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def loaded_bearing(
        self: "Self",
    ) -> "_2207.LoadedAxialThrustCylindricalRollerBearingResults":
        """mastapy.bearings.bearing_results.rolling.LoadedAxialThrustCylindricalRollerBearingResults

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "LoadedBearing")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedAxialThrustCylindricalRollerBearingRow":
        """Cast to another type.

        Returns:
            _Cast_LoadedAxialThrustCylindricalRollerBearingRow
        """
        return _Cast_LoadedAxialThrustCylindricalRollerBearingRow(self)
