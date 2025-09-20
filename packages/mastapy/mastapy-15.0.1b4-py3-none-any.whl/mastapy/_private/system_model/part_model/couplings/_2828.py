"""Coupling"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.system_model.part_model import _2713

_COUPLING = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel.Couplings", "Coupling"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model import _2419
    from mastapy._private.system_model.part_model import _2664, _2703
    from mastapy._private.system_model.part_model.couplings import (
        _2822,
        _2825,
        _2829,
        _2833,
        _2851,
        _2858,
    )

    Self = TypeVar("Self", bound="Coupling")
    CastSelf = TypeVar("CastSelf", bound="Coupling._Cast_Coupling")


__docformat__ = "restructuredtext en"
__all__ = ("Coupling",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_Coupling:
    """Special nested class for casting Coupling to subclasses."""

    __parent__: "Coupling"

    @property
    def specialised_assembly(self: "CastSelf") -> "_2713.SpecialisedAssembly":
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
    def clutch(self: "CastSelf") -> "_2822.Clutch":
        from mastapy._private.system_model.part_model.couplings import _2822

        return self.__parent__._cast(_2822.Clutch)

    @property
    def concept_coupling(self: "CastSelf") -> "_2825.ConceptCoupling":
        from mastapy._private.system_model.part_model.couplings import _2825

        return self.__parent__._cast(_2825.ConceptCoupling)

    @property
    def part_to_part_shear_coupling(
        self: "CastSelf",
    ) -> "_2833.PartToPartShearCoupling":
        from mastapy._private.system_model.part_model.couplings import _2833

        return self.__parent__._cast(_2833.PartToPartShearCoupling)

    @property
    def spring_damper(self: "CastSelf") -> "_2851.SpringDamper":
        from mastapy._private.system_model.part_model.couplings import _2851

        return self.__parent__._cast(_2851.SpringDamper)

    @property
    def torque_converter(self: "CastSelf") -> "_2858.TorqueConverter":
        from mastapy._private.system_model.part_model.couplings import _2858

        return self.__parent__._cast(_2858.TorqueConverter)

    @property
    def coupling(self: "CastSelf") -> "Coupling":
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
class Coupling(_2713.SpecialisedAssembly):
    """Coupling

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _COUPLING

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def axial_stiffness(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "AxialStiffness")

        if temp is None:
            return 0.0

        return temp

    @axial_stiffness.setter
    @exception_bridge
    @enforce_parameter_types
    def axial_stiffness(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "AxialStiffness", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def radial_stiffness(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "RadialStiffness")

        if temp is None:
            return 0.0

        return temp

    @radial_stiffness.setter
    @exception_bridge
    @enforce_parameter_types
    def radial_stiffness(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "RadialStiffness", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def tilt_stiffness(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "TiltStiffness")

        if temp is None:
            return 0.0

        return temp

    @tilt_stiffness.setter
    @exception_bridge
    @enforce_parameter_types
    def tilt_stiffness(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "TiltStiffness", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def torsional_stiffness(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "TorsionalStiffness")

        if temp is None:
            return 0.0

        return temp

    @torsional_stiffness.setter
    @exception_bridge
    @enforce_parameter_types
    def torsional_stiffness(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "TorsionalStiffness",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def halves(self: "Self") -> "List[_2829.CouplingHalf]":
        """List[mastapy.system_model.part_model.couplings.CouplingHalf]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Halves")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def half_a(self: "Self") -> "_2829.CouplingHalf":
        """mastapy.system_model.part_model.couplings.CouplingHalf

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HalfA")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def half_b(self: "Self") -> "_2829.CouplingHalf":
        """mastapy.system_model.part_model.couplings.CouplingHalf

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HalfB")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    def cast_to(self: "Self") -> "_Cast_Coupling":
        """Cast to another type.

        Returns:
            _Cast_Coupling
        """
        return _Cast_Coupling(self)
