"""SimpleTaskProgress"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _7899
from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
)

_SIMPLE_TASK_PROGRESS = python_net_import("SMT.MastaAPIUtility", "SimpleTaskProgress")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="SimpleTaskProgress")
    CastSelf = TypeVar("CastSelf", bound="SimpleTaskProgress._Cast_SimpleTaskProgress")


__docformat__ = "restructuredtext en"
__all__ = ("SimpleTaskProgress",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SimpleTaskProgress:
    """Special nested class for casting SimpleTaskProgress to subclasses."""

    __parent__: "SimpleTaskProgress"

    @property
    def simple_task_progress(self: "CastSelf") -> "SimpleTaskProgress":
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
class SimpleTaskProgress(_7899.ConsoleProgress):
    """SimpleTaskProgress

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SIMPLE_TASK_PROGRESS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @exception_bridge
    def complete(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "Complete")

    @property
    def cast_to(self: "Self") -> "_Cast_SimpleTaskProgress":
        """Cast to another type.

        Returns:
            _Cast_SimpleTaskProgress
        """
        return _Cast_SimpleTaskProgress(self)
