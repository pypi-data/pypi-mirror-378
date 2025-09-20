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
from mastapy._private.system_model.part_model.couplings import _2838

_ARRAY = python_net_import("System", "Array")
_ENUM_WITH_SELECTED_VALUE = python_net_import(
    "SMT.MastaAPI.Utility.Property", "EnumWithSelectedValue"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    Self = TypeVar("Self", bound="EnumWithSelectedValue_RigidConnectorStiffnessType")


__docformat__ = "restructuredtext en"
__all__ = ("EnumWithSelectedValue_RigidConnectorStiffnessType",)


class EnumWithSelectedValue_RigidConnectorStiffnessType(
    mixins.EnumWithSelectedValueMixin, Enum
):
    """EnumWithSelectedValue_RigidConnectorStiffnessType

    A specific implementation of 'EnumWithSelectedValue' for 'RigidConnectorStiffnessType' types.
    """

    __qualname__ = "RigidConnectorStiffnessType"

    @classmethod
    def wrapper_type(
        cls: "Type[EnumWithSelectedValue_RigidConnectorStiffnessType]",
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
        cls: "Type[EnumWithSelectedValue_RigidConnectorStiffnessType]",
    ) -> "_2838.RigidConnectorStiffnessType":
        """Wrapped Pythonnet type of this class.

        Note:
            This property is readonly

        Returns:
            _2838.RigidConnectorStiffnessType
        """
        return _2838.RigidConnectorStiffnessType

    @classmethod
    def implicit_type(
        cls: "Type[EnumWithSelectedValue_RigidConnectorStiffnessType]",
    ) -> "Any":
        """Implicit Pythonnet type of this class.

        Note:
            This property is readonly.

        Returns:
            Any
        """
        return _2838.RigidConnectorStiffnessType.type_()

    @property
    @exception_bridge
    def selected_value(self: "Self") -> "_2838.RigidConnectorStiffnessType":
        """mastapy.system_model.part_model.couplings.RigidConnectorStiffnessType

        Note:
            This property is readonly.
        """
        return None

    @property
    @exception_bridge
    def available_values(self: "Self") -> "List[_2838.RigidConnectorStiffnessType]":
        """List[mastapy.system_model.part_model.couplings.RigidConnectorStiffnessType]

        Note:
            This property is readonly.
        """
        return None
