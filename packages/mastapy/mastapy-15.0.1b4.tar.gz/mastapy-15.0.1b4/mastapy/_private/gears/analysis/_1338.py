"""GearDesignAnalysis"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import python_net_import
from mastapy._private.gears.analysis import _1335

_GEAR_DESIGN_ANALYSIS = python_net_import(
    "SMT.MastaAPI.Gears.Analysis", "GearDesignAnalysis"
)

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.gears.analysis import _1339, _1340, _1341
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

    Self = TypeVar("Self", bound="GearDesignAnalysis")
    CastSelf = TypeVar("CastSelf", bound="GearDesignAnalysis._Cast_GearDesignAnalysis")


__docformat__ = "restructuredtext en"
__all__ = ("GearDesignAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_GearDesignAnalysis:
    """Special nested class for casting GearDesignAnalysis to subclasses."""

    __parent__: "GearDesignAnalysis"

    @property
    def abstract_gear_analysis(self: "CastSelf") -> "_1335.AbstractGearAnalysis":
        return self.__parent__._cast(_1335.AbstractGearAnalysis)

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
    def gear_design_analysis(self: "CastSelf") -> "GearDesignAnalysis":
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
class GearDesignAnalysis(_1335.AbstractGearAnalysis):
    """GearDesignAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _GEAR_DESIGN_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    def cast_to(self: "Self") -> "_Cast_GearDesignAnalysis":
        """Cast to another type.

        Returns:
            _Cast_GearDesignAnalysis
        """
        return _Cast_GearDesignAnalysis(self)
