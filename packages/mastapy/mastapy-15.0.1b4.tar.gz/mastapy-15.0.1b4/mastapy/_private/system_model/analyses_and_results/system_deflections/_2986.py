"""CylindricalGearMeshSystemDeflectionTimestep"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import conversion, utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_property_get,
)
from mastapy._private.system_model.analyses_and_results.system_deflections import _2985

_CYLINDRICAL_GEAR_MESH_SYSTEM_DEFLECTION_TIMESTEP = python_net_import(
    "SMT.MastaAPI.SystemModel.AnalysesAndResults.SystemDeflections",
    "CylindricalGearMeshSystemDeflectionTimestep",
)

if TYPE_CHECKING:
    from typing import Any, List, Type, TypeVar

    from mastapy._private.gears.ltca.cylindrical import _961
    from mastapy._private.system_model.analyses_and_results import _2895, _2897, _2899
    from mastapy._private.system_model.analyses_and_results.analysis_cases import (
        _7885,
        _7887,
        _7888,
    )
    from mastapy._private.system_model.analyses_and_results.system_deflections import (
        _2973,
        _3005,
        _3013,
    )

    Self = TypeVar("Self", bound="CylindricalGearMeshSystemDeflectionTimestep")
    CastSelf = TypeVar(
        "CastSelf",
        bound="CylindricalGearMeshSystemDeflectionTimestep._Cast_CylindricalGearMeshSystemDeflectionTimestep",
    )


__docformat__ = "restructuredtext en"
__all__ = ("CylindricalGearMeshSystemDeflectionTimestep",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_CylindricalGearMeshSystemDeflectionTimestep:
    """Special nested class for casting CylindricalGearMeshSystemDeflectionTimestep to subclasses."""

    __parent__: "CylindricalGearMeshSystemDeflectionTimestep"

    @property
    def cylindrical_gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_2985.CylindricalGearMeshSystemDeflection":
        return self.__parent__._cast(_2985.CylindricalGearMeshSystemDeflection)

    @property
    def gear_mesh_system_deflection(
        self: "CastSelf",
    ) -> "_3005.GearMeshSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3005,
        )

        return self.__parent__._cast(_3005.GearMeshSystemDeflection)

    @property
    def inter_mountable_component_connection_system_deflection(
        self: "CastSelf",
    ) -> "_3013.InterMountableComponentConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _3013,
        )

        return self.__parent__._cast(
            _3013.InterMountableComponentConnectionSystemDeflection
        )

    @property
    def connection_system_deflection(
        self: "CastSelf",
    ) -> "_2973.ConnectionSystemDeflection":
        from mastapy._private.system_model.analyses_and_results.system_deflections import (
            _2973,
        )

        return self.__parent__._cast(_2973.ConnectionSystemDeflection)

    @property
    def connection_fe_analysis(self: "CastSelf") -> "_7887.ConnectionFEAnalysis":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7887,
        )

        return self.__parent__._cast(_7887.ConnectionFEAnalysis)

    @property
    def connection_static_load_analysis_case(
        self: "CastSelf",
    ) -> "_7888.ConnectionStaticLoadAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7888,
        )

        return self.__parent__._cast(_7888.ConnectionStaticLoadAnalysisCase)

    @property
    def connection_analysis_case(self: "CastSelf") -> "_7885.ConnectionAnalysisCase":
        from mastapy._private.system_model.analyses_and_results.analysis_cases import (
            _7885,
        )

        return self.__parent__._cast(_7885.ConnectionAnalysisCase)

    @property
    def connection_analysis(self: "CastSelf") -> "_2895.ConnectionAnalysis":
        from mastapy._private.system_model.analyses_and_results import _2895

        return self.__parent__._cast(_2895.ConnectionAnalysis)

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
    def cylindrical_gear_mesh_system_deflection_timestep(
        self: "CastSelf",
    ) -> "CylindricalGearMeshSystemDeflectionTimestep":
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
class CylindricalGearMeshSystemDeflectionTimestep(
    _2985.CylindricalGearMeshSystemDeflection
):
    """CylindricalGearMeshSystemDeflectionTimestep

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _CYLINDRICAL_GEAR_MESH_SYSTEM_DEFLECTION_TIMESTEP

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @property
    @exception_bridge
    def loaded_contact_lines(
        self: "Self",
    ) -> "List[_961.CylindricalGearMeshLoadedContactLine]":
        """List[mastapy.gears.ltca.cylindrical.CylindricalGearMeshLoadedContactLine]

        Note:
            This property is readonly.
        """
        temp = pythonnet_property_get(self.wrapped, "LoadedContactLines")

        if temp is None:
            return None

        value = conversion.pn_to_mp_objects_in_list(temp)

        if value is None:
            return None

        return value

    @property
    def cast_to(self: "Self") -> "_Cast_CylindricalGearMeshSystemDeflectionTimestep":
        """Cast to another type.

        Returns:
            _Cast_CylindricalGearMeshSystemDeflectionTimestep
        """
        return _Cast_CylindricalGearMeshSystemDeflectionTimestep(self)
