"""GearManufacturingConfigurationViewModelPlaceholder"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.manufacturing.cylindrical import _732

_GEAR_MANUFACTURING_CONFIGURATION_VIEW_MODEL_PLACEHOLDER = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Cylindrical",
    "GearManufacturingConfigurationViewModelPlaceholder",
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    Self = TypeVar("Self", bound="GearManufacturingConfigurationViewModelPlaceholder")
    CastSelf = TypeVar(
        "CastSelf",
        bound="GearManufacturingConfigurationViewModelPlaceholder._Cast_GearManufacturingConfigurationViewModelPlaceholder",
    )


__docformat__ = "restructuredtext en"
__all__ = ("GearManufacturingConfigurationViewModelPlaceholder",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearManufacturingConfigurationViewModelPlaceholder:
    """Special nested class for casting GearManufacturingConfigurationViewModelPlaceholder to subclasses."""

    __parent__: "GearManufacturingConfigurationViewModelPlaceholder"

    @property
    def gear_manufacturing_configuration_view_model(
        self: "CastSelf",
    ) -> "_732.GearManufacturingConfigurationViewModel":
        return self.__parent__._cast(_732.GearManufacturingConfigurationViewModel)

    @property
    def gear_manufacturing_configuration_view_model_placeholder(
        self: "CastSelf",
    ) -> "GearManufacturingConfigurationViewModelPlaceholder":
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
class GearManufacturingConfigurationViewModelPlaceholder(
    _732.GearManufacturingConfigurationViewModel
):
    """GearManufacturingConfigurationViewModelPlaceholder

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_MANUFACTURING_CONFIGURATION_VIEW_MODEL_PLACEHOLDER

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(
        self: "Self",
    ) -> "_Cast_GearManufacturingConfigurationViewModelPlaceholder":
        """Cast to another type.

        Returns:
            _Cast_GearManufacturingConfigurationViewModelPlaceholder
        """
        return _Cast_GearManufacturingConfigurationViewModelPlaceholder(self)
