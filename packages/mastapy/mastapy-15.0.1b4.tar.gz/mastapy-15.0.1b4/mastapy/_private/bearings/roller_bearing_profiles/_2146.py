"""RollerBearingProfile"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

_ROLLER_BEARING_PROFILE = python_net_import(
    "SMT.MastaAPI.Bearings.RollerBearingProfiles", "RollerBearingProfile"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.roller_bearing_profiles import (
        _2138,
        _2139,
        _2140,
        _2141,
        _2142,
        _2143,
        _2144,
        _2145,
        _2147,
        _2148,
    )

    Self = TypeVar("Self", bound="RollerBearingProfile")
    CastSelf = TypeVar(
        "CastSelf", bound="RollerBearingProfile._Cast_RollerBearingProfile"
    )


__docformat__ = "restructuredtext en"
__all__ = ("RollerBearingProfile",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_RollerBearingProfile:
    """Special nested class for casting RollerBearingProfile to subclasses."""

    __parent__: "RollerBearingProfile"

    @property
    def roller_bearing_conical_profile(
        self: "CastSelf",
    ) -> "_2138.RollerBearingConicalProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2138

        return self.__parent__._cast(_2138.RollerBearingConicalProfile)

    @property
    def roller_bearing_crowned_profile(
        self: "CastSelf",
    ) -> "_2139.RollerBearingCrownedProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2139

        return self.__parent__._cast(_2139.RollerBearingCrownedProfile)

    @property
    def roller_bearing_din_lundberg_profile(
        self: "CastSelf",
    ) -> "_2140.RollerBearingDinLundbergProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2140

        return self.__parent__._cast(_2140.RollerBearingDinLundbergProfile)

    @property
    def roller_bearing_flat_profile(
        self: "CastSelf",
    ) -> "_2141.RollerBearingFlatProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2141

        return self.__parent__._cast(_2141.RollerBearingFlatProfile)

    @property
    def roller_bearing_fujiwara_kawase_profile(
        self: "CastSelf",
    ) -> "_2142.RollerBearingFujiwaraKawaseProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2142

        return self.__parent__._cast(_2142.RollerBearingFujiwaraKawaseProfile)

    @property
    def roller_bearing_johns_gohar_profile(
        self: "CastSelf",
    ) -> "_2143.RollerBearingJohnsGoharProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2143

        return self.__parent__._cast(_2143.RollerBearingJohnsGoharProfile)

    @property
    def roller_bearing_load_dependent_profile(
        self: "CastSelf",
    ) -> "_2144.RollerBearingLoadDependentProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2144

        return self.__parent__._cast(_2144.RollerBearingLoadDependentProfile)

    @property
    def roller_bearing_lundberg_profile(
        self: "CastSelf",
    ) -> "_2145.RollerBearingLundbergProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2145

        return self.__parent__._cast(_2145.RollerBearingLundbergProfile)

    @property
    def roller_bearing_tangential_crowned_profile(
        self: "CastSelf",
    ) -> "_2147.RollerBearingTangentialCrownedProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2147

        return self.__parent__._cast(_2147.RollerBearingTangentialCrownedProfile)

    @property
    def roller_bearing_user_specified_profile(
        self: "CastSelf",
    ) -> "_2148.RollerBearingUserSpecifiedProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2148

        return self.__parent__._cast(_2148.RollerBearingUserSpecifiedProfile)

    @property
    def roller_bearing_profile(self: "CastSelf") -> "RollerBearingProfile":
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
class RollerBearingProfile(_0.APIBase):
    """RollerBearingProfile

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ROLLER_BEARING_PROFILE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def covers_two_rows_of_elements(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "CoversTwoRowsOfElements")

        if temp is None:
            return False

        return temp

    @covers_two_rows_of_elements.setter
    @exception_bridge
    @enforce_parameter_types
    def covers_two_rows_of_elements(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "CoversTwoRowsOfElements",
            bool(value) if value is not None else False,
        )

    @property
    def cast_to(self: "Self") -> "_Cast_RollerBearingProfile":
        """Cast to another type.

        Returns:
            _Cast_RollerBearingProfile
        """
        return _Cast_RollerBearingProfile(self)
