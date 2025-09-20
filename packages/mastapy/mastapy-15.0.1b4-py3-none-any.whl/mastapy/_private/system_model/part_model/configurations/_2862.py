"""ActiveFESubstructureSelection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.fe import _2610
from mastapy._private.system_model.part_model import _2685
from mastapy._private.system_model.part_model.configurations import _2870

_ACTIVE_FE_SUBSTRUCTURE_SELECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Configurations", "ActiveFESubstructureSelection"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="ActiveFESubstructureSelection")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ActiveFESubstructureSelection._Cast_ActiveFESubstructureSelection",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ActiveFESubstructureSelection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ActiveFESubstructureSelection:
    """Special nested class for casting ActiveFESubstructureSelection to subclasses."""

    __parent__: "ActiveFESubstructureSelection"

    @property
    def part_detail_selection(self: "CastSelf") -> "_2870.PartDetailSelection":
        return self.__parent__._cast(_2870.PartDetailSelection)

    @property
    def active_fe_substructure_selection(
        self: "CastSelf",
    ) -> "ActiveFESubstructureSelection":
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
class ActiveFESubstructureSelection(
    _2870.PartDetailSelection[_2685.FEPart, _2610.FESubstructure]
):
    """ActiveFESubstructureSelection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ACTIVE_FE_SUBSTRUCTURE_SELECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ActiveFESubstructureSelection":
        """Cast to another type.

        Returns:
            _Cast_ActiveFESubstructureSelection
        """
        return _Cast_ActiveFESubstructureSelection(self)
