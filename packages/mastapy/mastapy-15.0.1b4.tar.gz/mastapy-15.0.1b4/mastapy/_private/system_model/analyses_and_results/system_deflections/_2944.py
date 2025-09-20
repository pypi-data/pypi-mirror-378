"""BearingSystemDeflection"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import constructor, conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
    pythonnet_property_get,
)
from mastapy._private._math.vector_2d import Vector2D
from mastapy._private._math.vector_3d import Vector3D
from mastapy._private.system_model.analyses_and_results.system_deflections import _2974

_BEARING_SYSTEM_DEFLECTION = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "BearingSystemDeflection",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.bearings.bearing_results import _2152, _2160
    from mastapy._private.math_utility.measured_vectors import _1750
    from mastapy._private.system_model.analyses_and_results import _2897, _2899, _2903
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7892,
        _7894,
        _7895,
    )
    from mastapy._private.system_model.analyses_and_results.power_flows import _4306
    from mastapy._private.system_model.analyses_and_results.static_loads import _7693
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2961,
        _3030,
        _3033,
    )
    from mastapy._private.system_model.part_model import _2669, _2671
    from mastapy._private.utility_gui.charts import _2075

    Self = TypeVar("Self", bound="BearingSystemDeflection")
    CastSelf = TypeVar(
        "CastSelf", bound="BearingSystemDeflection._Cast_BearingSystemDeflection"
    )


__docformat__ = "restructuredtext en"
__all__ = ("BearingSystemDeflection",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_BearingSystemDeflection:
    """Special nested class for casting BearingSystemDeflection to subclasses."""

    __parent__: "BearingSystemDeflection"

    @property
    def connector_system_deflection(
        self: "CastSelf",
    ) -> "_2974.ConnectorSystemDeflection":
        return self.__parent__._cast(_2974.ConnectorSystemDeflection)

    @property
    def mountable_component_system_deflection(
        self: "CastSelf",
    ) -> "_3030.MountableComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3030,
        )

        return self.__parent__._cast(_3030.MountableComponentSystemDeflection)

    @property
    def component_system_deflection(
        self: "CastSelf",
    ) -> "_2961.ComponentSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2961,
        )

        return self.__parent__._cast(_2961.ComponentSystemDeflection)

    @property
    def part_system_deflection(self: "CastSelf") -> "_3033.PartSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3033,
        )

        return self.__parent__._cast(_3033.PartSystemDeflection)

    @property
    def part_fe_analysis(self: "CastSelf") -> "_7894.PartFEAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7894,
        )

        return self.__parent__._cast(_7894.PartFEAnalysis)

    @property
    def part_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7895.PartStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7895,
        )

        return self.__parent__._cast(_7895.PartStaticLoadAnalysisCase)

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
    def bearing_system_deflection(self: "CastSelf") -> "BearingSystemDeflection":
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
class BearingSystemDeflection(_2974.ConnectorSystemDeflection):
    """BearingSystemDeflection

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _BEARING_SYSTEM_DEFLECTION

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def axial_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "AxialStiffness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def component_angular_displacements(self: "Self") -> "List[Vector2D]":
        """List[Vector2D]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAngularDisplacements")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, Vector2D)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_axial_displacements(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentAxialDisplacements")

        if temp is None:
            return None

        value = conversion.to_list_any(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def component_radial_displacements(self: "Self") -> "List[Vector2D]":
        """List[Vector2D]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentRadialDisplacements")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp, Vector2D)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def element_axial_displacements(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElementAxialDisplacements")

        if temp is None:
            return None

        value = conversion.to_list_any(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def element_radial_displacements(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElementRadialDisplacements")

        if temp is None:
            return None

        value = conversion.to_list_any(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def element_tilts(self: "Self") -> "List[float]":
        """List[float]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElementTilts")

        if temp is None:
            return None

        value = conversion.to_list_any(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def elements_in_contact(self: "Self") -> "int":
        """int

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ElementsInContact")

        if temp is None:
            return 0

        return temp

    @property
    @exception_bridge
    def have_all_elements_converged(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "HaveAllElementsConverged")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def inner_left_mounting_axial_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerLeftMountingAxialStiffness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def inner_left_mounting_displacement(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerLeftMountingDisplacement")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def inner_left_mounting_maximum_tilt_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "InnerLeftMountingMaximumTiltStiffness"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def inner_left_mounting_tilt(self: "Self") -> "Vector2D":
        """Vector2D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerLeftMountingTilt")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector2d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def inner_radial_mounting_linear_displacement(self: "Self") -> "Vector2D":
        """Vector2D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "InnerRadialMountingLinearDisplacement"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector2d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def inner_radial_mounting_maximum_tilt_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "InnerRadialMountingMaximumTiltStiffness"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def inner_radial_mounting_tilt(self: "Self") -> "Vector2D":
        """Vector2D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerRadialMountingTilt")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector2d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def inner_right_mounting_axial_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerRightMountingAxialStiffness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def inner_right_mounting_displacement(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerRightMountingDisplacement")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def inner_right_mounting_maximum_tilt_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "InnerRightMountingMaximumTiltStiffness"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def inner_right_mounting_tilt(self: "Self") -> "Vector2D":
        """Vector2D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerRightMountingTilt")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector2d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def internal_force(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InternalForce")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def internal_moment(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InternalMoment")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def is_axially_loaded(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsAxiallyLoaded")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def is_loaded(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsLoaded")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def is_radially_loaded(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsRadiallyLoaded")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def is_tilt_loaded(self: "Self") -> "bool":
        """bool

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "IsTiltLoaded")

        if temp is None:
            return False

        return temp

    @property
    @exception_bridge
    def maximum_radial_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MaximumRadialStiffness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def maximum_tilt_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "MaximumTiltStiffness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def outer_left_mounting_axial_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterLeftMountingAxialStiffness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def outer_left_mounting_displacement(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterLeftMountingDisplacement")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def outer_left_mounting_maximum_tilt_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "OuterLeftMountingMaximumTiltStiffness"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def outer_left_mounting_tilt(self: "Self") -> "Vector2D":
        """Vector2D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterLeftMountingTilt")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector2d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def outer_radial_mounting_linear_displacement(self: "Self") -> "Vector2D":
        """Vector2D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "OuterRadialMountingLinearDisplacement"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector2d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def outer_radial_mounting_maximum_tilt_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "OuterRadialMountingMaximumTiltStiffness"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def outer_radial_mounting_tilt(self: "Self") -> "Vector2D":
        """Vector2D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterRadialMountingTilt")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector2d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def outer_right_mounting_axial_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterRightMountingAxialStiffness")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def outer_right_mounting_displacement(self: "Self") -> "Vector3D":
        """Vector3D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterRightMountingDisplacement")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector3d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def outer_right_mounting_maximum_tilt_stiffness(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "OuterRightMountingMaximumTiltStiffness"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def outer_right_mounting_tilt(self: "Self") -> "Vector2D":
        """Vector2D

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterRightMountingTilt")

        if temp is None:
            return None

        value = conversion.pn_to_mp_vector2d(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def percentage_preload_spring_compression(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "PercentagePreloadSpringCompression"
        )

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def preload_spring_compression(self: "Self") -> "float":
        """float

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PreloadSpringCompression")

        if temp is None:
            return 0.0

        return temp

    @property
    @exception_bridge
    def spring_preload_chart(self: "Self") -> "_2075.TwoDChartDefinition":
        """mastapy.utility_gui.charts.TwoDChartDefinition

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "SpringPreloadChart")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

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
    def component_detailed_analysis(self: "Self") -> "_2160.LoadedBearingResults":
        """mastapy.bearings.bearing_results.LoadedBearingResults

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "ComponentDetailedAnalysis")

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
    def inner_left_mounting_stiffness(
        self: "Self",
    ) -> "_2152.BearingStiffnessMatrixReporter":
        """mastapy.bearings.bearing_results.BearingStiffnessMatrixReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerLeftMountingStiffness")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def inner_radial_mounting_stiffness(
        self: "Self",
    ) -> "_2152.BearingStiffnessMatrixReporter":
        """mastapy.bearings.bearing_results.BearingStiffnessMatrixReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerRadialMountingStiffness")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def inner_right_mounting_stiffness(
        self: "Self",
    ) -> "_2152.BearingStiffnessMatrixReporter":
        """mastapy.bearings.bearing_results.BearingStiffnessMatrixReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "InnerRightMountingStiffness")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def outer_left_mounting_stiffness(
        self: "Self",
    ) -> "_2152.BearingStiffnessMatrixReporter":
        """mastapy.bearings.bearing_results.BearingStiffnessMatrixReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterLeftMountingStiffness")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def outer_radial_mounting_stiffness(
        self: "Self",
    ) -> "_2152.BearingStiffnessMatrixReporter":
        """mastapy.bearings.bearing_results.BearingStiffnessMatrixReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterRadialMountingStiffness")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def outer_right_mounting_stiffness(
        self: "Self",
    ) -> "_2152.BearingStiffnessMatrixReporter":
        """mastapy.bearings.bearing_results.BearingStiffnessMatrixReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "OuterRightMountingStiffness")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def power_flow_results(self: "Self") -> "_4306.BearingPowerFlow":
        """mastapy.system_model.analyses_and_results.power_flows.BearingPowerFlow

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PowerFlowResults")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def preload_spring_stiffness(
        self: "Self",
    ) -> "_2152.BearingStiffnessMatrixReporter":
        """mastapy.bearings.bearing_results.BearingStiffnessMatrixReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "PreloadSpringStiffness")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def stiffness_between_rings(self: "Self") -> "_2152.BearingStiffnessMatrixReporter":
        """mastapy.bearings.bearing_results.BearingStiffnessMatrixReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StiffnessBetweenRings")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def stiffness_matrix(self: "Self") -> "_2152.BearingStiffnessMatrixReporter":
        """mastapy.bearings.bearing_results.BearingStiffnessMatrixReporter

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StiffnessMatrix")

        if temp is None:
            return None

        type_ = temp.GetType()
        return constructor.new(type_.Namespace, type_.Name)(temp)

    @property
    @exception_bridge
    def forces_at_zero_displacement_for_inner_and_outer_nodes(
        self: "Self",
    ) -> "List[_1750.ForceResults]":
        """List[mastapy.math_utility.measured_vectors.ForceResults]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(
            self.wrapped, "ForcesAtZeroDisplacementForInnerAndOuterNodes"
        )

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def planetaries(self: "Self") -> "List[BearingSystemDeflection]":
        """List[mastapy.system_model.analyses_and_results.system_deflections.BearingSystemDeflection]

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
    @exception_bridge
    def race_mounting_options_for_analysis(
        self: "Self",
    ) -> "List[_2671.BearingRaceMountingOptions]":
        """List[mastapy.system_model.part_model.BearingRaceMountingOptions]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "RaceMountingOptionsForAnalysis")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    @exception_bridge
    def stiffness_between_each_ring(
        self: "Self",
    ) -> "List[_2152.BearingStiffnessMatrixReporter]":
        """List[mastapy.bearings.bearing_results.BearingStiffnessMatrixReporter]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "StiffnessBetweenEachRing")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @exception_bridge
    def continue_dynamic_analysis(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "ContinueDynamicAnalysis")

    @exception_bridge
    def dynamic_analysis(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "DynamicAnalysis")

    @property
    def cast_to(self: "Self") -> "_Cast_BearingSystemDeflection":
        """Cast to another type.

        Returns:
            _Cast_BearingSystemDeflection
        """
        return _Cast_BearingSystemDeflection(self)
