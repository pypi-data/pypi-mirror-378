"""NamedSelectionEdge"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.math_utility import _1708

_NAMED_SELECTION_EDGE = python_net_import(
    "SMT.MastaAPI.MathUtility", "NamedSelectionEdge"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="NamedSelectionEdge")
    CastSelf = TypeVar("CastSelf", bound="NamedSelectionEdge._Cast_NamedSelectionEdge")


__docformat__ = "restructuredtext en"
__all__ = ("NamedSelectionEdge",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_NamedSelectionEdge:
    """Special nested class for casting NamedSelectionEdge to subclasses."""

    __parent__: "NamedSelectionEdge"

    @property
    def named_selection(self: "CastSelf") -> "_1708.NamedSelection":
        return self.__parent__._cast(_1708.NamedSelection)

    @property
    def named_selection_edge(self: "CastSelf") -> "NamedSelectionEdge":
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
class NamedSelectionEdge(_1708.NamedSelection):
    """NamedSelectionEdge

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _NAMED_SELECTION_EDGE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_NamedSelectionEdge":
        """Cast to another type.

        Returns:
            _Cast_NamedSelectionEdge
        """
        return _Cast_NamedSelectionEdge(self)
