"""ConceptGearSet"""

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
from mastapy._private.system_model.part_model.gears import _2774

_CONCEPT_GEAR_SET = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Gears", "ConceptGearSet"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.gear_designs.concept import _1298
    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.connections_and_sockets.gears import _2531
    from mastapy._private.system_model.part_model import _2664, _2703, _2713
    from mastapy._private.system_model.part_model.gears import _2763

    Self = TypeVar("Self", bound="ConceptGearSet")
    CastSelf = TypeVar("CastSelf", bound="ConceptGearSet._Cast_ConceptGearSet")


__docformat__ = "restructuredtext en"
__all__ = ("ConceptGearSet",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_ConceptGearSet:
    """Special nested class for casting ConceptGearSet to subclasses."""

    __parent__: "ConceptGearSet"

    @property
    def gear_set(self: "CastSelf") -> "_2774.GearSet":
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
    def concept_gear_set(self: "CastSelf") -> "ConceptGearSet":
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
class ConceptGearSet(_2774.GearSet):
    """ConceptGearSet

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CONCEPT_GEAR_SET

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def active_gear_set_design(self: "Self") -> "_1298.ConceptGearSetDesign":
        """mastapy.gears.gear_designs.concept.ConceptGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ActiveGearSetDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def concept_gear_set_design(self: "Self") -> "_1298.ConceptGearSetDesign":
        """mastapy.gears.gear_designs.concept.ConceptGearSetDesign

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConceptGearSetDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def concept_gears(self: "Self") -> "List[_2763.ConceptGear]":
        """List[mastapy.system_model.part_model.gears.ConceptGear]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConceptGears")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def concept_meshes(self: "Self") -> "List[_2531.ConceptGearMesh]":
        """List[mastapy.system_model.connections_and_sockets.gears.ConceptGearMesh]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ConceptMeshes")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_ConceptGearSet":
        """Cast to another type.

        Returns:
            _Cast_ConceptGearSet
        """
        return _Cast_ConceptGearSet(self)
