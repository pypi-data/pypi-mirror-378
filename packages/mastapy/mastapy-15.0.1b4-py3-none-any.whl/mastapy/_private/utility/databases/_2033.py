"""NamedDatabaseItem"""

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

_NAMED_DATABASE_ITEM = python_net_import(
    "SMT.MastaAPI.Utility.Databases", "NamedDatabaseItem"
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private._internal.typing import PathLike
    from mastapy._private.bearings import _2089
    from mastapy._private.bearings.bearing_results.rolling import _2186
    from mastapy._private.bolts import _1651, _1653, _1655
    from mastapy._private.cycloidal import _1641, _1648
    from mastapy._private.detailed_rigid_connectors.splines import _1601
    from mastapy._private.electric_machines import _1404, _1418, _1437, _1452
    from mastapy._private.gears import _433
    from mastapy._private.gears.gear_designs import _1045, _1047, _1050
    from mastapy._private.gears.gear_designs.cylindrical import _1124, _1132
    from mastapy._private.gears.manufacturing.bevel import _903
    from mastapy._private.gears.manufacturing.cylindrical.cutters import (
        _810,
        _811,
        _812,
        _813,
        _814,
        _816,
        _817,
        _818,
        _819,
        _822,
    )
    from mastapy._private.gears.materials import (
        _675,
        _678,
        _680,
        _685,
        _689,
        _697,
        _699,
        _702,
        _706,
        _709,
    )
    from mastapy._private.gears.rating.cylindrical import _546, _562
    from mastapy._private.materials import _333, _343, _357, _359, _363
    from mastapy._private.math_utility.optimisation import _1738
    from mastapy._private.nodal_analysis import _53
    from mastapy._private.shafts import _24, _43, _46
    from mastapy._private.system_model.optimization import _2442, _2445, _2451, _2452
    from mastapy._private.system_model.optimization.machine_learning import _2460
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set import (
        _2806,
    )
    from mastapy._private.utility import _1780
    from mastapy._private.utility.databases import _2034

    Self = TypeVar("Self", bound="NamedDatabaseItem")
    CastSelf = TypeVar("CastSelf", bound="NamedDatabaseItem._Cast_NamedDatabaseItem")


__docformat__ = "restructuredtext en"
__all__ = ("NamedDatabaseItem",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_NamedDatabaseItem:
    """Special nested class for casting NamedDatabaseItem to subclasses."""

    __parent__: "NamedDatabaseItem"

    @property
    def shaft_material(self: "CastSelf") -> "_24.ShaftMaterial":
        from mastapy._private.shafts import _24

        return self.__parent__._cast(_24.ShaftMaterial)

    @property
    def shaft_settings_item(self: "CastSelf") -> "_43.ShaftSettingsItem":
        from mastapy._private.shafts import _43

        return self.__parent__._cast(_43.ShaftSettingsItem)

    @property
    def simple_shaft_definition(self: "CastSelf") -> "_46.SimpleShaftDefinition":
        from mastapy._private.shafts import _46

        return self.__parent__._cast(_46.SimpleShaftDefinition)

    @property
    def analysis_settings_item(self: "CastSelf") -> "_53.AnalysisSettingsItem":
        from mastapy._private.nodal_analysis import _53

        return self.__parent__._cast(_53.AnalysisSettingsItem)

    @property
    def bearing_material(self: "CastSelf") -> "_333.BearingMaterial":
        from mastapy._private.materials import _333

        return self.__parent__._cast(_333.BearingMaterial)

    @property
    def fluid(self: "CastSelf") -> "_343.Fluid":
        from mastapy._private.materials import _343

        return self.__parent__._cast(_343.Fluid)

    @property
    def lubrication_detail(self: "CastSelf") -> "_357.LubricationDetail":
        from mastapy._private.materials import _357

        return self.__parent__._cast(_357.LubricationDetail)

    @property
    def material(self: "CastSelf") -> "_359.Material":
        from mastapy._private.materials import _359

        return self.__parent__._cast(_359.Material)

    @property
    def materials_settings_item(self: "CastSelf") -> "_363.MaterialsSettingsItem":
        from mastapy._private.materials import _363

        return self.__parent__._cast(_363.MaterialsSettingsItem)

    @property
    def pocketing_power_loss_coefficients(
        self: "CastSelf",
    ) -> "_433.PocketingPowerLossCoefficients":
        from mastapy._private.gears import _433

        return self.__parent__._cast(_433.PocketingPowerLossCoefficients)

    @property
    def cylindrical_gear_design_and_rating_settings_item(
        self: "CastSelf",
    ) -> "_546.CylindricalGearDesignAndRatingSettingsItem":
        from mastapy._private.gears.rating.cylindrical import _546

        return self.__parent__._cast(_546.CylindricalGearDesignAndRatingSettingsItem)

    @property
    def cylindrical_plastic_gear_rating_settings_item(
        self: "CastSelf",
    ) -> "_562.CylindricalPlasticGearRatingSettingsItem":
        from mastapy._private.gears.rating.cylindrical import _562

        return self.__parent__._cast(_562.CylindricalPlasticGearRatingSettingsItem)

    @property
    def agma_cylindrical_gear_material(
        self: "CastSelf",
    ) -> "_675.AGMACylindricalGearMaterial":
        from mastapy._private.gears.materials import _675

        return self.__parent__._cast(_675.AGMACylindricalGearMaterial)

    @property
    def bevel_gear_iso_material(self: "CastSelf") -> "_678.BevelGearISOMaterial":
        from mastapy._private.gears.materials import _678

        return self.__parent__._cast(_678.BevelGearISOMaterial)

    @property
    def bevel_gear_material(self: "CastSelf") -> "_680.BevelGearMaterial":
        from mastapy._private.gears.materials import _680

        return self.__parent__._cast(_680.BevelGearMaterial)

    @property
    def cylindrical_gear_material(self: "CastSelf") -> "_685.CylindricalGearMaterial":
        from mastapy._private.gears.materials import _685

        return self.__parent__._cast(_685.CylindricalGearMaterial)

    @property
    def gear_material(self: "CastSelf") -> "_689.GearMaterial":
        from mastapy._private.gears.materials import _689

        return self.__parent__._cast(_689.GearMaterial)

    @property
    def iso_cylindrical_gear_material(
        self: "CastSelf",
    ) -> "_697.ISOCylindricalGearMaterial":
        from mastapy._private.gears.materials import _697

        return self.__parent__._cast(_697.ISOCylindricalGearMaterial)

    @property
    def isotr1417912001_coefficient_of_friction_constants(
        self: "CastSelf",
    ) -> "_699.ISOTR1417912001CoefficientOfFrictionConstants":
        from mastapy._private.gears.materials import _699

        return self.__parent__._cast(_699.ISOTR1417912001CoefficientOfFrictionConstants)

    @property
    def klingelnberg_cyclo_palloid_conical_gear_material(
        self: "CastSelf",
    ) -> "_702.KlingelnbergCycloPalloidConicalGearMaterial":
        from mastapy._private.gears.materials import _702

        return self.__parent__._cast(_702.KlingelnbergCycloPalloidConicalGearMaterial)

    @property
    def plastic_cylindrical_gear_material(
        self: "CastSelf",
    ) -> "_706.PlasticCylindricalGearMaterial":
        from mastapy._private.gears.materials import _706

        return self.__parent__._cast(_706.PlasticCylindricalGearMaterial)

    @property
    def raw_material(self: "CastSelf") -> "_709.RawMaterial":
        from mastapy._private.gears.materials import _709

        return self.__parent__._cast(_709.RawMaterial)

    @property
    def cylindrical_gear_abstract_cutter_design(
        self: "CastSelf",
    ) -> "_810.CylindricalGearAbstractCutterDesign":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _810

        return self.__parent__._cast(_810.CylindricalGearAbstractCutterDesign)

    @property
    def cylindrical_gear_form_grinding_wheel(
        self: "CastSelf",
    ) -> "_811.CylindricalGearFormGrindingWheel":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _811

        return self.__parent__._cast(_811.CylindricalGearFormGrindingWheel)

    @property
    def cylindrical_gear_grinding_worm(
        self: "CastSelf",
    ) -> "_812.CylindricalGearGrindingWorm":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _812

        return self.__parent__._cast(_812.CylindricalGearGrindingWorm)

    @property
    def cylindrical_gear_hob_design(
        self: "CastSelf",
    ) -> "_813.CylindricalGearHobDesign":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _813

        return self.__parent__._cast(_813.CylindricalGearHobDesign)

    @property
    def cylindrical_gear_plunge_shaver(
        self: "CastSelf",
    ) -> "_814.CylindricalGearPlungeShaver":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _814

        return self.__parent__._cast(_814.CylindricalGearPlungeShaver)

    @property
    def cylindrical_gear_rack_design(
        self: "CastSelf",
    ) -> "_816.CylindricalGearRackDesign":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _816

        return self.__parent__._cast(_816.CylindricalGearRackDesign)

    @property
    def cylindrical_gear_real_cutter_design(
        self: "CastSelf",
    ) -> "_817.CylindricalGearRealCutterDesign":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _817

        return self.__parent__._cast(_817.CylindricalGearRealCutterDesign)

    @property
    def cylindrical_gear_shaper(self: "CastSelf") -> "_818.CylindricalGearShaper":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _818

        return self.__parent__._cast(_818.CylindricalGearShaper)

    @property
    def cylindrical_gear_shaver(self: "CastSelf") -> "_819.CylindricalGearShaver":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _819

        return self.__parent__._cast(_819.CylindricalGearShaver)

    @property
    def involute_cutter_design(self: "CastSelf") -> "_822.InvoluteCutterDesign":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _822

        return self.__parent__._cast(_822.InvoluteCutterDesign)

    @property
    def manufacturing_machine(self: "CastSelf") -> "_903.ManufacturingMachine":
        from mastapy._private.gears.manufacturing.bevel import _903

        return self.__parent__._cast(_903.ManufacturingMachine)

    @property
    def bevel_hypoid_gear_design_settings_item(
        self: "CastSelf",
    ) -> "_1045.BevelHypoidGearDesignSettingsItem":
        from mastapy._private.gears.gear_designs import _1045

        return self.__parent__._cast(_1045.BevelHypoidGearDesignSettingsItem)

    @property
    def bevel_hypoid_gear_rating_settings_item(
        self: "CastSelf",
    ) -> "_1047.BevelHypoidGearRatingSettingsItem":
        from mastapy._private.gears.gear_designs import _1047

        return self.__parent__._cast(_1047.BevelHypoidGearRatingSettingsItem)

    @property
    def design_constraints_collection(
        self: "CastSelf",
    ) -> "_1050.DesignConstraintsCollection":
        from mastapy._private.gears.gear_designs import _1050

        return self.__parent__._cast(_1050.DesignConstraintsCollection)

    @property
    def cylindrical_gear_design_constraints(
        self: "CastSelf",
    ) -> "_1124.CylindricalGearDesignConstraints":
        from mastapy._private.gears.gear_designs.cylindrical import _1124

        return self.__parent__._cast(_1124.CylindricalGearDesignConstraints)

    @property
    def cylindrical_gear_micro_geometry_settings_item(
        self: "CastSelf",
    ) -> "_1132.CylindricalGearMicroGeometrySettingsItem":
        from mastapy._private.gears.gear_designs.cylindrical import _1132

        return self.__parent__._cast(_1132.CylindricalGearMicroGeometrySettingsItem)

    @property
    def general_electric_machine_material(
        self: "CastSelf",
    ) -> "_1404.GeneralElectricMachineMaterial":
        from mastapy._private.electric_machines import _1404

        return self.__parent__._cast(_1404.GeneralElectricMachineMaterial)

    @property
    def magnet_material(self: "CastSelf") -> "_1418.MagnetMaterial":
        from mastapy._private.electric_machines import _1418

        return self.__parent__._cast(_1418.MagnetMaterial)

    @property
    def stator_rotor_material(self: "CastSelf") -> "_1437.StatorRotorMaterial":
        from mastapy._private.electric_machines import _1437

        return self.__parent__._cast(_1437.StatorRotorMaterial)

    @property
    def winding_material(self: "CastSelf") -> "_1452.WindingMaterial":
        from mastapy._private.electric_machines import _1452

        return self.__parent__._cast(_1452.WindingMaterial)

    @property
    def spline_material(self: "CastSelf") -> "_1601.SplineMaterial":
        from mastapy._private.detailed_rigid_connectors.splines import _1601

        return self.__parent__._cast(_1601.SplineMaterial)

    @property
    def cycloidal_disc_material(self: "CastSelf") -> "_1641.CycloidalDiscMaterial":
        from mastapy._private.cycloidal import _1641

        return self.__parent__._cast(_1641.CycloidalDiscMaterial)

    @property
    def ring_pins_material(self: "CastSelf") -> "_1648.RingPinsMaterial":
        from mastapy._private.cycloidal import _1648

        return self.__parent__._cast(_1648.RingPinsMaterial)

    @property
    def bolted_joint_material(self: "CastSelf") -> "_1651.BoltedJointMaterial":
        from mastapy._private.bolts import _1651

        return self.__parent__._cast(_1651.BoltedJointMaterial)

    @property
    def bolt_geometry(self: "CastSelf") -> "_1653.BoltGeometry":
        from mastapy._private.bolts import _1653

        return self.__parent__._cast(_1653.BoltGeometry)

    @property
    def bolt_material(self: "CastSelf") -> "_1655.BoltMaterial":
        from mastapy._private.bolts import _1655

        return self.__parent__._cast(_1655.BoltMaterial)

    @property
    def pareto_optimisation_strategy(
        self: "CastSelf",
    ) -> "_1738.ParetoOptimisationStrategy":
        from mastapy._private.math_utility.optimisation import _1738

        return self.__parent__._cast(_1738.ParetoOptimisationStrategy)

    @property
    def bearing_settings_item(self: "CastSelf") -> "_2089.BearingSettingsItem":
        from mastapy._private.bearings import _2089

        return self.__parent__._cast(_2089.BearingSettingsItem)

    @property
    def iso14179_settings(self: "CastSelf") -> "_2186.ISO14179Settings":
        from mastapy._private.bearings.bearing_results.rolling import _2186

        return self.__parent__._cast(_2186.ISO14179Settings)

    @property
    def conical_gear_optimisation_strategy(
        self: "CastSelf",
    ) -> "_2442.ConicalGearOptimisationStrategy":
        from mastapy._private.system_model.optimization import _2442

        return self.__parent__._cast(_2442.ConicalGearOptimisationStrategy)

    @property
    def cylindrical_gear_optimisation_strategy(
        self: "CastSelf",
    ) -> "_2445.CylindricalGearOptimisationStrategy":
        from mastapy._private.system_model.optimization import _2445

        return self.__parent__._cast(_2445.CylindricalGearOptimisationStrategy)

    @property
    def optimization_strategy(self: "CastSelf") -> "_2451.OptimizationStrategy":
        from mastapy._private.system_model.optimization import _2451

        return self.__parent__._cast(_2451.OptimizationStrategy)

    @property
    def optimization_strategy_base(
        self: "CastSelf",
    ) -> "_2452.OptimizationStrategyBase":
        from mastapy._private.system_model.optimization import _2452

        return self.__parent__._cast(_2452.OptimizationStrategyBase)

    @property
    def cylindrical_gear_flank_optimisation_parameters(
        self: "CastSelf",
    ) -> "_2460.CylindricalGearFlankOptimisationParameters":
        from mastapy._private.system_model.optimization.machine_learning import _2460

        return self.__parent__._cast(_2460.CylindricalGearFlankOptimisationParameters)

    @property
    def supercharger_rotor_set(self: "CastSelf") -> "_2806.SuperchargerRotorSet":
        from mastapy._private.system_model.part_model.gears.supercharger_rotor_set import (
            _2806,
        )

        return self.__parent__._cast(_2806.SuperchargerRotorSet)

    @property
    def named_database_item(self: "CastSelf") -> "NamedDatabaseItem":
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
class NamedDatabaseItem(_0.APIBase):
    """NamedDatabaseItem

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _NAMED_DATABASE_ITEM

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def comment(self: "Self") -> "str":
        """str"""
        temp = pythonnet_property_get(self.wrapped, "Comment")

        if temp is None:
            return ""

        return temp

    @comment.setter
    @exception_bridge
    @enforce_parameter_types
    def comment(self: "Self", value: "str") -> None:
        pythonnet_property_set(
            self.wrapped, "Comment", str(value) if value is not None else ""
        )

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
    def no_history(self: "Self") -> "str":
        """str

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "NoHistory")

        if temp is None:
            return ""

        return temp

    @property
    @exception_bridge
    def history(self: "Self") -> "_1780.FileHistory":
        """mastapy.utility.FileHistory

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "History")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def database_key(self: "Self") -> "_2034.NamedKey":
        """mastapy.utility.databases.NamedKey"""
        temp = pythonnet_property_get(self.wrapped, "DatabaseKey")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @database_key.setter
    @exception_bridge
    @enforce_parameter_types
    def database_key(self: "Self", value: "_2034.NamedKey") -> None:
        pythonnet_property_set(self.wrapped, "DatabaseKey", value.wrapped)

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
    def cast_to(self: "Self") -> "_Cast_NamedDatabaseItem":
        """Cast to another type.

        Returns:
            _Cast_NamedDatabaseItem
        """
        return _Cast_NamedDatabaseItem(self)
