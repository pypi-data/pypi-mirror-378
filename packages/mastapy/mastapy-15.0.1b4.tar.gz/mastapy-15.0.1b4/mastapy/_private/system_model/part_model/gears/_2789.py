"""StraightBevelDiffGearSet"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.part_model.gears import _2762

_STRAIGHT_BEVEL_DIFF_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "StraightBevelDiffGearSet"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.gear_designs.straight_bevel_diff import _1071
    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets.gears import _2551
    from mastapy._private.system_model.part_model import _2664, _2703, _2713
    from mastapy._private.system_model.part_model.gears import (
        _2756,
        _2766,
        _2774,
        _2788,
    )

    Self = TypeVar("Self", bound="StraightBevelDiffGearSet")
    CastSelf = TypeVar(
        "CastSelf", bound="StraightBevelDiffGearSet._Cast_StraightBevelDiffGearSet"
    )


__docformat__ = "restructuredtext en"
__all__ = ("StraightBevelDiffGearSet",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_StraightBevelDiffGearSet:
    """Special nested class for casting StraightBevelDiffGearSet to subclasses."""

    __parent__: "StraightBevelDiffGearSet"

    @property
    def bevel_gear_set(self: "CastSelf") -> "_2762.BevelGearSet":
        return self.__parent__._cast(_2762.BevelGearSet)

    @property
    def agma_gleason_conical_gear_set(
        self: "CastSelf",
    ) -> "_2756.AGMAGleasonConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2756

        return self.__parent__._cast(_2756.AGMAGleasonConicalGearSet)

    @property
    def conical_gear_set(self: "CastSelf") -> "_2766.ConicalGearSet":
        from mastapy._private.system_model.part_model.gears import _2766

        return self.__parent__._cast(_2766.ConicalGearSet)

    @property
    def gear_set(self: "CastSelf") -> "_2774.GearSet":
        from mastapy._private.system_model.part_model.gears import _2774

        return self.__parent__._cast(_2774.GearSet)

    @property
    def specialised_assembly(self: "CastSelf") -> "_2713.SpecialisedAssembly":
        from mastapy._private.system_model.part_model import _2713

        return self.__parent__._cast(_2713.SpecialisedAssembly)

    @property
    def abstract_assembly(self: "CastSelf") -> "_2664.AbstractAssembly":
        from mastapy._private.system_model.part_model import _2664

        return self.__parent__._cast(_2664.AbstractAssembly)

    @property
    def part(self: "CastSelf") -> "_2703.Part":
        from mastapy._private.system_model.part_model import _2703

        return self.__parent__._cast(_2703.Part)

    @property
    def design_entity(self: "CastSelf") -> "_2419.DesignEntity":
        from mastapy._private.system_model import _2419

        return self.__parent__._cast(_2419.DesignEntity)

    @property
    def straight_bevel_diff_gear_set(self: "CastSelf") -> "StraightBevelDiffGearSet":
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
class StraightBevelDiffGearSet(_2762.BevelGearSet):
    """StraightBevelDiffGearSet

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _STRAIGHT_BEVEL_DIFF_GEAR_SET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def conical_gear_set_design(self: "Self") -> "_1071.StraightBevelDiffGearSetDesign":
        """mastapy.gears.gear_designs.straight_bevel_diff.StraightBevelDiffGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConicalGearSetDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def straight_bevel_diff_gear_set_design(
        self: "Self",
    ) -> "_1071.StraightBevelDiffGearSetDesign":
        """mastapy.gears.gear_designs.straight_bevel_diff.StraightBevelDiffGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelDiffGearSetDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def straight_bevel_diff_gears(self: "Self") -> "List[_2788.StraightBevelDiffGear]":
        """List[mastapy.system_model.part_model.gears.StraightBevelDiffGear]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelDiffGears")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def straight_bevel_diff_meshes(
        self: "Self",
    ) -> "List[_2551.StraightBevelDiffGearMesh]":
        """List[mastapy.system_model.connections_and_sockets.gears.StraightBevelDiffGearMesh]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StraightBevelDiffMeshes")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_StraightBevelDiffGearSet":
        """Cast to another type.

        Returns:
            _Cast_StraightBevelDiffGearSet
        """
        return _Cast_StraightBevelDiffGearSet(self)
