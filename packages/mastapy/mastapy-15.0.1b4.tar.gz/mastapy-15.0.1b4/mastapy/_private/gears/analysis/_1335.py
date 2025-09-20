"""AbstractGearAnalysis"""

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
    pythonnet_property_set,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types

_ABSTRACT_GEAR_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "AbstractGearAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike
    from mastapy._private.gears.analysis import _1338, _1339, _1340, _1341
    from mastapy._private.gears.fe_model import _1317
    from mastapy._private.gears.fe_model.conical import _1324
    from mastapy._private.gears.fe_model.cylindrical import _1321
    from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import (
        _1213,
        _1214,
        _1215,
        _1217,
    )
    from mastapy._private.gears.gear_designs.face import _1097
    from mastapy._private.gears.gear_two_d_fe_analysis import _1001, _1002
    from mastapy._private.gears.load_case import _976
    from mastapy._private.gears.load_case.bevel import _994
    from mastapy._private.gears.load_case.concept import _991
    from mastapy._private.gears.load_case.conical import _988
    from mastapy._private.gears.load_case.cylindrical import _985
    from mastapy._private.gears.load_case.face import _982
    from mastapy._private.gears.load_case.worm import _979
    from mastapy._private.gears.ltca import _944
    from mastapy._private.gears.ltca.conical import _970
    from mastapy._private.gears.ltca.cylindrical import _959
    from mastapy._private.gears.manufacturing.bevel import (
        _879,
        _880,
        _881,
        _882,
        _892,
        _893,
        _898,
    )
    from mastapy._private.gears.manufacturing.cylindrical import _716, _720, _721
    from mastapy._private.gears.rating import _445, _449, _453
    from mastapy._private.gears.rating.agma_gleason_conical import _658
    from mastapy._private.gears.rating.bevel import _647
    from mastapy._private.gears.rating.concept import _640, _643
    from mastapy._private.gears.rating.conical import _630, _632
    from mastapy._private.gears.rating.cylindrical import _547, _552
    from mastapy._private.gears.rating.face import _537, _540
    from mastapy._private.gears.rating.hypoid import _531
    from mastapy._private.gears.rating.klingelnberg_conical import _504
    from mastapy._private.gears.rating.klingelnberg_hypoid import _501
    from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _498
    from mastapy._private.gears.rating.spiral_bevel import _495
    from mastapy._private.gears.rating.straight_bevel import _488
    from mastapy._private.gears.rating.straight_bevel_diff import _491
    from mastapy._private.gears.rating.worm import _464, _466
    from mastapy._private.gears.rating.zerol_bevel import _462

    Self = TypeVar("Self", bound="AbstractGearAnalysis")
    CastSelf = TypeVar(
        "CastSelf", bound="AbstractGearAnalysis._Cast_AbstractGearAnalysis"
    )


__docformat__ = "restructuredtext en"
__all__ = ("AbstractGearAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_AbstractGearAnalysis:
    """Special nested class for casting AbstractGearAnalysis to subclasses."""

    __parent__: "AbstractGearAnalysis"

    @property
    def abstract_gear_rating(self: "CastSelf") -> "_445.AbstractGearRating":
        from mastapy._private.gears.rating import _445

        return self.__parent__._cast(_445.AbstractGearRating)

    @property
    def gear_duty_cycle_rating(self: "CastSelf") -> "_449.GearDutyCycleRating":
        from mastapy._private.gears.rating import _449

        return self.__parent__._cast(_449.GearDutyCycleRating)

    @property
    def gear_rating(self: "CastSelf") -> "_453.GearRating":
        from mastapy._private.gears.rating import _453

        return self.__parent__._cast(_453.GearRating)

    @property
    def zerol_bevel_gear_rating(self: "CastSelf") -> "_462.ZerolBevelGearRating":
        from mastapy._private.gears.rating.zerol_bevel import _462

        return self.__parent__._cast(_462.ZerolBevelGearRating)

    @property
    def worm_gear_duty_cycle_rating(self: "CastSelf") -> "_464.WormGearDutyCycleRating":
        from mastapy._private.gears.rating.worm import _464

        return self.__parent__._cast(_464.WormGearDutyCycleRating)

    @property
    def worm_gear_rating(self: "CastSelf") -> "_466.WormGearRating":
        from mastapy._private.gears.rating.worm import _466

        return self.__parent__._cast(_466.WormGearRating)

    @property
    def straight_bevel_gear_rating(self: "CastSelf") -> "_488.StraightBevelGearRating":
        from mastapy._private.gears.rating.straight_bevel import _488

        return self.__parent__._cast(_488.StraightBevelGearRating)

    @property
    def straight_bevel_diff_gear_rating(
        self: "CastSelf",
    ) -> "_491.StraightBevelDiffGearRating":
        from mastapy._private.gears.rating.straight_bevel_diff import _491

        return self.__parent__._cast(_491.StraightBevelDiffGearRating)

    @property
    def spiral_bevel_gear_rating(self: "CastSelf") -> "_495.SpiralBevelGearRating":
        from mastapy._private.gears.rating.spiral_bevel import _495

        return self.__parent__._cast(_495.SpiralBevelGearRating)

    @property
    def klingelnberg_cyclo_palloid_spiral_bevel_gear_rating(
        self: "CastSelf",
    ) -> "_498.KlingelnbergCycloPalloidSpiralBevelGearRating":
        from mastapy._private.gears.rating.klingelnberg_spiral_bevel import _498

        return self.__parent__._cast(_498.KlingelnbergCycloPalloidSpiralBevelGearRating)

    @property
    def klingelnberg_cyclo_palloid_hypoid_gear_rating(
        self: "CastSelf",
    ) -> "_501.KlingelnbergCycloPalloidHypoidGearRating":
        from mastapy._private.gears.rating.klingelnberg_hypoid import _501

        return self.__parent__._cast(_501.KlingelnbergCycloPalloidHypoidGearRating)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_rating(
        self: "CastSelf",
    ) -> "_504.KlingelnbergCycloPalloidConicalGearRating":
        from mastapy._private.gears.rating.klingelnberg_conical import _504

        return self.__parent__._cast(_504.KlingelnbergCycloPalloidConicalGearRating)

    @property
    def hypoid_gear_rating(self: "CastSelf") -> "_531.HypoidGearRating":
        from mastapy._private.gears.rating.hypoid import _531

        return self.__parent__._cast(_531.HypoidGearRating)

    @property
    def face_gear_duty_cycle_rating(self: "CastSelf") -> "_537.FaceGearDutyCycleRating":
        from mastapy._private.gears.rating.face import _537

        return self.__parent__._cast(_537.FaceGearDutyCycleRating)

    @property
    def face_gear_rating(self: "CastSelf") -> "_540.FaceGearRating":
        from mastapy._private.gears.rating.face import _540

        return self.__parent__._cast(_540.FaceGearRating)

    @property
    def cylindrical_gear_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_547.CylindricalGearDutyCycleRating":
        from mastapy._private.gears.rating.cylindrical import _547

        return self.__parent__._cast(_547.CylindricalGearDutyCycleRating)

    @property
    def cylindrical_gear_rating(self: "CastSelf") -> "_552.CylindricalGearRating":
        from mastapy._private.gears.rating.cylindrical import _552

        return self.__parent__._cast(_552.CylindricalGearRating)

    @property
    def conical_gear_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_630.ConicalGearDutyCycleRating":
        from mastapy._private.gears.rating.conical import _630

        return self.__parent__._cast(_630.ConicalGearDutyCycleRating)

    @property
    def conical_gear_rating(self: "CastSelf") -> "_632.ConicalGearRating":
        from mastapy._private.gears.rating.conical import _632

        return self.__parent__._cast(_632.ConicalGearRating)

    @property
    def concept_gear_duty_cycle_rating(
        self: "CastSelf",
    ) -> "_640.ConceptGearDutyCycleRating":
        from mastapy._private.gears.rating.concept import _640

        return self.__parent__._cast(_640.ConceptGearDutyCycleRating)

    @property
    def concept_gear_rating(self: "CastSelf") -> "_643.ConceptGearRating":
        from mastapy._private.gears.rating.concept import _643

        return self.__parent__._cast(_643.ConceptGearRating)

    @property
    def bevel_gear_rating(self: "CastSelf") -> "_647.BevelGearRating":
        from mastapy._private.gears.rating.bevel import _647

        return self.__parent__._cast(_647.BevelGearRating)

    @property
    def agma_gleason_conical_gear_rating(
        self: "CastSelf",
    ) -> "_658.AGMAGleasonConicalGearRating":
        from mastapy._private.gears.rating.agma_gleason_conical import _658

        return self.__parent__._cast(_658.AGMAGleasonConicalGearRating)

    @property
    def cylindrical_gear_manufacturing_config(
        self: "CastSelf",
    ) -> "_716.CylindricalGearManufacturingConfig":
        from mastapy._private.gears.manufacturing.cylindrical import _716

        return self.__parent__._cast(_716.CylindricalGearManufacturingConfig)

    @property
    def cylindrical_manufactured_gear_duty_cycle(
        self: "CastSelf",
    ) -> "_720.CylindricalManufacturedGearDutyCycle":
        from mastapy._private.gears.manufacturing.cylindrical import _720

        return self.__parent__._cast(_720.CylindricalManufacturedGearDutyCycle)

    @property
    def cylindrical_manufactured_gear_load_case(
        self: "CastSelf",
    ) -> "_721.CylindricalManufacturedGearLoadCase":
        from mastapy._private.gears.manufacturing.cylindrical import _721

        return self.__parent__._cast(_721.CylindricalManufacturedGearLoadCase)

    @property
    def conical_gear_manufacturing_analysis(
        self: "CastSelf",
    ) -> "_879.ConicalGearManufacturingAnalysis":
        from mastapy._private.gears.manufacturing.bevel import _879

        return self.__parent__._cast(_879.ConicalGearManufacturingAnalysis)

    @property
    def conical_gear_manufacturing_config(
        self: "CastSelf",
    ) -> "_880.ConicalGearManufacturingConfig":
        from mastapy._private.gears.manufacturing.bevel import _880

        return self.__parent__._cast(_880.ConicalGearManufacturingConfig)

    @property
    def conical_gear_micro_geometry_config(
        self: "CastSelf",
    ) -> "_881.ConicalGearMicroGeometryConfig":
        from mastapy._private.gears.manufacturing.bevel import _881

        return self.__parent__._cast(_881.ConicalGearMicroGeometryConfig)

    @property
    def conical_gear_micro_geometry_config_base(
        self: "CastSelf",
    ) -> "_882.ConicalGearMicroGeometryConfigBase":
        from mastapy._private.gears.manufacturing.bevel import _882

        return self.__parent__._cast(_882.ConicalGearMicroGeometryConfigBase)

    @property
    def conical_pinion_manufacturing_config(
        self: "CastSelf",
    ) -> "_892.ConicalPinionManufacturingConfig":
        from mastapy._private.gears.manufacturing.bevel import _892

        return self.__parent__._cast(_892.ConicalPinionManufacturingConfig)

    @property
    def conical_pinion_micro_geometry_config(
        self: "CastSelf",
    ) -> "_893.ConicalPinionMicroGeometryConfig":
        from mastapy._private.gears.manufacturing.bevel import _893

        return self.__parent__._cast(_893.ConicalPinionMicroGeometryConfig)

    @property
    def conical_wheel_manufacturing_config(
        self: "CastSelf",
    ) -> "_898.ConicalWheelManufacturingConfig":
        from mastapy._private.gears.manufacturing.bevel import _898

        return self.__parent__._cast(_898.ConicalWheelManufacturingConfig)

    @property
    def gear_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_944.GearLoadDistributionAnalysis":
        from mastapy._private.gears.ltca import _944

        return self.__parent__._cast(_944.GearLoadDistributionAnalysis)

    @property
    def cylindrical_gear_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_959.CylindricalGearLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.cylindrical import _959

        return self.__parent__._cast(_959.CylindricalGearLoadDistributionAnalysis)

    @property
    def conical_gear_load_distribution_analysis(
        self: "CastSelf",
    ) -> "_970.ConicalGearLoadDistributionAnalysis":
        from mastapy._private.gears.ltca.conical import _970

        return self.__parent__._cast(_970.ConicalGearLoadDistributionAnalysis)

    @property
    def gear_load_case_base(self: "CastSelf") -> "_976.GearLoadCaseBase":
        from mastapy._private.gears.load_case import _976

        return self.__parent__._cast(_976.GearLoadCaseBase)

    @property
    def worm_gear_load_case(self: "CastSelf") -> "_979.WormGearLoadCase":
        from mastapy._private.gears.load_case.worm import _979

        return self.__parent__._cast(_979.WormGearLoadCase)

    @property
    def face_gear_load_case(self: "CastSelf") -> "_982.FaceGearLoadCase":
        from mastapy._private.gears.load_case.face import _982

        return self.__parent__._cast(_982.FaceGearLoadCase)

    @property
    def cylindrical_gear_load_case(self: "CastSelf") -> "_985.CylindricalGearLoadCase":
        from mastapy._private.gears.load_case.cylindrical import _985

        return self.__parent__._cast(_985.CylindricalGearLoadCase)

    @property
    def conical_gear_load_case(self: "CastSelf") -> "_988.ConicalGearLoadCase":
        from mastapy._private.gears.load_case.conical import _988

        return self.__parent__._cast(_988.ConicalGearLoadCase)

    @property
    def concept_gear_load_case(self: "CastSelf") -> "_991.ConceptGearLoadCase":
        from mastapy._private.gears.load_case.concept import _991

        return self.__parent__._cast(_991.ConceptGearLoadCase)

    @property
    def bevel_load_case(self: "CastSelf") -> "_994.BevelLoadCase":
        from mastapy._private.gears.load_case.bevel import _994

        return self.__parent__._cast(_994.BevelLoadCase)

    @property
    def cylindrical_gear_tiff_analysis(
        self: "CastSelf",
    ) -> "_1001.CylindricalGearTIFFAnalysis":
        from mastapy._private.gears.gear_two_d_fe_analysis import _1001

        return self.__parent__._cast(_1001.CylindricalGearTIFFAnalysis)

    @property
    def cylindrical_gear_tiff_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1002.CylindricalGearTIFFAnalysisDutyCycle":
        from mastapy._private.gears.gear_two_d_fe_analysis import _1002

        return self.__parent__._cast(_1002.CylindricalGearTIFFAnalysisDutyCycle)

    @property
    def face_gear_micro_geometry(self: "CastSelf") -> "_1097.FaceGearMicroGeometry":
        from mastapy._private.gears.gear_designs.face import _1097

        return self.__parent__._cast(_1097.FaceGearMicroGeometry)

    @property
    def cylindrical_gear_micro_geometry(
        self: "CastSelf",
    ) -> "_1213.CylindricalGearMicroGeometry":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1213

        return self.__parent__._cast(_1213.CylindricalGearMicroGeometry)

    @property
    def cylindrical_gear_micro_geometry_base(
        self: "CastSelf",
    ) -> "_1214.CylindricalGearMicroGeometryBase":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1214

        return self.__parent__._cast(_1214.CylindricalGearMicroGeometryBase)

    @property
    def cylindrical_gear_micro_geometry_duty_cycle(
        self: "CastSelf",
    ) -> "_1215.CylindricalGearMicroGeometryDutyCycle":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1215

        return self.__parent__._cast(_1215.CylindricalGearMicroGeometryDutyCycle)

    @property
    def cylindrical_gear_micro_geometry_per_tooth(
        self: "CastSelf",
    ) -> "_1217.CylindricalGearMicroGeometryPerTooth":
        from mastapy._private.gears.gear_designs.cylindrical.micro_geometry import _1217

        return self.__parent__._cast(_1217.CylindricalGearMicroGeometryPerTooth)

    @property
    def gear_fe_model(self: "CastSelf") -> "_1317.GearFEModel":
        from mastapy._private.gears.fe_model import _1317

        return self.__parent__._cast(_1317.GearFEModel)

    @property
    def cylindrical_gear_fe_model(self: "CastSelf") -> "_1321.CylindricalGearFEModel":
        from mastapy._private.gears.fe_model.cylindrical import _1321

        return self.__parent__._cast(_1321.CylindricalGearFEModel)

    @property
    def conical_gear_fe_model(self: "CastSelf") -> "_1324.ConicalGearFEModel":
        from mastapy._private.gears.fe_model.conical import _1324

        return self.__parent__._cast(_1324.ConicalGearFEModel)

    @property
    def gear_design_analysis(self: "CastSelf") -> "_1338.GearDesignAnalysis":
        from mastapy._private.gears.analysis import _1338

        return self.__parent__._cast(_1338.GearDesignAnalysis)

    @property
    def gear_implementation_analysis(
        self: "CastSelf",
    ) -> "_1339.GearImplementationAnalysis":
        from mastapy._private.gears.analysis import _1339

        return self.__parent__._cast(_1339.GearImplementationAnalysis)

    @property
    def gear_implementation_analysis_duty_cycle(
        self: "CastSelf",
    ) -> "_1340.GearImplementationAnalysisDutyCycle":
        from mastapy._private.gears.analysis import _1340

        return self.__parent__._cast(_1340.GearImplementationAnalysisDutyCycle)

    @property
    def gear_implementation_detail(
        self: "CastSelf",
    ) -> "_1341.GearImplementationDetail":
        from mastapy._private.gears.analysis import _1341

        return self.__parent__._cast(_1341.GearImplementationDetail)

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "AbstractGearAnalysis":
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
class AbstractGearAnalysis(_0.APIBase):
    """AbstractGearAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _ABSTRACT_GEAR_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Name")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def name_with_gear_set_name(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NameWithGearSetName")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def planet_index(self: "Self") -> "int":
        """int"""
        temp = pythonnet_property_get(self.wrapped, "PlanetIndex")

        if temp is None:
            return 0

        return temp

    @planet_index.setter
    @exception_bridge
    @enforce_parameter_types
    def planet_index(self: "Self", value: "int") -> None:
        pythonnet_property_set(
            self.wrapped, "PlanetIndex", int(value) if value is not None else 0
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
    def cast_to(self: "Self") -> "_Cast_AbstractGearAnalysis":
        """Cast to another type.

        Returns:
            _Cast_AbstractGearAnalysis
        """
        return _Cast_AbstractGearAnalysis(self)
