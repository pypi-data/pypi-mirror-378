"""Implementations of 'EnumWithSelectedValue' in Python.

As Python does not have an implicit operator, this is the next
best solution for implementing these types properly.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from mastapy._private._internal import mixins
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.bearings.bearing_results import _2173

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="EnumWithSelectedValue_LoadedBallElementPropertyType")


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_LoadedBallElementPropertyType",)


class EnumWithSelectedValue_LoadedBallElementPropertyType(
    mixins.EnumWithSelectedValueMixin, Enum
):
    """EnumWithSelectedValue_LoadedBallElementPropertyType

    A specific implementation of 'EnumWithSelectedValue' for 'LoadedBallElementPropertyType' types.
    """

    __qualname__ = "LoadedBallElementPropertyType"

    @classmethod
    def wrapper_type(
        cls: "Type[EnumWithSelectedValue_LoadedBallElementPropertyType]",
    ) -> "Any":
        """Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _ENUM_WITH_SELECTED_VALUE

    @classmethod
    def wrapped_type(
        cls: "Type[EnumWithSelectedValue_LoadedBallElementPropertyType]",
    ) -> "_2173.LoadedBallElementPropertyType":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _2173.LoadedBallElementPropertyType
        """
        return _2173.LoadedBallElementPropertyType

    @classmethod
    def implicit_type(
        cls: "Type[EnumWithSelectedValue_LoadedBallElementPropertyType]",
    ) -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _2173.LoadedBallElementPropertyType.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_2173.LoadedBallElementPropertyType":
        """mastapy.bearings.bearing_results.LoadedBallElementPropertyType

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(self: "Self") -> "List[_2173.LoadedBallElementPropertyType]":
        """List[mastapy.bearings.bearing_results.LoadedBallElementPropertyType]

        Note:
            This property is readonly.
        """
        return None
