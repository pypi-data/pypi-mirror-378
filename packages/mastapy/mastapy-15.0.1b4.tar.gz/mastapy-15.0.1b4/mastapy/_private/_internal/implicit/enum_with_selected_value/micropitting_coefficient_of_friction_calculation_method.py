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
from mastapy._private.gears import _429

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar(
        "Self",
        bound="EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod",
    )


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod",)


class EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod(
    mixins.EnumWithSelectedValueMixin, Enum
):
    """EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod

    A specific implementation of 'EnumWithSelectedValue' for 'MicropittingCoefficientOfFrictionCalculationMethod' types.
    """

    __qualname__ = "MicropittingCoefficientOfFrictionCalculationMethod"

    @classmethod
    def wrapper_type(
        cls: "Type[EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod]",
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
        cls: "Type[EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod]",
    ) -> "_429.MicropittingCoefficientOfFrictionCalculationMethod":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _429.MicropittingCoefficientOfFrictionCalculationMethod
        """
        return _429.MicropittingCoefficientOfFrictionCalculationMethod

    @classmethod
    def implicit_type(
        cls: "Type[EnumWithSelectedValue_MicropittingCoefficientOfFrictionCalculationMethod]",
    ) -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _429.MicropittingCoefficientOfFrictionCalculationMethod.type_()

    @property
    @exception_bridge
    def selected_value(
        self: "Self",
    ) -> "_429.MicropittingCoefficientOfFrictionCalculationMethod":
        """mastapy.gears.MicropittingCoefficientOfFrictionCalculationMethod

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(
        self: "Self",
    ) -> "List[_429.MicropittingCoefficientOfFrictionCalculationMethod]":
        """List[mastapy.gears.MicropittingCoefficientOfFrictionCalculationMethod]

        Note:
            This property is readonly.
        """
        return None
