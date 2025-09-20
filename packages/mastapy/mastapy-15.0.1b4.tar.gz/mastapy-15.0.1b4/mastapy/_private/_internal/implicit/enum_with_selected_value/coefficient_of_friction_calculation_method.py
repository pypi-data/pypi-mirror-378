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
from mastapy._private.gears import _409

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar(
        "Self", bound="EnumWithSelectedValue_CoefficientOfFrictionCalculationMethod"
    )


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_CoefficientOfFrictionCalculationMethod",)


class EnumWithSelectedValue_CoefficientOfFrictionCalculationMethod(
    mixins.EnumWithSelectedValueMixin, Enum
):
    """EnumWithSelectedValue_CoefficientOfFrictionCalculationMethod

    A specific implementation of 'EnumWithSelectedValue' for 'CoefficientOfFrictionCalculationMethod' types.
    """

    __qualname__ = "CoefficientOfFrictionCalculationMethod"

    @classmethod
    def wrapper_type(
        cls: "Type[EnumWithSelectedValue_CoefficientOfFrictionCalculationMethod]",
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
        cls: "Type[EnumWithSelectedValue_CoefficientOfFrictionCalculationMethod]",
    ) -> "_409.CoefficientOfFrictionCalculationMethod":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _409.CoefficientOfFrictionCalculationMethod
        """
        return _409.CoefficientOfFrictionCalculationMethod

    @classmethod
    def implicit_type(
        cls: "Type[EnumWithSelectedValue_CoefficientOfFrictionCalculationMethod]",
    ) -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _409.CoefficientOfFrictionCalculationMethod.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_409.CoefficientOfFrictionCalculationMethod":
        """mastapy.gears.CoefficientOfFrictionCalculationMethod

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(
        self: "Self",
    ) -> "List[_409.CoefficientOfFrictionCalculationMethod]":
        """List[mastapy.gears.CoefficientOfFrictionCalculationMethod]

        Note:
            This property is readonly.
        """
        return None
