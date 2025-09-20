"""SKFCalculationResult"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

_SKF_CALCULATION_RESULT = python_net_import(
    "SMT.MastaAPI.Bearings.BearingResults.Rolling.SkfModule", "SKFCalculationResult"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike
    from mastapy._private.bearings.bearing_results.rolling.skf_module import (
        _2290,
        _2292,
        _2293,
        _2294,
        _2295,
        _2297,
        _2300,
        _2301,
        _2302,
        _2303,
        _2304,
        _2305,
        _2313,
        _2314,
    )

    Self = TypeVar("Self", bound="SKFCalculationResult")
    CastSelf = TypeVar(
        "CastSelf", bound="SKFCalculationResult._Cast_SKFCalculationResult"
    )


__docformat__ = "restructuredtext en"
__all__ = ("SKFCalculationResult",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SKFCalculationResult:
    """Special nested class for casting SKFCalculationResult to subclasses."""

    __parent__: "SKFCalculationResult"

    @property
    def adjusted_speed(self: "CastSelf") -> "_2290.AdjustedSpeed":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2290

        return self.__parent__._cast(_2290.AdjustedSpeed)

    @property
    def bearing_loads(self: "CastSelf") -> "_2292.BearingLoads":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2292

        return self.__parent__._cast(_2292.BearingLoads)

    @property
    def bearing_rating_life(self: "CastSelf") -> "_2293.BearingRatingLife":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2293

        return self.__parent__._cast(_2293.BearingRatingLife)

    @property
    def dynamic_axial_load_carrying_capacity(
        self: "CastSelf",
    ) -> "_2294.DynamicAxialLoadCarryingCapacity":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2294

        return self.__parent__._cast(_2294.DynamicAxialLoadCarryingCapacity)

    @property
    def frequencies(self: "CastSelf") -> "_2295.Frequencies":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2295

        return self.__parent__._cast(_2295.Frequencies)

    @property
    def friction(self: "CastSelf") -> "_2297.Friction":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2297

        return self.__parent__._cast(_2297.Friction)

    @property
    def grease(self: "CastSelf") -> "_2300.Grease":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2300

        return self.__parent__._cast(_2300.Grease)

    @property
    def grease_life_and_relubrication_interval(
        self: "CastSelf",
    ) -> "_2301.GreaseLifeAndRelubricationInterval":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2301

        return self.__parent__._cast(_2301.GreaseLifeAndRelubricationInterval)

    @property
    def grease_quantity(self: "CastSelf") -> "_2302.GreaseQuantity":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2302

        return self.__parent__._cast(_2302.GreaseQuantity)

    @property
    def initial_fill(self: "CastSelf") -> "_2303.InitialFill":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2303

        return self.__parent__._cast(_2303.InitialFill)

    @property
    def life_model(self: "CastSelf") -> "_2304.LifeModel":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2304

        return self.__parent__._cast(_2304.LifeModel)

    @property
    def minimum_load(self: "CastSelf") -> "_2305.MinimumLoad":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2305

        return self.__parent__._cast(_2305.MinimumLoad)

    @property
    def static_safety_factors(self: "CastSelf") -> "_2313.StaticSafetyFactors":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2313

        return self.__parent__._cast(_2313.StaticSafetyFactors)

    @property
    def viscosities(self: "CastSelf") -> "_2314.Viscosities":
        from mastapy._private.bearings.bearing_results.rolling.skf_module import _2314

        return self.__parent__._cast(_2314.Viscosities)

    @property
    def skf_calculation_result(self: "CastSelf") -> "SKFCalculationResult":
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
class SKFCalculationResult(_0.APIBase):
    """SKFCalculationResult

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _SKF_CALCULATION_RESULT

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

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
    def cast_to(self: "Self") -> "_Cast_SKFCalculationResult":
        """Cast to another type.

        Returns:
            _Cast_SKFCalculationResult
        """
        return _Cast_SKFCalculationResult(self)
