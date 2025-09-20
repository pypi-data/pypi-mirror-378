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
from mastapy._private.bearings.tolerances import _2111

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="EnumWithSelectedValue_BearingToleranceClass")


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_BearingToleranceClass",)


class EnumWithSelectedValue_BearingToleranceClass(
    mixins.EnumWithSelectedValueMixin, Enum
):
    """EnumWithSelectedValue_BearingToleranceClass

    A specific implementation of 'EnumWithSelectedValue' for 'BearingToleranceClass' types.
    """

    __qualname__ = "BearingToleranceClass"

    @classmethod
    def wrapper_type(cls: "Type[EnumWithSelectedValue_BearingToleranceClass]") -> "Any":
        """Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _ENUM_WITH_SELECTED_VALUE

    @classmethod
    def wrapped_type(
        cls: "Type[EnumWithSelectedValue_BearingToleranceClass]",
    ) -> "_2111.BearingToleranceClass":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _2111.BearingToleranceClass
        """
        return _2111.BearingToleranceClass

    @classmethod
    def implicit_type(
        cls: "Type[EnumWithSelectedValue_BearingToleranceClass]",
    ) -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _2111.BearingToleranceClass.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_2111.BearingToleranceClass":
        """mastapy.bearings.tolerances.BearingToleranceClass

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(self: "Self") -> "List[_2111.BearingToleranceClass]":
        """List[mastapy.bearings.tolerances.BearingToleranceClass]

        Note:
            This property is readonly.
        """
        return None
