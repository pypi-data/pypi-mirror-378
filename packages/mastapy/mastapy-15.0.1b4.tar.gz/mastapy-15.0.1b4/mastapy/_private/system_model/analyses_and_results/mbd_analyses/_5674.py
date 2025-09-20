"""BearingMultibodyDynamicsAnalysis"""

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
from mastapy._private._math.vector_3d import Vector3D
from mastapy._private.system_model.analyses_and_results.mbd_analyses import _5704

_BEARING_MULTIBODY_DYNAMICS_ANALYSIS = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.MBDAnalyses",
    "BearingMultibodyDynamicsAnalysis",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.system_model.analyses_and_results import _2897, _2899, _2903
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7892,
        _7896,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
        _5693,
        _5755,
        _5758,
    )
    from mastapy._private.system_model.analyses_and_results.mbd_analyses.reporting import (
        _5817,
    )
    from mastapy._private.system_model.analyses_and_results.static_loads import _7693
    from mastapy._private.system_model.part_model import _2669

    Self = TypeVar("Self", bound="BearingMultibodyDynamicsAnalysis")
    CastSelf = TypeVar(
        "CastSelf",
        bound="BearingMultibodyDynamicsAnalysis._Cast_BearingMultibodyDynamicsAnalysis",
    )


__docformat__ = "restructuredtext en"
__all__ = ("BearingMultibodyDynamicsAnalysis",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BearingMultibodyDynamicsAnalysis:
    """Special nested class for casting BearingMultibodyDynamicsAnalysis to subclasses."""

    __parent__: "BearingMultibodyDynamicsAnalysis"

    @property
    def connector_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5704.ConnectorMultibodyDynamicsAnalysis":
        return self.__parent__._cast(_5704.ConnectorMultibodyDynamicsAnalysis)

    @property
    def mountable_component_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5755.MountableComponentMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5755,
        )

        return self.__parent__._cast(_5755.MountableComponentMultibodyDynamicsAnalysis)

    @property
    def component_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5693.ComponentMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5693,
        )

        return self.__parent__._cast(_5693.ComponentMultibodyDynamicsAnalysis)

    @property
    def part_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "_5758.PartMultibodyDynamicsAnalysis":
        from mastapy._private.system_model.analyses_and_results.mbd_analyses import (
            _5758,
        )

        return self.__parent__._cast(_5758.PartMultibodyDynamicsAnalysis)

    @property
    def part_time_series_load_analysis_case(
        self: "CastSelf",
    ) -> "_7896.PartTimeSeriesLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7896,
        )

        return self.__parent__._cast(_7896.PartTimeSeriesLoadAnalysisCase)

    @property
    def part_analysis_case(self: "CastSelf") -> "_7892.PartAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7892,
        )

        return self.__parent__._cast(_7892.PartAnalysisCase)

    @property
    def part_analysis(self: "CastSelf") -> "_2903.PartAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2903

        return self.__parent__._cast(_2903.PartAnalysis)

    @property
    def design_entity_single_context_analysis(
        self: "CastSelf",
    ) -> "_2899.DesignEntitySingleContextAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2899

        return self.__parent__._cast(_2899.DesignEntitySingleContextAnalysis)

    @property
    def design_entity_analysis(self: "CastSelf") -> "_2897.DesignEntityAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2897

        return self.__parent__._cast(_2897.DesignEntityAnalysis)

    @property
    def bearing_multibody_dynamics_analysis(
        self: "CastSelf",
    ) -> "BearingMultibodyDynamicsAnalysis":
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
class BearingMultibodyDynamicsAnalysis(_5704.ConnectorMultibodyDynamicsAnalysis):
    """BearingMultibodyDynamicsAnalysis

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEARING_MULTIBODY_DYNAMICS_ANALYSIS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def ansiabma_adjusted_rating_life_damage_rate(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ANSIABMAAdjustedRatingLifeDamageRate"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def ansiabma_adjusted_rating_life_damage_rate_during_analysis(
        self: "Self",
    ) -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ANSIABMAAdjustedRatingLifeDamageRateDuringAnalysis"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def ansiabma_basic_rating_life_damage_rate(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ANSIABMABasicRatingLifeDamageRate")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def ansiabma_basic_rating_life_damage_rate_during_analysis(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ANSIABMABasicRatingLifeDamageRateDuringAnalysis"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def ansiabma_static_safety_factor(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ANSIABMAStaticSafetyFactor")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def ansiabma_static_safety_factor_at_current_time(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ANSIABMAStaticSafetyFactorAtCurrentTime"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def drag_torque(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "DragTorque")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def element_orbital_position(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElementOrbitalPosition")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def element_orbital_velocity(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElementOrbitalVelocity")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def element_passing_frequency(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElementPassingFrequency")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def force(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Force")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def force_angular(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ForceAngular")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def iso162812025_basic_reference_rating_life_damage_during_analysis(
        self: "Self",
    ) -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ISO162812025BasicReferenceRatingLifeDamageDuringAnalysis"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def iso162812025_basic_reference_rating_life_damage_rate(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ISO162812025BasicReferenceRatingLifeDamageRate"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def iso162812025_modified_reference_rating_life_damage_during_analysis(
        self: "Self",
    ) -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ISO162812025ModifiedReferenceRatingLifeDamageDuringAnalysis"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def iso162812025_modified_reference_rating_life_damage_rate(
        self: "Self",
    ) -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ISO162812025ModifiedReferenceRatingLifeDamageRate"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def iso2812007_basic_rating_life_damage_during_analysis(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ISO2812007BasicRatingLifeDamageDuringAnalysis"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def iso2812007_basic_rating_life_damage_rate(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ISO2812007BasicRatingLifeDamageRate"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def iso2812007_modified_rating_life_damage_during_analysis(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ISO2812007ModifiedRatingLifeDamageDuringAnalysis"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def iso2812007_modified_rating_life_damage_rate(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ISO2812007ModifiedRatingLifeDamageRate"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def iso762006_safety_factor(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ISO762006SafetyFactor")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def iso762006_safety_factor_at_current_time(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ISO762006SafetyFactorAtCurrentTime"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_element_normal_stress_inner(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MaximumElementNormalStressInner")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_element_normal_stress_inner_at_current_time(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "MaximumElementNormalStressInnerAtCurrentTime"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_element_normal_stress_outer(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MaximumElementNormalStressOuter")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_element_normal_stress_outer_at_current_time(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "MaximumElementNormalStressOuterAtCurrentTime"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_static_contact_stress_inner_safety_factor(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "MaximumStaticContactStressInnerSafetyFactor"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_static_contact_stress_inner_safety_factor_at_current_time(
        self: "Self",
    ) -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "MaximumStaticContactStressInnerSafetyFactorAtCurrentTime"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_static_contact_stress_outer_safety_factor(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "MaximumStaticContactStressOuterSafetyFactor"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_static_contact_stress_outer_safety_factor_at_current_time(
        self: "Self",
    ) -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "MaximumStaticContactStressOuterSafetyFactorAtCurrentTime"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_time_step(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MaximumTimeStep")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def power_loss(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerLoss")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def relative_acceleration(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RelativeAcceleration")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def relative_displacement(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RelativeDisplacement")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def relative_tilt(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RelativeTilt")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def relative_velocity(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RelativeVelocity")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_design(self: "Self") -> "_2669.Bearing":
        """mastapy.system_model.part_model.Bearing

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDesign")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def component_load_case(self: "Self") -> "_7693.BearingLoadCase":
        """mastapy.system_model.analyses_and_results.static_loads.BearingLoadCase

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentLoadCase")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def peak_dynamic_force(self: "Self") -> "_5817.DynamicForceVector3DResult":
        """mastapy.system_model.analyses_and_results.mbd_analyses.reporting.DynamicForceVector3DResult

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PeakDynamicForce")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def planetaries(self: "Self") -> "List[BearingMultibodyDynamicsAnalysis]":
        """List[mastapy.system_model.analyses_and_results.mbd_analyses.BearingMultibodyDynamicsAnalysis]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "Planetaries")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_BearingMultibodyDynamicsAnalysis":
        """Cast to another type.

        Returns:
            _Cast_BearingMultibodyDynamicsAnalysis
        """
        return _Cast_BearingMultibodyDynamicsAnalysis(self)
