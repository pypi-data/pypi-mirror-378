"""AGMAGleasonConicalGear"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.system_model.part_model.gears import _2765

_AGMA_GLEASON_CONICAL_GEAR = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "AGMAGleasonConicalGear"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.part_model import _2675, _2698, _2703
    from mastapy._private.system_model.part_model.gears import (
        _2757,
        _2759,
        _2760,
        _2761,
        _2772,
        _2776,
        _2786,
        _2788,
        _2790,
        _2792,
        _2793,
        _2796,
    )

    Self = TypeVar("Self", bound="AGMAGleasonConicalGear")
    CastSelf = TypeVar(
        "CastSelf", bound="AGMAGleasonConicalGear._Cast_AGMAGleasonConicalGear"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AGMAGleasonConicalGear",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AGMAGleasonConicalGear:
    """Special nested class for casting AGMAGleasonConicalGear to subclasses."""

    __parent__: "AGMAGleasonConicalGear"

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
    def bevel_differential_gear(self: "CastSelf") -> "_2757.BevelDifferentialGear":
        from mastapy._private.system_model.part_model.gears import _2757

        return self.__parent__._cast(_2757.BevelDifferentialGear)

    @property
    def bevel_differential_planet_gear(
        self: "CastSelf",
    ) -> "_2759.BevelDifferentialPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2759

        return self.__parent__._cast(_2759.BevelDifferentialPlanetGear)

    @property
    def bevel_differential_sun_gear(
        self: "CastSelf",
    ) -> "_2760.BevelDifferentialSunGear":
        from mastapy._private.system_model.part_model.gears import _2760

        return self.__parent__._cast(_2760.BevelDifferentialSunGear)

    @property
    def bevel_gear(self: "CastSelf") -> "_2761.BevelGear":
        from mastapy._private.system_model.part_model.gears import _2761

        return self.__parent__._cast(_2761.BevelGear)

    @property
    def hypoid_gear(self: "CastSelf") -> "_2776.HypoidGear":
        from mastapy._private.system_model.part_model.gears import _2776

        return self.__parent__._cast(_2776.HypoidGear)

    @property
    def spiral_bevel_gear(self: "CastSelf") -> "_2786.SpiralBevelGear":
        from mastapy._private.system_model.part_model.gears import _2786

        return self.__parent__._cast(_2786.SpiralBevelGear)

    @property
    def straight_bevel_diff_gear(self: "CastSelf") -> "_2788.StraightBevelDiffGear":
        from mastapy._private.system_model.part_model.gears import _2788

        return self.__parent__._cast(_2788.StraightBevelDiffGear)

    @property
    def straight_bevel_gear(self: "CastSelf") -> "_2790.StraightBevelGear":
        from mastapy._private.system_model.part_model.gears import _2790

        return self.__parent__._cast(_2790.StraightBevelGear)

    @property
    def straight_bevel_planet_gear(self: "CastSelf") -> "_2792.StraightBevelPlanetGear":
        from mastapy._private.system_model.part_model.gears import _2792

        return self.__parent__._cast(_2792.StraightBevelPlanetGear)

    @property
    def straight_bevel_sun_gear(self: "CastSelf") -> "_2793.StraightBevelSunGear":
        from mastapy._private.system_model.part_model.gears import _2793

        return self.__parent__._cast(_2793.StraightBevelSunGear)

    @property
    def zerol_bevel_gear(self: "CastSelf") -> "_2796.ZerolBevelGear":
        from mastapy._private.system_model.part_model.gears import _2796

        return self.__parent__._cast(_2796.ZerolBevelGear)

    @property
    def agma_gleason_conical_gear(self: "CastSelf") -> "AGMAGleasonConicalGear":
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
class AGMAGleasonConicalGear(_2765.ConicalGear):
    """AGMAGleasonConicalGear

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _AGMA_GLEASON_CONICAL_GEAR

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_AGMAGleasonConicalGear":
        """Cast to another type.

        Returns:
            _Cast_AGMAGleasonConicalGear
        """
        return _Cast_AGMAGleasonConicalGear(self)
