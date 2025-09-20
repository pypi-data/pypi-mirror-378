"""MaterialsSettings"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import

_MATERIALS_SETTINGS = python_net_import("SMT.MastaAPI.Materials", "MaterialsSettings")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="MaterialsSettings")
    CastSelf = TypeVar("CastSelf", bound="MaterialsSettings._Cast_MaterialsSettings")


__docformat__ = "restructuredtext en"
__all__ = ("MaterialsSettings",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_MaterialsSettings:
    """Special nested class for casting MaterialsSettings to subclasses."""

    __parent__: "MaterialsSettings"

    @property
    def materials_settings(self: "CastSelf") -> "MaterialsSettings":
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
class MaterialsSettings(_0.APIBase):
    """MaterialsSettings

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _MATERIALS_SETTINGS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_MaterialsSettings":
        """Cast to another type.

        Returns:
            _Cast_MaterialsSettings
        """
        return _Cast_MaterialsSettings(self)
