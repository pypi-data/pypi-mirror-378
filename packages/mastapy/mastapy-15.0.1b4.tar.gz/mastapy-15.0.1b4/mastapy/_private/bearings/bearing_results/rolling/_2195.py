"""LoadedAngularContactBallBearingElement"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.bearings.bearing_results.rolling import _2213

_LOADED_ANGULAR_CONTACT_BALL_BEARING_ELEMENT = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling",
    "LoadedAngularContactBallBearingElement",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings.bearing_results.rolling import _2198, _2227

    Self = TypeVar("Self", bound="LoadedAngularContactBallBearingElement")
    CastSelf = TypeVar(
        "CastSelf",
        bound="LoadedAngularContactBallBearingElement._Cast_LoadedAngularContactBallBearingElement",
    )


__docformat__ = "restructuredtext en"
__all__ = ("LoadedAngularContactBallBearingElement",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_LoadedAngularContactBallBearingElement:
    """Special nested class for casting LoadedAngularContactBallBearingElement to subclasses."""

    __parent__: "LoadedAngularContactBallBearingElement"

    @property
    def loaded_ball_bearing_element(
        self: "CastSelf",
    ) -> "_2213.LoadedBallBearingElement":
        return self.__parent__._cast(_2213.LoadedBallBearingElement)

    @property
    def loaded_element(self: "CastSelf") -> "_2227.LoadedElement":
        from mastapy._private.bearings.bearing_results.rolling import _2227

        return self.__parent__._cast(_2227.LoadedElement)

    @property
    def loaded_angular_contact_thrust_ball_bearing_element(
        self: "CastSelf",
    ) -> "_2198.LoadedAngularContactThrustBallBearingElement":
        from mastapy._private.bearings.bearing_results.rolling import _2198

        return self.__parent__._cast(_2198.LoadedAngularContactThrustBallBearingElement)

    @property
    def loaded_angular_contact_ball_bearing_element(
        self: "CastSelf",
    ) -> "LoadedAngularContactBallBearingElement":
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
class LoadedAngularContactBallBearingElement(_2213.LoadedBallBearingElement):
    """LoadedAngularContactBallBearingElement

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _LOADED_ANGULAR_CONTACT_BALL_BEARING_ELEMENT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_LoadedAngularContactBallBearingElement":
        """Cast to another type.

        Returns:
            _Cast_LoadedAngularContactBallBearingElement
        """
        return _Cast_LoadedAngularContactBallBearingElement(self)
