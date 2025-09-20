"""SQLDatabase"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, TypeVar

from mastapy._private import _0
from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private._internal.type_enforcement import enforce_parameter_types
from mastapy._private.utility.databases import _2028

_SQL_DATABASE = python_net_import("SMT.MastaAPI.Utility.Databases", "SQLDatabase")

if TYPE_CHECKING:
    from typing import Any, Type

    from mastapy._private import _7906
    from mastapy._private.bearings import _2088, _2101
    from mastapy._private.bearings.bearing_results.rolling import _2187
    from mastapy._private.bolts import _1652, _1654, _1656, _1661
    from mastapy._private.cycloidal import _1642, _1649
    from mastapy._private.electric_machines import _1405, _1419, _1438, _1453
    from mastapy._private.gears import _434
    from mastapy._private.gears.gear_designs import _1044, _1046, _1049
    from mastapy._private.gears.gear_designs.cylindrical import _1125, _1131
    from mastapy._private.gears.gear_set_pareto_optimiser import (
        _1022,
        _1024,
        _1025,
        _1027,
        _1028,
        _1029,
        _1030,
        _1031,
        _1032,
        _1033,
        _1034,
        _1035,
        _1037,
        _1038,
        _1039,
        _1040,
    )
    from mastapy._private.gears.manufacturing.bevel import _904
    from mastapy._private.gears.manufacturing.cylindrical import _714, _719, _730
    from mastapy._private.gears.manufacturing.cylindrical.cutters import (
        _809,
        _815,
        _820,
        _821,
    )
    from mastapy._private.gears.materials import (
        _677,
        _679,
        _681,
        _683,
        _684,
        _686,
        _687,
        _690,
        _700,
        _701,
        _710,
    )
    from mastapy._private.gears.rating.cylindrical import _545, _561
    from mastapy._private.materials import _334, _337, _344, _358, _360, _362
    from mastapy._private.math_utility.optimisation import _1728, _1741
    from mastapy._private.nodal_analysis import _52
    from mastapy._private.shafts import _25, _42
    from mastapy._private.system_model.optimization import _2444, _2453
    from mastapy._private.system_model.optimization.machine_learning import _2461
    from mastapy._private.system_model.part_model.gears.supercharger_rotor_set import (
        _2807,
    )
    from mastapy._private.utility.databases import _2030, _2032

    Self = TypeVar("Self", bound="SQLDatabase")
    CastSelf = TypeVar("CastSelf", bound="SQLDatabase._Cast_SQLDatabase")

TKey = TypeVar("TKey", bound="_2030.DatabaseKey")
TValue = TypeVar("TValue", bound="_0.APIBase")

__docformat__ = "restructuredtext en"
__all__ = ("SQLDatabase",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_SQLDatabase:
    """Special nested class for casting SQLDatabase to subclasses."""

    __parent__: "SQLDatabase"

    @property
    def database(self: "CastSelf") -> "_2028.Database":
        return self.__parent__._cast(_2028.Database)

    @property
    def shaft_material_database(self: "CastSelf") -> "_25.ShaftMaterialDatabase":
        from mastapy._private.shafts import _25

        return self.__parent__._cast(_25.ShaftMaterialDatabase)

    @property
    def shaft_settings_database(self: "CastSelf") -> "_42.ShaftSettingsDatabase":
        from mastapy._private.shafts import _42

        return self.__parent__._cast(_42.ShaftSettingsDatabase)

    @property
    def analysis_settings_database(self: "CastSelf") -> "_52.AnalysisSettingsDatabase":
        from mastapy._private.nodal_analysis import _52

        return self.__parent__._cast(_52.AnalysisSettingsDatabase)

    @property
    def bearing_material_database(self: "CastSelf") -> "_334.BearingMaterialDatabase":
        from mastapy._private.materials import _334

        return self.__parent__._cast(_334.BearingMaterialDatabase)

    @property
    def component_material_database(
        self: "CastSelf",
    ) -> "_337.ComponentMaterialDatabase":
        from mastapy._private.materials import _337

        return self.__parent__._cast(_337.ComponentMaterialDatabase)

    @property
    def fluid_database(self: "CastSelf") -> "_344.FluidDatabase":
        from mastapy._private.materials import _344

        return self.__parent__._cast(_344.FluidDatabase)

    @property
    def lubrication_detail_database(
        self: "CastSelf",
    ) -> "_358.LubricationDetailDatabase":
        from mastapy._private.materials import _358

        return self.__parent__._cast(_358.LubricationDetailDatabase)

    @property
    def material_database(self: "CastSelf") -> "_360.MaterialDatabase":
        from mastapy._private.materials import _360

        return self.__parent__._cast(_360.MaterialDatabase)

    @property
    def materials_settings_database(
        self: "CastSelf",
    ) -> "_362.MaterialsSettingsDatabase":
        from mastapy._private.materials import _362

        return self.__parent__._cast(_362.MaterialsSettingsDatabase)

    @property
    def pocketing_power_loss_coefficients_database(
        self: "CastSelf",
    ) -> "_434.PocketingPowerLossCoefficientsDatabase":
        from mastapy._private.gears import _434

        return self.__parent__._cast(_434.PocketingPowerLossCoefficientsDatabase)

    @property
    def cylindrical_gear_design_and_rating_settings_database(
        self: "CastSelf",
    ) -> "_545.CylindricalGearDesignAndRatingSettingsDatabase":
        from mastapy._private.gears.rating.cylindrical import _545

        return self.__parent__._cast(
            _545.CylindricalGearDesignAndRatingSettingsDatabase
        )

    @property
    def cylindrical_plastic_gear_rating_settings_database(
        self: "CastSelf",
    ) -> "_561.CylindricalPlasticGearRatingSettingsDatabase":
        from mastapy._private.gears.rating.cylindrical import _561

        return self.__parent__._cast(_561.CylindricalPlasticGearRatingSettingsDatabase)

    @property
    def bevel_gear_abstract_material_database(
        self: "CastSelf",
    ) -> "_677.BevelGearAbstractMaterialDatabase":
        from mastapy._private.gears.materials import _677

        return self.__parent__._cast(_677.BevelGearAbstractMaterialDatabase)

    @property
    def bevel_gear_iso_material_database(
        self: "CastSelf",
    ) -> "_679.BevelGearISOMaterialDatabase":
        from mastapy._private.gears.materials import _679

        return self.__parent__._cast(_679.BevelGearISOMaterialDatabase)

    @property
    def bevel_gear_material_database(
        self: "CastSelf",
    ) -> "_681.BevelGearMaterialDatabase":
        from mastapy._private.gears.materials import _681

        return self.__parent__._cast(_681.BevelGearMaterialDatabase)

    @property
    def cylindrical_gear_agma_material_database(
        self: "CastSelf",
    ) -> "_683.CylindricalGearAGMAMaterialDatabase":
        from mastapy._private.gears.materials import _683

        return self.__parent__._cast(_683.CylindricalGearAGMAMaterialDatabase)

    @property
    def cylindrical_gear_iso_material_database(
        self: "CastSelf",
    ) -> "_684.CylindricalGearISOMaterialDatabase":
        from mastapy._private.gears.materials import _684

        return self.__parent__._cast(_684.CylindricalGearISOMaterialDatabase)

    @property
    def cylindrical_gear_material_database(
        self: "CastSelf",
    ) -> "_686.CylindricalGearMaterialDatabase":
        from mastapy._private.gears.materials import _686

        return self.__parent__._cast(_686.CylindricalGearMaterialDatabase)

    @property
    def cylindrical_gear_plastic_material_database(
        self: "CastSelf",
    ) -> "_687.CylindricalGearPlasticMaterialDatabase":
        from mastapy._private.gears.materials import _687

        return self.__parent__._cast(_687.CylindricalGearPlasticMaterialDatabase)

    @property
    def gear_material_database(self: "CastSelf") -> "_690.GearMaterialDatabase":
        from mastapy._private.gears.materials import _690

        return self.__parent__._cast(_690.GearMaterialDatabase)

    @property
    def isotr1417912001_coefficient_of_friction_constants_database(
        self: "CastSelf",
    ) -> "_700.ISOTR1417912001CoefficientOfFrictionConstantsDatabase":
        from mastapy._private.gears.materials import _700

        return self.__parent__._cast(
            _700.ISOTR1417912001CoefficientOfFrictionConstantsDatabase
        )

    @property
    def klingelnberg_conical_gear_material_database(
        self: "CastSelf",
    ) -> "_701.KlingelnbergConicalGearMaterialDatabase":
        from mastapy._private.gears.materials import _701

        return self.__parent__._cast(_701.KlingelnbergConicalGearMaterialDatabase)

    @property
    def raw_material_database(self: "CastSelf") -> "_710.RawMaterialDatabase":
        from mastapy._private.gears.materials import _710

        return self.__parent__._cast(_710.RawMaterialDatabase)

    @property
    def cylindrical_cutter_database(
        self: "CastSelf",
    ) -> "_714.CylindricalCutterDatabase":
        from mastapy._private.gears.manufacturing.cylindrical import _714

        return self.__parent__._cast(_714.CylindricalCutterDatabase)

    @property
    def cylindrical_hob_database(self: "CastSelf") -> "_719.CylindricalHobDatabase":
        from mastapy._private.gears.manufacturing.cylindrical import _719

        return self.__parent__._cast(_719.CylindricalHobDatabase)

    @property
    def cylindrical_shaper_database(
        self: "CastSelf",
    ) -> "_730.CylindricalShaperDatabase":
        from mastapy._private.gears.manufacturing.cylindrical import _730

        return self.__parent__._cast(_730.CylindricalShaperDatabase)

    @property
    def cylindrical_formed_wheel_grinder_database(
        self: "CastSelf",
    ) -> "_809.CylindricalFormedWheelGrinderDatabase":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _809

        return self.__parent__._cast(_809.CylindricalFormedWheelGrinderDatabase)

    @property
    def cylindrical_gear_plunge_shaver_database(
        self: "CastSelf",
    ) -> "_815.CylindricalGearPlungeShaverDatabase":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _815

        return self.__parent__._cast(_815.CylindricalGearPlungeShaverDatabase)

    @property
    def cylindrical_gear_shaver_database(
        self: "CastSelf",
    ) -> "_820.CylindricalGearShaverDatabase":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _820

        return self.__parent__._cast(_820.CylindricalGearShaverDatabase)

    @property
    def cylindrical_worm_grinder_database(
        self: "CastSelf",
    ) -> "_821.CylindricalWormGrinderDatabase":
        from mastapy._private.gears.manufacturing.cylindrical.cutters import _821

        return self.__parent__._cast(_821.CylindricalWormGrinderDatabase)

    @property
    def manufacturing_machine_database(
        self: "CastSelf",
    ) -> "_904.ManufacturingMachineDatabase":
        from mastapy._private.gears.manufacturing.bevel import _904

        return self.__parent__._cast(_904.ManufacturingMachineDatabase)

    @property
    def micro_geometry_design_space_search_strategy_database(
        self: "CastSelf",
    ) -> "_1022.MicroGeometryDesignSpaceSearchStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1022

        return self.__parent__._cast(
            _1022.MicroGeometryDesignSpaceSearchStrategyDatabase
        )

    @property
    def micro_geometry_gear_set_design_space_search_strategy_database(
        self: "CastSelf",
    ) -> "_1024.MicroGeometryGearSetDesignSpaceSearchStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1024

        return self.__parent__._cast(
            _1024.MicroGeometryGearSetDesignSpaceSearchStrategyDatabase
        )

    @property
    def micro_geometry_gear_set_duty_cycle_design_space_search_strategy_database(
        self: "CastSelf",
    ) -> "_1025.MicroGeometryGearSetDutyCycleDesignSpaceSearchStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1025

        return self.__parent__._cast(
            _1025.MicroGeometryGearSetDutyCycleDesignSpaceSearchStrategyDatabase
        )

    @property
    def pareto_conical_rating_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1027.ParetoConicalRatingOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1027

        return self.__parent__._cast(
            _1027.ParetoConicalRatingOptimisationStrategyDatabase
        )

    @property
    def pareto_cylindrical_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1028.ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1028

        return self.__parent__._cast(
            _1028.ParetoCylindricalGearSetDutyCycleOptimisationStrategyDatabase
        )

    @property
    def pareto_cylindrical_gear_set_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1029.ParetoCylindricalGearSetOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1029

        return self.__parent__._cast(
            _1029.ParetoCylindricalGearSetOptimisationStrategyDatabase
        )

    @property
    def pareto_cylindrical_rating_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1030.ParetoCylindricalRatingOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1030

        return self.__parent__._cast(
            _1030.ParetoCylindricalRatingOptimisationStrategyDatabase
        )

    @property
    def pareto_face_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1031.ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1031

        return self.__parent__._cast(
            _1031.ParetoFaceGearSetDutyCycleOptimisationStrategyDatabase
        )

    @property
    def pareto_face_gear_set_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1032.ParetoFaceGearSetOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1032

        return self.__parent__._cast(
            _1032.ParetoFaceGearSetOptimisationStrategyDatabase
        )

    @property
    def pareto_face_rating_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1033.ParetoFaceRatingOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1033

        return self.__parent__._cast(_1033.ParetoFaceRatingOptimisationStrategyDatabase)

    @property
    def pareto_hypoid_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1034.ParetoHypoidGearSetDutyCycleOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1034

        return self.__parent__._cast(
            _1034.ParetoHypoidGearSetDutyCycleOptimisationStrategyDatabase
        )

    @property
    def pareto_hypoid_gear_set_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1035.ParetoHypoidGearSetOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1035

        return self.__parent__._cast(
            _1035.ParetoHypoidGearSetOptimisationStrategyDatabase
        )

    @property
    def pareto_spiral_bevel_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1037.ParetoSpiralBevelGearSetDutyCycleOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1037

        return self.__parent__._cast(
            _1037.ParetoSpiralBevelGearSetDutyCycleOptimisationStrategyDatabase
        )

    @property
    def pareto_spiral_bevel_gear_set_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1038.ParetoSpiralBevelGearSetOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1038

        return self.__parent__._cast(
            _1038.ParetoSpiralBevelGearSetOptimisationStrategyDatabase
        )

    @property
    def pareto_straight_bevel_gear_set_duty_cycle_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1039.ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1039

        return self.__parent__._cast(
            _1039.ParetoStraightBevelGearSetDutyCycleOptimisationStrategyDatabase
        )

    @property
    def pareto_straight_bevel_gear_set_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1040.ParetoStraightBevelGearSetOptimisationStrategyDatabase":
        from mastapy._private.gears.gear_set_pareto_optimiser import _1040

        return self.__parent__._cast(
            _1040.ParetoStraightBevelGearSetOptimisationStrategyDatabase
        )

    @property
    def bevel_hypoid_gear_design_settings_database(
        self: "CastSelf",
    ) -> "_1044.BevelHypoidGearDesignSettingsDatabase":
        from mastapy._private.gears.gear_designs import _1044

        return self.__parent__._cast(_1044.BevelHypoidGearDesignSettingsDatabase)

    @property
    def bevel_hypoid_gear_rating_settings_database(
        self: "CastSelf",
    ) -> "_1046.BevelHypoidGearRatingSettingsDatabase":
        from mastapy._private.gears.gear_designs import _1046

        return self.__parent__._cast(_1046.BevelHypoidGearRatingSettingsDatabase)

    @property
    def design_constraint_collection_database(
        self: "CastSelf",
    ) -> "_1049.DesignConstraintCollectionDatabase":
        from mastapy._private.gears.gear_designs import _1049

        return self.__parent__._cast(_1049.DesignConstraintCollectionDatabase)

    @property
    def cylindrical_gear_design_constraints_database(
        self: "CastSelf",
    ) -> "_1125.CylindricalGearDesignConstraintsDatabase":
        from mastapy._private.gears.gear_designs.cylindrical import _1125

        return self.__parent__._cast(_1125.CylindricalGearDesignConstraintsDatabase)

    @property
    def cylindrical_gear_micro_geometry_settings_database(
        self: "CastSelf",
    ) -> "_1131.CylindricalGearMicroGeometrySettingsDatabase":
        from mastapy._private.gears.gear_designs.cylindrical import _1131

        return self.__parent__._cast(_1131.CylindricalGearMicroGeometrySettingsDatabase)

    @property
    def general_electric_machine_material_database(
        self: "CastSelf",
    ) -> "_1405.GeneralElectricMachineMaterialDatabase":
        from mastapy._private.electric_machines import _1405

        return self.__parent__._cast(_1405.GeneralElectricMachineMaterialDatabase)

    @property
    def magnet_material_database(self: "CastSelf") -> "_1419.MagnetMaterialDatabase":
        from mastapy._private.electric_machines import _1419

        return self.__parent__._cast(_1419.MagnetMaterialDatabase)

    @property
    def stator_rotor_material_database(
        self: "CastSelf",
    ) -> "_1438.StatorRotorMaterialDatabase":
        from mastapy._private.electric_machines import _1438

        return self.__parent__._cast(_1438.StatorRotorMaterialDatabase)

    @property
    def winding_material_database(self: "CastSelf") -> "_1453.WindingMaterialDatabase":
        from mastapy._private.electric_machines import _1453

        return self.__parent__._cast(_1453.WindingMaterialDatabase)

    @property
    def cycloidal_disc_material_database(
        self: "CastSelf",
    ) -> "_1642.CycloidalDiscMaterialDatabase":
        from mastapy._private.cycloidal import _1642

        return self.__parent__._cast(_1642.CycloidalDiscMaterialDatabase)

    @property
    def ring_pins_material_database(
        self: "CastSelf",
    ) -> "_1649.RingPinsMaterialDatabase":
        from mastapy._private.cycloidal import _1649

        return self.__parent__._cast(_1649.RingPinsMaterialDatabase)

    @property
    def bolted_joint_material_database(
        self: "CastSelf",
    ) -> "_1652.BoltedJointMaterialDatabase":
        from mastapy._private.bolts import _1652

        return self.__parent__._cast(_1652.BoltedJointMaterialDatabase)

    @property
    def bolt_geometry_database(self: "CastSelf") -> "_1654.BoltGeometryDatabase":
        from mastapy._private.bolts import _1654

        return self.__parent__._cast(_1654.BoltGeometryDatabase)

    @property
    def bolt_material_database(self: "CastSelf") -> "_1656.BoltMaterialDatabase":
        from mastapy._private.bolts import _1656

        return self.__parent__._cast(_1656.BoltMaterialDatabase)

    @property
    def clamped_section_material_database(
        self: "CastSelf",
    ) -> "_1661.ClampedSectionMaterialDatabase":
        from mastapy._private.bolts import _1661

        return self.__parent__._cast(_1661.ClampedSectionMaterialDatabase)

    @property
    def design_space_search_strategy_database(
        self: "CastSelf",
    ) -> "_1728.DesignSpaceSearchStrategyDatabase":
        from mastapy._private.math_utility.optimisation import _1728

        return self.__parent__._cast(_1728.DesignSpaceSearchStrategyDatabase)

    @property
    def pareto_optimisation_strategy_database(
        self: "CastSelf",
    ) -> "_1741.ParetoOptimisationStrategyDatabase":
        from mastapy._private.math_utility.optimisation import _1741

        return self.__parent__._cast(_1741.ParetoOptimisationStrategyDatabase)

    @property
    def named_database(self: "CastSelf") -> "_2032.NamedDatabase":
        from mastapy._private.utility.databases import _2032

        return self.__parent__._cast(_2032.NamedDatabase)

    @property
    def bearing_settings_database(self: "CastSelf") -> "_2088.BearingSettingsDatabase":
        from mastapy._private.bearings import _2088

        return self.__parent__._cast(_2088.BearingSettingsDatabase)

    @property
    def rolling_bearing_database(self: "CastSelf") -> "_2101.RollingBearingDatabase":
        from mastapy._private.bearings import _2101

        return self.__parent__._cast(_2101.RollingBearingDatabase)

    @property
    def iso14179_settings_database(
        self: "CastSelf",
    ) -> "_2187.ISO14179SettingsDatabase":
        from mastapy._private.bearings.bearing_results.rolling import _2187

        return self.__parent__._cast(_2187.ISO14179SettingsDatabase)

    @property
    def conical_gear_optimization_strategy_database(
        self: "CastSelf",
    ) -> "_2444.ConicalGearOptimizationStrategyDatabase":
        from mastapy._private.system_model.optimization import _2444

        return self.__parent__._cast(_2444.ConicalGearOptimizationStrategyDatabase)

    @property
    def optimization_strategy_database(
        self: "CastSelf",
    ) -> "_2453.OptimizationStrategyDatabase":
        from mastapy._private.system_model.optimization import _2453

        return self.__parent__._cast(_2453.OptimizationStrategyDatabase)

    @property
    def cylindrical_gear_flank_optimisation_parameters_database(
        self: "CastSelf",
    ) -> "_2461.CylindricalGearFlankOptimisationParametersDatabase":
        from mastapy._private.system_model.optimization.machine_learning import _2461

        return self.__parent__._cast(
            _2461.CylindricalGearFlankOptimisationParametersDatabase
        )

    @property
    def supercharger_rotor_set_database(
        self: "CastSelf",
    ) -> "_2807.SuperchargerRotorSetDatabase":
        from mastapy._private.system_model.part_model.gears.supercharger_rotor_set import (
            _2807,
        )

        return self.__parent__._cast(_2807.SuperchargerRotorSetDatabase)

    @property
    def sql_database(self: "CastSelf") -> "SQLDatabase":
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
class SQLDatabase(_2028.Database[TKey, TValue]):
    """SQLDatabase

    This is a mastapy class.

    Generic Types:
        TKey
        TValue
    """

    TYPE: ClassVar["Type"] = _SQL_DATABASE

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def allow_network_database(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AllowNetworkDatabase")

        if temp is None:
            return False

        return temp

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
    def uses_database(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "UsesDatabase")

        if temp is None:
            return False

        return temp

    @exception_bridge
    @enforce_parameter_types
    def delete(self: "Self", key: "TKey") -> None:
        """Method does not return.

        Args:
            key (TKey)
        """
        pythonnet_method_call(self.wrapped, "Delete", key)

    @exception_bridge
    @enforce_parameter_types
    def reload(
        self: "Self",
        task_progress: "_7906.TaskProgress",
        reload_protobuf: "bool" = False,
    ) -> None:
        """Method does not return.

        Args:
            task_progress (mastapy.TaskProgress)
            reload_protobuf (bool, optional)
        """
        reload_protobuf = bool(reload_protobuf)
        pythonnet_method_call(
            self.wrapped,
            "Reload",
            task_progress.wrapped if task_progress else None,
            reload_protobuf if reload_protobuf else False,
        )

    @exception_bridge
    @enforce_parameter_types
    def save(self: "Self", item: "TValue") -> None:
        """Method does not return.

        Args:
            item (TValue)
        """
        pythonnet_method_call(self.wrapped, "Save", item)

    @property
    def cast_to(self: "Self") -> "_Cast_SQLDatabase":
        """Cast to another type.

        Returns:
            _Cast_SQLDatabase
        """
        return _Cast_SQLDatabase(self)
