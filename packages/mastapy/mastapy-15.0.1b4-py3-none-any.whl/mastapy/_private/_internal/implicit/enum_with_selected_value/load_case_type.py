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
from mastapy._private.electric_machines.load_cases_and_analyses import _1548

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="EnumWithSelectedValue_LoadCaseType")


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_LoadCaseType",)


class EnumWithSelectedValue_LoadCaseType(mixins.EnumWithSelectedValueMixin, Enum):
    """EnumWithSelectedValue_LoadCaseType

    A specific implementation of 'EnumWithSelectedValue' for 'LoadCaseType' types.
    """

    __qualname__ = "LoadCaseType"

    @classmethod
    def wrapper_type(cls: "Type[EnumWithSelectedValue_LoadCaseType]") -> "Any":
        """Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _ENUM_WITH_SELECTED_VALUE

    @classmethod
    def wrapped_type(
        cls: "Type[EnumWithSelectedValue_LoadCaseType]",
    ) -> "_1548.LoadCaseType":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _1548.LoadCaseType
        """
        return _1548.LoadCaseType

    @classmethod
    def implicit_type(cls: "Type[EnumWithSelectedValue_LoadCaseType]") -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _1548.LoadCaseType.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_1548.LoadCaseType":
        """mastapy.electric_machines.load_cases_and_analyses.LoadCaseType

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(self: "Self") -> "List[_1548.LoadCaseType]":
        """List[mastapy.electric_machines.load_cases_and_analyses.LoadCaseType]

        Note:
            This property is readonly.
        """
        return None
