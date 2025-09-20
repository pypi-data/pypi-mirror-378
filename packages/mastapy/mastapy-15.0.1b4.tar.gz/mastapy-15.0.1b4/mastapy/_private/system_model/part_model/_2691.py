"""InternalClearanceTolerance"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import (
    constructor,
    conversion,
    enum_with_selected_value_runtime,
    utility,
)
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.implicit import enum_with_selected_value, overridable
from mastapy._private._internal.overridable_constructor import _unpack_overridable
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.bearings.tolerances import _2110, _2112

_INTERNAL_CLEARANCE_TOLERANCE = python_net_import(
    "SMT.MastaAPI.SystemModel.PartModel", "InternalClearanceTolerance"
)

if TYPE_CHECKING:
    from typing import Any, List, Tuple, Type, TypeVar, Union

    from mastapy._private._internal.typing import PathLike
    from mastapy._private.system_model.part_model import _2668, _2709

    Self = TypeVar("Self", bound="InternalClearanceTolerance")
    CastSelf = TypeVar(
        "CastSelf", bound="InternalClearanceTolerance._Cast_InternalClearanceTolerance"
    )


__docformat__ = "restructuredtext en"
__all__ = ("InternalClearanceTolerance",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_InternalClearanceTolerance:
    """Special nested class for casting InternalClearanceTolerance to subclasses."""

    __parent__: "InternalClearanceTolerance"

    @property
    def axial_internal_clearance_tolerance(
        self: "CastSelf",
    ) -> "_2668.AxialInternalClearanceTolerance":
        from mastapy._private.system_model.part_model import _2668

        return self.__parent__._cast(_2668.AxialInternalClearanceTolerance)

    @property
    def radial_internal_clearance_tolerance(
        self: "CastSelf",
    ) -> "_2709.RadialInternalClearanceTolerance":
        from mastapy._private.system_model.part_model import _2709

        return self.__parent__._cast(_2709.RadialInternalClearanceTolerance)

    @property
    def internal_clearance_tolerance(self: "CastSelf") -> "InternalClearanceTolerance":
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
class InternalClearanceTolerance(_0.APIBase):
    """InternalClearanceTolerance

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _INTERNAL_CLEARANCE_TOLERANCE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def clearance_class(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_InternalClearanceClass":
        """EnumWithSelectedValue[mastapy.bearings.tolerances.InternalClearanceClass]"""
        temp = pythonnet_property_get(self.wrapped, "ClearanceClass")

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_InternalClearanceClass.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @clearance_class.setter
    @exception_bridge
    @enforce_parameter_types
    def clearance_class(self: "Self", value: "_2110.InternalClearanceClass") -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_InternalClearanceClass.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "ClearanceClass", value)

    @property
    @exception_bridge
    def definition_option(
        self: "Self",
    ) -> "enum_with_selected_value.EnumWithSelectedValue_BearingToleranceDefinitionOptions":
        """EnumWithSelectedValue[mastapy.bearings.tolerances.BearingToleranceDefinitionOptions]"""
        temp = pythonnet_property_get(self.wrapped, "DefinitionOption")

        if temp is None:
            return None

        value = enum_with_selected_value.EnumWithSelectedValue_BearingToleranceDefinitionOptions.wrapped_type()
        return enum_with_selected_value_runtime.create(temp, value)

    @definition_option.setter
    @exception_bridge
    @enforce_parameter_types
    def definition_option(
        self: "Self", value: "_2112.BearingToleranceDefinitionOptions"
    ) -> None:
        wrapper_type = enum_with_selected_value_runtime.ENUM_WITH_SELECTED_VALUE
        enclosed_type = enum_with_selected_value.EnumWithSelectedValue_BearingToleranceDefinitionOptions.implicit_type()
        value = conversion.mp_to_pn_enum(value, enclosed_type)
        value = wrapper_type[enclosed_type](value)
        pythonnet_property_set(self.wrapped, "DefinitionOption", value)

    @property
    @exception_bridge
    def maximum(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "Maximum")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @maximum.setter
    @exception_bridge
    @enforce_parameter_types
    def maximum(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "Maximum", value)

    @property
    @exception_bridge
    def maximum_from_nominal(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "MaximumFromNominal")

        if temp is None:
            return 0.0

        return temp

    @maximum_from_nominal.setter
    @exception_bridge
    @enforce_parameter_types
    def maximum_from_nominal(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "MaximumFromNominal",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def minimum(self: "Self") -> "overridable.Overridable_float":
        """Overridable[float]"""
        temp = pythonnet_property_get(self.wrapped, "Minimum")

        if temp is None:
            return 0.0

        return constructor.new_from_mastapy(
            "mastapy._private._internal.implicit.overridable", "Overridable_float"
        )(temp)

    @minimum.setter
    @exception_bridge
    @enforce_parameter_types
    def minimum(self: "Self", value: "Union[float, Tuple[float, bool]]") -> None:
        wrapper_type = overridable.Overridable_float.wrapper_type()
        enclosed_type = overridable.Overridable_float.implicit_type()
        value, is_overridden = _unpack_overridable(value)
        value = wrapper_type[enclosed_type](
            enclosed_type(value) if value is not None else 0.0, is_overridden
        )
        pythonnet_property_set(self.wrapped, "Minimum", value)

    @property
    @exception_bridge
    def minimum_from_nominal(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "MinimumFromNominal")

        if temp is None:
            return 0.0

        return temp

    @minimum_from_nominal.setter
    @exception_bridge
    @enforce_parameter_types
    def minimum_from_nominal(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped,
            "MinimumFromNominal",
            float(value) if value is not None else 0.0,
        )

    @property
    @exception_bridge
    def nominal(self: "Self") -> "float":
        """float"""
        temp = pythonnet_property_get(self.wrapped, "Nominal")

        if temp is None:
            return 0.0

        return temp

    @nominal.setter
    @exception_bridge
    @enforce_parameter_types
    def nominal(self: "Self", value: "float") -> None:
        pythonnet_property_set(
            self.wrapped, "Nominal", float(value) if value is not None else 0.0
        )

    @property
    @exception_bridge
    def specify_from_nominal(self: "Self") -> "bool":
        """bool"""
        temp = pythonnet_property_get(self.wrapped, "SpecifyFromNominal")

        if temp is None:
            return False

        return temp

    @specify_from_nominal.setter
    @exception_bridge
    @enforce_parameter_types
    def specify_from_nominal(self: "Self", value: "bool") -> None:
        pythonnet_property_set(
            self.wrapped,
            "SpecifyFromNominal",
            bool(value) if value is not None else False,
        )

    @property
    @exception_bridge
    def report_names(self: "Self") -> "List[str]":
        """List[str]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ReportNames")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, str)

        if value is None:
            return None

        return value

    @exception_bridge
    @enforce_parameter_types
    def output_default_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputDefaultReportTo", file_path)

    @exception_bridge
    def get_default_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetDefaultReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportTo", file_path)

    @exception_bridge
    @enforce_parameter_types
    def output_active_report_as_text_to(self: "Self", file_path: "PathLike") -> None:
        """Method does not return.

        Args:
            file_path (PathLike)
        """
        file_path = str(file_path)
        pythonnet_method_call(self.wrapped, "OutputActiveReportAsTextTo", file_path)

    @exception_bridge
    def get_active_report_with_encoded_images(self: "Self") -> "str":
        """str"""
        method_result = pythonnet_method_call(
            self.wrapped, "GetActiveReportWithEncodedImages"
        )
        return method_result

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_masta_report(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsMastaReport",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def output_named_report_as_text_to(
        self: "Self", report_name: "str", file_path: "PathLike"
    ) -> None:
        """Method does not return.

        Args:
            report_name (str)
            file_path (PathLike)
        """
        report_name = str(report_name)
        file_path = str(file_path)
        pythonnet_method_call(
            self.wrapped,
            "OutputNamedReportAsTextTo",
            report_name if report_name else "",
            file_path,
        )

    @exception_bridge
    @enforce_parameter_types
    def get_named_report_with_encoded_images(self: "Self", report_name: "str") -> "str":
        """str

        Args:
            report_name (str)
        """
        report_name = str(report_name)
        method_result = pythonnet_method_call(
            self.wrapped,
            "GetNamedReportWithEncodedImages",
            report_name if report_name else "",
        )
        return method_result

    @property
    def cast_to(self: "Self") -> "_Cast_InternalClearanceTolerance":
        """Cast to another type.

        Returns:
            _Cast_InternalClearanceTolerance
        """
        return _Cast_InternalClearanceTolerance(self)
