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
from mastapy._private.math_utility import _1690

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="EnumWithSelectedValue_DynamicsResponseScaling")


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_DynamicsResponseScaling",)


class EnumWithSelectedValue_DynamicsResponseScaling(
    mixins.EnumWithSelectedValueMixin, Enum
):
    """EnumWithSelectedValue_DynamicsResponseScaling

    A specific implementation of 'EnumWithSelectedValue' for 'DynamicsResponseScaling' types.
    """

    __qualname__ = "DynamicsResponseScaling"

    @classmethod
    def wrapper_type(
        cls: "Type[EnumWithSelectedValue_DynamicsResponseScaling]",
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
        cls: "Type[EnumWithSelectedValue_DynamicsResponseScaling]",
    ) -> "_1690.DynamicsResponseScaling":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _1690.DynamicsResponseScaling
        """
        return _1690.DynamicsResponseScaling

    @classmethod
    def implicit_type(
        cls: "Type[EnumWithSelectedValue_DynamicsResponseScaling]",
    ) -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _1690.DynamicsResponseScaling.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_1690.DynamicsResponseScaling":
        """mastapy.math_utility.DynamicsResponseScaling

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(self: "Self") -> "List[_1690.DynamicsResponseScaling]":
        """List[mastapy.math_utility.DynamicsResponseScaling]

        Note:
            This property is readonly.
        """
        return None
