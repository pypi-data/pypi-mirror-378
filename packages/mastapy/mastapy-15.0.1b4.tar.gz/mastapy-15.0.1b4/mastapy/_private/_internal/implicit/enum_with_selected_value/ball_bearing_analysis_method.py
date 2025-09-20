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
from mastapy._private.bearings.bearing_results.rolling import _2177

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="EnumWithSelectedValue_BallBearingAnalysisMethod")


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_BallBearingAnalysisMethod",)


class EnumWithSelectedValue_BallBearingAnalysisMethod(
    mixins.EnumWithSelectedValueMixin, Enum
):
    """EnumWithSelectedValue_BallBearingAnalysisMethod

    A specific implementation of 'EnumWithSelectedValue' for 'BallBearingAnalysisMethod' types.
    """

    __qualname__ = "BallBearingAnalysisMethod"

    @classmethod
    def wrapper_type(
        cls: "Type[EnumWithSelectedValue_BallBearingAnalysisMethod]",
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
        cls: "Type[EnumWithSelectedValue_BallBearingAnalysisMethod]",
    ) -> "_2177.BallBearingAnalysisMethod":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _2177.BallBearingAnalysisMethod
        """
        return _2177.BallBearingAnalysisMethod

    @classmethod
    def implicit_type(
        cls: "Type[EnumWithSelectedValue_BallBearingAnalysisMethod]",
    ) -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _2177.BallBearingAnalysisMethod.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_2177.BallBearingAnalysisMethod":
        """mastapy.bearings.bearing_results.rolling.BallBearingAnalysisMethod

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(self: "Self") -> "List[_2177.BallBearingAnalysisMethod]":
        """List[mastapy.bearings.bearing_results.rolling.BallBearingAnalysisMethod]

        Note:
            This property is readonly.
        """
        return None
