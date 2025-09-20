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
from mastapy._private.bearings.tolerances import _2110

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="EnumWithSelectedValue_InternalClearanceClass")


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_InternalClearanceClass",)


class EnumWithSelectedValue_InternalClearanceClass(
    mixins.EnumWithSelectedValueMixin, Enum
):
    """EnumWithSelectedValue_InternalClearanceClass

    A specific implementation of 'EnumWithSelectedValue' for 'InternalClearanceClass' types.
    """

    __qualname__ = "InternalClearanceClass"

    @classmethod
    def wrapper_type(
        cls: "Type[EnumWithSelectedValue_InternalClearanceClass]",
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
        cls: "Type[EnumWithSelectedValue_InternalClearanceClass]",
    ) -> "_2110.InternalClearanceClass":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _2110.InternalClearanceClass
        """
        return _2110.InternalClearanceClass

    @classmethod
    def implicit_type(
        cls: "Type[EnumWithSelectedValue_InternalClearanceClass]",
    ) -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _2110.InternalClearanceClass.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_2110.InternalClearanceClass":
        """mastapy.bearings.tolerances.InternalClearanceClass

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(self: "Self") -> "List[_2110.InternalClearanceClass]":
        """List[mastapy.bearings.tolerances.InternalClearanceClass]

        Note:
            This property is readonly.
        """
        return None
