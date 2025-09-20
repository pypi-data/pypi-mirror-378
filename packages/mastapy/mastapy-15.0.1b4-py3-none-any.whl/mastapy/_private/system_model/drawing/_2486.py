"""SystemDeflectionViewable"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.drawing import _2469

_SYSTEM_DEFLECTION_VIEWABLE = python_net_import(
    "SMT.MastaAPI.SystemModel.Drawing", "SystemDeflectionViewable"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model.drawing import _2479

    Self = TypeVar("Self", bound="SystemDeflectionViewable")
    CastSelf = TypeVar(
        "CastSelf", bound="SystemDeflectionViewable._Cast_SystemDeflectionViewable"
    )


__docformat__ = "restructuredtext en"
__all__ = ("SystemDeflectionViewable",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SystemDeflectionViewable:
    """Special nested class for casting SystemDeflectionViewable to subclasses."""

    __parent__: "SystemDeflectionViewable"

    @property
    def abstract_system_deflection_viewable(
        self: "CastSelf",
    ) -> "_2469.AbstractSystemDeflectionViewable":
        return self.__parent__._cast(_2469.AbstractSystemDeflectionViewable)

    @property
    def part_analysis_case_with_contour_viewable(
        self: "CastSelf",
    ) -> "_2479.PartAnalysisCaseWithContourViewable":
        from mastapy._private.system_model.drawing import _2479

        return self.__parent__._cast(_2479.PartAnalysisCaseWithContourViewable)

    @property
    def system_deflection_viewable(self: "CastSelf") -> "SystemDeflectionViewable":
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
class SystemDeflectionViewable(_2469.AbstractSystemDeflectionViewable):
    """SystemDeflectionViewable

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SYSTEM_DEFLECTION_VIEWABLE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_SystemDeflectionViewable":
        """Cast to another type.

        Returns:
            _Cast_SystemDeflectionViewable
        """
        return _Cast_SystemDeflectionViewable(self)
