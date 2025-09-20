"""ConicalGearMicroGeometryConfig"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.manufacturing.bevel import _882

_CONICAL_GEAR_MICRO_GEOMETRY_CONFIG = python_net_import(
    "SMT.MastaAPI.Gears.Manufacturing.Bevel", "ConicalGearMicroGeometryConfig"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1335, _1338, _1341
    from mastapy._private.gears.manufacturing.bevel import _893

    Self = TypeVar("Self", bound="ConicalGearMicroGeometryConfig")
    CastSelf = TypeVar(
        "CastSelf",
        bound="ConicalGearMicroGeometryConfig._Cast_ConicalGearMicroGeometryConfig",
    )


__docformat__ = "restructuredtext en"
__all__ = ("ConicalGearMicroGeometryConfig",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConicalGearMicroGeometryConfig:
    """Special nested class for casting ConicalGearMicroGeometryConfig to subclasses."""

    __parent__: "ConicalGearMicroGeometryConfig"

    @property
    def conical_gear_micro_geometry_config_base(
        self: "CastSelf",
    ) -> "_882.ConicalGearMicroGeometryConfigBase":
        return self.__parent__._cast(_882.ConicalGearMicroGeometryConfigBase)

    @property
    def gear_implementation_detail(
        self: "CastSelf",
    ) -> "_1341.GearImplementationDetail":
        from mastapy._private.gears.analysis import _1341

        return self.__parent__._cast(_1341.GearImplementationDetail)

    @property
    def gear_design_analysis(self: "CastSelf") -> "_1338.GearDesignAnalysis":
        from mastapy._private.gears.analysis import _1338

        return self.__parent__._cast(_1338.GearDesignAnalysis)

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1335.AbstractGearAnalysis":
        from mastapy._private.gears.analysis import _1335

        return self.__parent__._cast(_1335.AbstractGearAnalysis)

    @property
    def conical_pinion_micro_geometry_config(
        self: "CastSelf",
    ) -> "_893.ConicalPinionMicroGeometryConfig":
        from mastapy._private.gears.manufacturing.bevel import _893

        return self.__parent__._cast(_893.ConicalPinionMicroGeometryConfig)

    @property
    def conical_gear_micro_geometry_config(
        self: "CastSelf",
    ) -> "ConicalGearMicroGeometryConfig":
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
class ConicalGearMicroGeometryConfig(_882.ConicalGearMicroGeometryConfigBase):
    """ConicalGearMicroGeometryConfig

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONICAL_GEAR_MICRO_GEOMETRY_CONFIG

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_ConicalGearMicroGeometryConfig":
        """Cast to another type.

        Returns:
            _Cast_ConicalGearMicroGeometryConfig
        """
        return _Cast_ConicalGearMicroGeometryConfig(self)
