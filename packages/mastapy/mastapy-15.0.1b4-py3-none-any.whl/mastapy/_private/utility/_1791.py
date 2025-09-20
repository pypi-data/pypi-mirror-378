"""PerMachineSettings"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from mastapy._private._internal import utility
from mastapy._private._internal.dataclasses import extended_dataclass
from mastapy._private._internal.exception_bridge import exception_bridge
from mastapy._private._internal.exceptions import CastException
from mastapy._private._internal.python_net import (
    python_net_import,
    pythonnet_method_call,
)
from mastapy._private.utility import _1792

_PER_MACHINE_SETTINGS = python_net_import("SMT.MastaAPI.Utility", "PerMachineSettings")

if TYPE_CHECKING:
    from typing import Any, Type, TypeVar

    from mastapy._private.bearings import _2107
    from mastapy._private.gears.gear_designs.cylindrical import _1121
    from mastapy._private.gears.materials import _691
    from mastapy._private.nodal_analysis import _71
    from mastapy._private.nodal_analysis.geometry_modeller_link import _239
    from mastapy._private.system_model.part_model import _2680, _2706
    from mastapy._private.utility import _1793
    from mastapy._private.utility.cad_export import _2039
    from mastapy._private.utility.databases import _2031
    from mastapy._private.utility.scripting import _1939
    from mastapy._private.utility.units_and_measurements import _1803

    Self = TypeVar("Self", bound="PerMachineSettings")
    CastSelf = TypeVar("CastSelf", bound="PerMachineSettings._Cast_PerMachineSettings")


__docformat__ = "restructuredtext en"
__all__ = ("PerMachineSettings",)


@extended_dataclass(frozen=True, slots=True, weakref_slot=True)
class _Cast_PerMachineSettings:
    """Special nested class for casting PerMachineSettings to subclasses."""

    __parent__: "PerMachineSettings"

    @property
    def persistent_singleton(self: "CastSelf") -> "_1792.PersistentSingleton":
        return self.__parent__._cast(_1792.PersistentSingleton)

    @property
    def fe_user_settings(self: "CastSelf") -> "_71.FEUserSettings":
        from mastapy._private.nodal_analysis import _71

        return self.__parent__._cast(_71.FEUserSettings)

    @property
    def geometry_modeller_settings(self: "CastSelf") -> "_239.GeometryModellerSettings":
        from mastapy._private.nodal_analysis.geometry_modeller_link import _239

        return self.__parent__._cast(_239.GeometryModellerSettings)

    @property
    def gear_material_expert_system_factor_settings(
        self: "CastSelf",
    ) -> "_691.GearMaterialExpertSystemFactorSettings":
        from mastapy._private.gears.materials import _691

        return self.__parent__._cast(_691.GearMaterialExpertSystemFactorSettings)

    @property
    def cylindrical_gear_defaults(self: "CastSelf") -> "_1121.CylindricalGearDefaults":
        from mastapy._private.gears.gear_designs.cylindrical import _1121

        return self.__parent__._cast(_1121.CylindricalGearDefaults)

    @property
    def program_settings(self: "CastSelf") -> "_1793.ProgramSettings":
        from mastapy._private.utility import _1793

        return self.__parent__._cast(_1793.ProgramSettings)

    @property
    def measurement_settings(self: "CastSelf") -> "_1803.MeasurementSettings":
        from mastapy._private.utility.units_and_measurements import _1803

        return self.__parent__._cast(_1803.MeasurementSettings)

    @property
    def scripting_setup(self: "CastSelf") -> "_1939.ScriptingSetup":
        from mastapy._private.utility.scripting import _1939

        return self.__parent__._cast(_1939.ScriptingSetup)

    @property
    def database_settings(self: "CastSelf") -> "_2031.DatabaseSettings":
        from mastapy._private.utility.databases import _2031

        return self.__parent__._cast(_2031.DatabaseSettings)

    @property
    def cad_export_settings(self: "CastSelf") -> "_2039.CADExportSettings":
        from mastapy._private.utility.cad_export import _2039

        return self.__parent__._cast(_2039.CADExportSettings)

    @property
    def skf_settings(self: "CastSelf") -> "_2107.SKFSettings":
        from mastapy._private.bearings import _2107

        return self.__parent__._cast(_2107.SKFSettings)

    @property
    def default_export_settings(self: "CastSelf") -> "_2680.DefaultExportSettings":
        from mastapy._private.system_model.part_model import _2680

        return self.__parent__._cast(_2680.DefaultExportSettings)

    @property
    def planet_carrier_settings(self: "CastSelf") -> "_2706.PlanetCarrierSettings":
        from mastapy._private.system_model.part_model import _2706

        return self.__parent__._cast(_2706.PlanetCarrierSettings)

    @property
    def per_machine_settings(self: "CastSelf") -> "PerMachineSettings":
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
class PerMachineSettings(_1792.PersistentSingleton):
    """PerMachineSettings

    This is a mastapy class.
    """

    TYPE: ClassVar["Type"] = _PER_MACHINE_SETTINGS

    wrapped: "Any"

    def __post_init__(self: "Self") -> None:
        """Override of the post initialisation magic method."""
        if not hasattr(self.wrapped, "reference_count"):
            self.wrapped.reference_count = 0

        self.wrapped.reference_count += 1

    @exception_bridge
    def reset_to_defaults(self: "Self") -> None:
        """Method does not return."""
        pythonnet_method_call(self.wrapped, "ResetToDefaults")

    @property
    def cast_to(self: "Self") -> "_Cast_PerMachineSettings":
        """Cast to another type.

        Returns:
            _Cast_PerMachineSettings
        """
        return _Cast_PerMachineSettings(self)
