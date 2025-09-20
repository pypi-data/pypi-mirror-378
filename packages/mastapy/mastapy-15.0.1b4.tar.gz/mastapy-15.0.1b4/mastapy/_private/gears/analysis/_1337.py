"""AbstractGearSetAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private import _0
from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

_ABSTRACT_GEAR_SET_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "AbstractGearSetAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike
    from mastapy._private.gears.analysis import _1346, _1348, _1349, _1350, _1351
    from mastapy._private.gears.fe_model import _1320
    from mastapy._private.gears.fe_model.conical import _1326
    from mastapy._private.gears.fe_model.cylindrical import _1323
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import (
        _1220,
        _1221,
    )
    from mastapy._private.gears.gear_designs.face import _1100
    from mastapy._private.gears.gear_two_d_fe_analysis import _999, _1000
    from mastapy._private.gears.load_case import _977
    from mastapy._private.gears.load_case.bevel import _996
    from mastapy._private.gears.load_case.concept import _992
    from mastapy._private.gears.load_case.conical import _989
    from mastapy._private.gears.load_case.cylindrical import _986
    from mastapy._private.gears.load_case.face import _983
    from mastapy._private.gears.load_case.worm import _980
    from mastapy._private.gears.ltca import _950
    from mastapy._private.gears.ltca.conical import _971
    from mastapy._private.gears.ltca.cylindrical import _963, _965
    from mastapy._private.gears.manufacturing.bevel import _894, _895, _896, _897
    from mastapy._private.gears.manufacturing.cylindrical import _724, _725, _729
    from mastapy._private.gears.rating import _446, _454, _455
    from mastapy._private.gears.rating.agma_gleason_conical import _659
    from mastapy._private.gears.rating.bevel import _648
    from mastapy._private.gears.rating.concept import _644, _645
    from mastapy._private.gears.rating.conical import _633, _634
    from mastapy._private.gears.rating.cylindrical import _555, _556, _572
    from mastapy._private.gears.rating.face import _541, _542
    from mastapy._private.gears.rating.hypoid import _532
    from mastapy._private.gears.rating.klingelnberg_conical import _505
    from mastapy._private.gears.rating.klingelnberg_hypoid import _502
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _499
    from mastapy._private.gears.rating.spiral_bevel import _496
    from mastapy._private.gears.rating.straight_bevel import _489
    from mastapy._private.gears.rating.straight_bevel_diff import _492
    from mastapy._private.gears.rating.worm import _467, _468
    from mastapy._private.gears.rating.zerol_bevel import _463
    from mastapy._private.utility.model_validation import _1993, _1994

    Self = TypeVar("Self", bound="AbstractGearSetAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="AbstractGearSetAnalysis._Cast_AbstractGearSetAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractGearSetAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractGearSetAnalysis:
    """Special nested class for casting AbstractGearSetAnalysis to subclasses."""

    __parent__: "AbstractGearSetAnalysis"

    @property
    def abstract_gear_set_rating(self: "CastSelf") -> "_446.AbstractGearSetRating":
        from mastapy._private.gears.rating import _446

        return self.__parent__._cast(_446.AbstractGearSetRating)

    @property
    def gear_set_duty_cycle_rating(self: "CastSelf") -> "_454.GearSetDutyCycleRating":
        from mastapy._private.gears.rating import _454

        return self.__parent__._cast(_454.GearSetDutyCycleRating)

    @property
    def gear_set_rating(self: "CastSelf") -> "_455.GearSetRating":
        from mastapy._private.gears.rating import _455

        return self.__parent__._cast(_455.GearSetRating)

    @property
    def zerol_bevel_gear_set_rating(self: "CastSelf") -> "_463.ZerolBevelGearSetRating":
        from mastapy._private.gears.rating.zerol_bevel import _463

        return self.__parent__._cast(_463.ZerolBevelGearSetRating)

    @property
    def worm_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_467.WormGearSetDutyCycleRating":
        from mastapy._private.gears.rating.worm import _467

        return self.__parent__._cast(_467.WormGearSetDutyCycleRating)

    @property
    def worm_gear_set_rating(self: "CastSelf") -> "_468.WormGearSetRating":
        from mastapy._private.gears.rating.worm import _468

        return self.__parent__._cast(_468.WormGearSetRating)

    @property
    def straight_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_489.StraightBevelGearSetRating":
        from mastapy._private.gears.rating.straight_bevel import _489

        return self.__parent__._cast(_489.StraightBevelGearSetRating)

    @property
    def straight_bevel_diff_gear_set_rating(
        self: "CastSelf",
    ) -> "_492.StraightBevelDiffGearSetRating":
        from mastapy._private.gears.rating.straight_bevel_diff import _492

        return self.__parent__._cast(_492.StraightBevelDiffGearSetRating)

    @property
    def spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_496.SpiralBevelGearSetRating":
        from mastapy._private.gears.rating.spiral_bevel import _496

        return self.__parent__._cast(_496.SpiralBevelGearSetRating)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_set_rating(
        self: "CastSelf",
    ) -> "_499.KlingelnbergCycloPalloidSpiralBevelGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _499

        return self.__parent__._cast(
            _499.KlingelnbergCycloPalloidSpiralBevelGearSetRating
        )

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_set_rating(
        self: "CastSelf",
    ) -> "_502.KlingelnbergCycloPalloidHypoidGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _502

        return self.__parent__._cast(_502.KlingelnbergCycloPalloidHypoidGearSetRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_505.KlingelnbergCycloPalloidConicalGearSetRating":
        from mastapy._private.gears.rating.klingelnberg_conical import _505

        return self.__parent__._cast(_505.KlingelnbergCycloPalloidConicalGearSetRating)

    @property
    def hypoid_gear_set_rating(self: "CastSelf") -> "_532.HypoidGearSetRating":
        from mastapy._private.gears.rating.hypoid import _532

        return self.__parent__._cast(_532.HypoidGearSetRating)

    @property
    def face_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_541.FaceGearSetDutyCycleRating":
        from mastapy._private.gears.rating.face import _541

        return self.__parent__._cast(_541.FaceGearSetDutyCycleRating)

    @property
    def face_gear_set_rating(self: "CastSelf") -> "_542.FaceGearSetRating":
        from mastapy._private.gears.rating.face import _542

        return self.__parent__._cast(_542.FaceGearSetRating)

    @property
    def cylindrical_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_555.CylindricalGearSetDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _555

        return self.__parent__._cast(_555.CylindricalGearSetDutyCycleRating)

    @property
    def cylindrical_gear_set_rating(
        self: "CastSelf",
    ) -> "_556.CylindricalGearSetRating":
        from mastapy._private.gears.rating.cylindrical import _556

        return self.__parent__._cast(_556.CylindricalGearSetRating)

    @property
    def reduced_cylindrical_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_572.ReducedCylindricalGearSetDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _572

        return self.__parent__._cast(_572.ReducedCylindricalGearSetDutyCycleRating)

    @property
    def conical_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_633.ConicalGearSetDutyCycleRating":
        from mastapy._private.gears.rating.conical import _633

        return self.__parent__._cast(_633.ConicalGearSetDutyCycleRating)

    @property
    def conical_gear_set_rating(self: "CastSelf") -> "_634.ConicalGearSetRating":
        from mastapy._private.gears.rating.conical import _634

        return self.__parent__._cast(_634.ConicalGearSetRating)

    @property
    def concept_gear_set_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_644.ConceptGearSetDutyCycleRating":
        from mastapy._private.gears.rating.concept import _644

        return self.__parent__._cast(_644.ConceptGearSetDutyCycleRating)

    @property
    def concept_gear_set_rating(self: "CastSelf") -> "_645.ConceptGearSetRating":
        from mastapy._private.gears.rating.concept import _645

        return self.__parent__._cast(_645.ConceptGearSetRating)

    @property
    def bevel_gear_set_rating(self: "CastSelf") -> "_648.BevelGearSetRating":
        from mastapy._private.gears.rating.bevel import _648

        return self.__parent__._cast(_648.BevelGearSetRating)

    @property
    def agma_gleason_conical_gear_set_rating(
        self: "CastSelf",
    ) -> "_659.AGMAGleasonConicalGearSetRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _659

        return self.__parent__._cast(_659.AGMAGleasonConicalGearSetRating)

    @property
    def cylindrical_manufactured_gear_set_duty_cycle(
        self: "CastSelf",
    ) -> "_724.CylindricalManufacturedGearSetDutyCycle":
        from mastapy._private.gears.manufacturing.cylindrical import _724

        return self.__parent__._cast(_724.CylindricalManufacturedGearSetDutyCycle)

    @property
    def cylindrical_manufactured_gear_set_load_case(
        self: "CastSelf",
    ) -> "_725.CylindricalManufacturedGearSetLoadCase":
        from mastapy._private.gears.manufacturing.cylindrical import _725

        return self.__parent__._cast(_725.CylindricalManufacturedGearSetLoadCase)

    @property
    def cylindrical_set_manufacturing_config(
        self: "CastSelf",
    ) -> "_729.CylindricalSetManufacturingConfig":
        from mastapy._private.gears.manufacturing.cylindrical import _729

        return self.__parent__._cast(_729.CylindricalSetManufacturingConfig)

    @property
    def conical_set_manufacturing_analysis(
        self: "CastSelf",
    ) -> "_894.ConicalSetManufacturingAnalysis":
        from mastapy._private.gears.manufacturing.bevel import _894

        return self.__parent__._cast(_894.ConicalSetManufacturingAnalysis)

    @property
    def conical_set_manufacturing_config(
        self: "CastSelf",
    ) -> "_895.ConicalSetManufacturingConfig":
        from mastapy._private.gears.manufacturing.bevel import _895

        return self.__parent__._cast(_895.ConicalSetManufacturingConfig)

    @property
    def conical_set_micro_geometry_config(
        self: "CastSelf",
    ) -> "_896.ConicalSetMicroGeometryConfig":
        from mastapy._private.gears.manufacturing.bevel import _896

        return self.__parent__._cast(_896.ConicalSetMicroGeometryConfig)

    @property
    def conical_set_micro_geometry_config_base(
        self: "CastSelf",
    ) -> "_897.ConicalSetMicroGeometryConfigBase":
        from mastapy._private.gears.manufacturing.bevel import _897

        return self.__parent__._cast(_897.ConicalSetMicroGeometryConfigBase)

    @property
    def gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_950.GearSetLoadDistributionAnalysis":
        from mastapy._private.gears.ltca import _950

        return self.__parent__._cast(_950.GearSetLoadDistributionAnalysis)

    @property
    def cylindrical_gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_963.CylindricalGearSetLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.cylindrical import _963

        return self.__parent__._cast(_963.CylindricalGearSetLoadDistributionAnalysis)

    @property
    def face_gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_965.FaceGearSetLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.cylindrical import _965

        return self.__parent__._cast(_965.FaceGearSetLoadDistributionAnalysis)

    @property
    def conical_gear_set_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_971.ConicalGearSetLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.conical import _971

        return self.__parent__._cast(_971.ConicalGearSetLoadDistributionAnalysis)

    @property
    def gear_set_load_case_base(self: "CastSelf") -> "_977.GearSetLoadCaseBase":
        from mastapy._private.gears.load_case import _977

        return self.__parent__._cast(_977.GearSetLoadCaseBase)

    @property
    def worm_gear_set_load_case(self: "CastSelf") -> "_980.WormGearSetLoadCase":
        from mastapy._private.gears.load_case.worm import _980

        return self.__parent__._cast(_980.WormGearSetLoadCase)

    @property
    def face_gear_set_load_case(self: "CastSelf") -> "_983.FaceGearSetLoadCase":
        from mastapy._private.gears.load_case.face import _983

        return self.__parent__._cast(_983.FaceGearSetLoadCase)

    @property
    def cylindrical_gear_set_load_case(
        self: "CastSelf",
    ) -> "_986.CylindricalGearSetLoadCase":
        from mastapy._private.gears.load_case.cylindrical import _986

        return self.__parent__._cast(_986.CylindricalGearSetLoadCase)

    @property
    def conical_gear_set_load_case(self: "CastSelf") -> "_989.ConicalGearSetLoadCase":
        from mastapy._private.gears.load_case.conical import _989

        return self.__parent__._cast(_989.ConicalGearSetLoadCase)

    @property
    def concept_gear_set_load_case(self: "CastSelf") -> "_992.ConceptGearSetLoadCase":
        from mastapy._private.gears.load_case.concept import _992

        return self.__parent__._cast(_992.ConceptGearSetLoadCase)

    @property
    def bevel_set_load_case(self: "CastSelf") -> "_996.BevelSetLoadCase":
        from mastapy._private.gears.load_case.bevel import _996

        return self.__parent__._cast(_996.BevelSetLoadCase)

    @property
    def cylindrical_gear_set_tiff_analysis(
        self: "CastSelf",
    ) -> "_999.CylindricalGearSetTIFFAnalysis":
        from mastapy._private.gears.gear_two_d_fe_analysis import _999

        return self.__parent__._cast(_999.CylindricalGearSetTIFFAnalysis)

    @property
    def cylindrical_gear_set_tiff_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1000.CylindricalGearSetTIFFAnalysisDutyCycle":
        from mastapy._private.gears.gear_two_d_fe_analysis import _1000

        return self.__parent__._cast(_1000.CylindricalGearSetTIFFAnalysisDutyCycle)

    @property
    def face_gear_set_micro_geometry(
        self: "CastSelf",
    ) -> "_1100.FaceGearSetMicroGeometry":
        from mastapy._private.gears.gear_designs.face import _1100

        return self.__parent__._cast(_1100.FaceGearSetMicroGeometry)

    @property
    def cylindrical_gear_set_micro_geometry(
        self: "CastSelf",
    ) -> "_1220.CylindricalGearSetMicroGeometry":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1220

        return self.__parent__._cast(_1220.CylindricalGearSetMicroGeometry)

    @property
    def cylindrical_gear_set_micro_geometry_duty_cycle(
        self: "CastSelf",
    ) -> "_1221.CylindricalGearSetMicroGeometryDutyCycle":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1221

        return self.__parent__._cast(_1221.CylindricalGearSetMicroGeometryDutyCycle)

    @property
    def gear_set_fe_model(self: "CastSelf") -> "_1320.GearSetFEModel":
        from mastapy._private.gears.fe_model import _1320

        return self.__parent__._cast(_1320.GearSetFEModel)

    @property
    def cylindrical_gear_set_fe_model(
        self: "CastSelf",
    ) -> "_1323.CylindricalGearSetFEModel":
        from mastapy._private.gears.fe_model.cylindrical import _1323

        return self.__parent__._cast(_1323.CylindricalGearSetFEModel)

    @property
    def conical_set_fe_model(self: "CastSelf") -> "_1326.ConicalSetFEModel":
        from mastapy._private.gears.fe_model.conical import _1326

        return self.__parent__._cast(_1326.ConicalSetFEModel)

    @property
    def gear_set_design_analysis(self: "CastSelf") -> "_1346.GearSetDesignAnalysis":
        from mastapy._private.gears.analysis import _1346

        return self.__parent__._cast(_1346.GearSetDesignAnalysis)

    @property
    def gear_set_implementation_analysis(
        self: "CastSelf",
    ) -> "_1348.GearSetImplementationAnalysis":
        from mastapy._private.gears.analysis import _1348

        return self.__parent__._cast(_1348.GearSetImplementationAnalysis)

    @property
    def gear_set_implementation_analysis_abstract(
        self: "CastSelf",
    ) -> "_1349.GearSetImplementationAnalysisAbstract":
        from mastapy._private.gears.analysis import _1349

        return self.__parent__._cast(_1349.GearSetImplementationAnalysisAbstract)

    @property
    def gear_set_implementation_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1350.GearSetImplementationAnalysisDutyCycle":
        from mastapy._private.gears.analysis import _1350

        return self.__parent__._cast(_1350.GearSetImplementationAnalysisDutyCycle)

    @property
    def gear_set_implementation_detail(
        self: "CastSelf",
    ) -> "_1351.GearSetImplementationDetail":
        from mastapy._private.gears.analysis import _1351

        return self.__parent__._cast(_1351.GearSetImplementationDetail)

    @property
    def abstract_gear_set_analysis(self: "CastSelf") -> "AbstractGearSetAnalysis":
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
class AbstractGearSetAnalysis(_0.APIBase):
    """AbstractGearSetAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_GEAR_SET_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @name.setter
    @exception_bridge
    @enforce_parameter_types
    def name(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Name", str(value) if value is not None else ""
        )

    @property
    @exception_bridge
    def all_status_errors(self: "Self") -> "List[_1994.StatusItem]":
        """List[mastapy.utility.model_validation.StatusItem]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AllStatusErrors")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def status(self: "Self") -> "_1993.Status":
        """mastapy.utility.model_validation.Status

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Status")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

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
    def cast_to(self: "Self") -> "_Cast_AbstractGearSetAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AbstractGearSetAnalysis
        """
        return _Cast_AbstractGearSetAnalysis(self)
