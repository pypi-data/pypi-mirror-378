"""KlingelnbergCycloPalloidConicalGear"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.part_model.gears import _2765

_KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "KlingelnbergCycloPalloidConicalGear"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.part_model import _2675, _2698, _2703
    from mastapy._private.system_model.part_model.gears import _2772, _2780, _2782

    Self = TypeVar("Self", bound="KlingelnbergCycloPalloidConicalGear")
    CastSelf = TypeVar(
        "CastSelf",
        bound="KlingelnbergCycloPalloidConicalGear._Cast_KlingelnbergCycloPalloidConicalGear",
    )


__docformat__ = "restructuredtext en"
__all__ = ("KlingelnbergCycloPalloidConicalGear",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_KlingelnbergCycloPalloidConicalGear:
    """Special nested class for casting KlingelnbergCycloPalloidConicalGear to subclasses."""

    __parent__: "KlingelnbergCycloPalloidConicalGear"

    @property
    def conical_gear(self: "CastSelf") -> "_2765.ConicalGear":
        return self.__parent__._cast(_2765.ConicalGear)

    @property
    def gear(self: "CastSelf") -> "_2772.Gear":
        from mastapy._private.system_model.part_model.gears import _2772

        return self.__parent__._cast(_2772.Gear)

    @property
    def mountable_component(self: "CastSelf") -> "_2698.MountableComponent":
        from mastapy._private.system_model.part_model import _2698

        return self.__parent__._cast(_2698.MountableComponent)

    @property
    def component(self: "CastSelf") -> "_2675.Component":
        from mastapy._private.system_model.part_model import _2675

        return self.__parent__._cast(_2675.Component)

    @property
    def part(self: "CastSelf") -> "_2703.Part":
        from mastapy._private.system_model.part_model import _2703

        return self.__parent__._cast(_2703.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2419.DesignEntity":
        from mastapy._private.system_model import _2419

        return self.__parent__._cast(_2419.DesignEntity)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear(
        self: "CastSelf",
    ) -> "_2780.KlingelnbergCycloPalloidHypoidGear":
        from mastapy._private.system_model.part_model.gears import _2780

        return self.__parent__._cast(_2780.KlingelnbergCycloPalloidHypoidGear)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear(
        self: "CastSelf",
    ) -> "_2782.KlingelnbergCycloPalloidSpiralBevelGear":
        from mastapy._private.system_model.part_model.gears import _2782

        return self.__parent__._cast(_2782.KlingelnbergCycloPalloidSpiralBevelGear)

    @property
    def klingelnberg_cyclo_palloid_conical_gear(
        self: "CastSelf",
    ) -> "KlingelnbergCycloPalloidConicalGear":
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
class KlingelnbergCycloPalloidConicalGear(_2765.ConicalGear):
    """KlingelnbergCycloPalloidConicalGear

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _KLINGELNBERG_CYCLO_PALLOID_CONICAL_GEAR

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_KlingelnbergCycloPalloidConicalGear":
        """Cast to another type.

        Returns:
            _Cast_KlingelnbergCycloPalloidConicalGear
        """
        return _Cast_KlingelnbergCycloPalloidConicalGear(self)
