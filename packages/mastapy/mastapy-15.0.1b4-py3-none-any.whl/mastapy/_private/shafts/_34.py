"""ShaftProfilePointCopy"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.shafts import _33

_SHAFT_PROFILE_POINT_COPY = python_net_import(
    "SMT.MastaAPI.Shafts", "ShaftProfilePointCopy"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="ShaftProfilePointCopy")
    CastSelf = TypeVar(
        "CastSelf", bound="ShaftProfilePointCopy._Cast_ShaftProfilePointCopy"
    )


__docformat__ = "restructuredtext en"
__all__ = ("ShaftProfilePointCopy",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ShaftProfilePointCopy:
    """Special nested class for casting ShaftProfilePointCopy to subclasses."""

    __parent__: "ShaftProfilePointCopy"

    @property
    def shaft_profile_point(self: "CastSelf") -> "_33.ShaftProfilePoint":
        return self.__parent__._cast(_33.ShaftProfilePoint)

    @property
    def shaft_profile_point_copy(self: "CastSelf") -> "ShaftProfilePointCopy":
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
class ShaftProfilePointCopy(_33.ShaftProfilePoint):
    """ShaftProfilePointCopy

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SHAFT_PROFILE_POINT_COPY

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ShaftProfilePointCopy":
        """Cast to another type.

        Returns:
            _Cast_ShaftProfilePointCopy
        """
        return _Cast_ShaftProfilePointCopy(self)
