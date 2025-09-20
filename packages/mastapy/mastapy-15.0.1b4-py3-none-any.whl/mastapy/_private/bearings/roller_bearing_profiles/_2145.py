"""RollerBearingLundbergProfile"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.bearings.roller_bearing_profiles import _2144

_ROLLER_BEARING_LUNDBERG_PROFILE = python_net_import(
    "SMT.MastaAPI.Bearings.RollerBearingProfiles", "RollerBearingLundbergProfile"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.roller_bearing_profiles import _2146

    Self = TypeVar("Self", bound="RollerBearingLundbergProfile")
    CastSelf = TypeVar(
        "CastSelf",
        bound="RollerBearingLundbergProfile._Cast_RollerBearingLundbergProfile",
    )


__docformat__ = "restructuredtext en"
__all__ = ("RollerBearingLundbergProfile",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_RollerBearingLundbergProfile:
    """Special nested class for casting RollerBearingLundbergProfile to subclasses."""

    __parent__: "RollerBearingLundbergProfile"

    @property
    def roller_bearing_load_dependent_profile(
        self: "CastSelf",
    ) -> "_2144.RollerBearingLoadDependentProfile":
        return self.__parent__._cast(_2144.RollerBearingLoadDependentProfile)

    @property
    def roller_bearing_profile(self: "CastSelf") -> "_2146.RollerBearingProfile":
        from mastapy._private.bearings.roller_bearing_profiles import _2146

        return self.__parent__._cast(_2146.RollerBearingProfile)

    @property
    def roller_bearing_lundberg_profile(
        self: "CastSelf",
    ) -> "RollerBearingLundbergProfile":
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
class RollerBearingLundbergProfile(_2144.RollerBearingLoadDependentProfile):
    """RollerBearingLundbergProfile

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ROLLER_BEARING_LUNDBERG_PROFILE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_RollerBearingLundbergProfile":
        """Cast to another type.

        Returns:
            _Cast_RollerBearingLundbergProfile
        """
        return _Cast_RollerBearingLundbergProfile(self)
