"""HypoidGearSet"""

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
from mastapy._private.system_model.part_model.gears import _2756

_HYPOID_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "HypoidGearSet"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.gear_designs.hypoid import _1091
    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets.gears import _2541
    from mastapy._private.system_model.part_model import _2664, _2703, _2713
    from mastapy._private.system_model.part_model.gears import _2766, _2774, _2776

    Self = TypeVar("Self", bound="HypoidGearSet")
    CastSelf = TypeVar("CastSelf", bound="HypoidGearSet._Cast_HypoidGearSet")


__docformat__ = "restructuredtext en"
__all__ = ("HypoidGearSet",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_HypoidGearSet:
    """Special nested class for casting HypoidGearSet to subclasses."""

    __parent__: "HypoidGearSet"

    @property
    def agma_gleason_conical_gear_set(
        self: "CastSelf",
    ) -> "_2756.AGMAGleasonConicalGearSet":
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
    def hypoid_gear_set(self: "CastSelf") -> "HypoidGearSet":
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
class HypoidGearSet(_2756.AGMAGleasonConicalGearSet):
    """HypoidGearSet

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _HYPOID_GEAR_SET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def conical_gear_set_design(self: "Self") -> "_1091.HypoidGearSetDesign":
        """mastapy.gears.gear_designs.hypoid.HypoidGearSetDesign

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
    def hypoid_gear_set_design(self: "Self") -> "_1091.HypoidGearSetDesign":
        """mastapy.gears.gear_designs.hypoid.HypoidGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HypoidGearSetDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def hypoid_gears(self: "Self") -> "List[_2776.HypoidGear]":
        """List[mastapy.system_model.part_model.gears.HypoidGear]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HypoidGears")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def hypoid_meshes(self: "Self") -> "List[_2541.HypoidGearMesh]":
        """List[mastapy.system_model.connections_and_sockets.gears.HypoidGearMesh]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HypoidMeshes")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_HypoidGearSet":
        """Cast to another type.

        Returns:
            _Cast_HypoidGearSet
        """
        return _Cast_HypoidGearSet(self)
