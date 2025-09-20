"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model._2416 import Design
    from mastapy._private.system_model._2417 import ComponentDampingOption
    from mastapy._private.system_model._2418 import (
        ConceptCouplingSpeedRatioSpecificationMethod,
    )
    from mastapy._private.system_model._2419 import DesignEntity
    from mastapy._private.system_model._2420 import DesignEntityId
    from mastapy._private.system_model._2421 import DesignSettings
    from mastapy._private.system_model._2422 import DutyCycleImporter
    from mastapy._private.system_model._2423 import DutyCycleImporterDesignEntityMatch
    from mastapy._private.system_model._2424 import ExternalFullFELoader
    from mastapy._private.system_model._2425 import HypoidWindUpRemovalMethod
    from mastapy._private.system_model._2426 import IncludeDutyCycleOption
    from mastapy._private.system_model._2427 import MAAElectricMachineGroup
    from mastapy._private.system_model._2428 import MASTASettings
    from mastapy._private.system_model._2429 import MemorySummary
    from mastapy._private.system_model._2430 import MeshStiffnessModel
    from mastapy._private.system_model._2431 import (
        PlanetPinManufacturingErrorsCoordinateSystem,
    )
    from mastapy._private.system_model._2432 import (
        PowerLoadDragTorqueSpecificationMethod,
    )
    from mastapy._private.system_model._2433 import (
        PowerLoadInputTorqueSpecificationMethod,
    )
    from mastapy._private.system_model._2434 import PowerLoadPIDControlSpeedInputType
    from mastapy._private.system_model._2435 import PowerLoadType
    from mastapy._private.system_model._2436 import RelativeComponentAlignment
    from mastapy._private.system_model._2437 import RelativeOffsetOption
    from mastapy._private.system_model._2438 import SystemReporting
    from mastapy._private.system_model._2439 import (
        ThermalExpansionOptionForGroundedNodes,
    )
    from mastapy._private.system_model._2440 import TransmissionTemperatureSet
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model._2416": ["Design"],
        "_private.system_model._2417": ["ComponentDampingOption"],
        "_private.system_model._2418": ["ConceptCouplingSpeedRatioSpecificationMethod"],
        "_private.system_model._2419": ["DesignEntity"],
        "_private.system_model._2420": ["DesignEntityId"],
        "_private.system_model._2421": ["DesignSettings"],
        "_private.system_model._2422": ["DutyCycleImporter"],
        "_private.system_model._2423": ["DutyCycleImporterDesignEntityMatch"],
        "_private.system_model._2424": ["ExternalFullFELoader"],
        "_private.system_model._2425": ["HypoidWindUpRemovalMethod"],
        "_private.system_model._2426": ["IncludeDutyCycleOption"],
        "_private.system_model._2427": ["MAAElectricMachineGroup"],
        "_private.system_model._2428": ["MASTASettings"],
        "_private.system_model._2429": ["MemorySummary"],
        "_private.system_model._2430": ["MeshStiffnessModel"],
        "_private.system_model._2431": ["PlanetPinManufacturingErrorsCoordinateSystem"],
        "_private.system_model._2432": ["PowerLoadDragTorqueSpecificationMethod"],
        "_private.system_model._2433": ["PowerLoadInputTorqueSpecificationMethod"],
        "_private.system_model._2434": ["PowerLoadPIDControlSpeedInputType"],
        "_private.system_model._2435": ["PowerLoadType"],
        "_private.system_model._2436": ["RelativeComponentAlignment"],
        "_private.system_model._2437": ["RelativeOffsetOption"],
        "_private.system_model._2438": ["SystemReporting"],
        "_private.system_model._2439": ["ThermalExpansionOptionForGroundedNodes"],
        "_private.system_model._2440": ["TransmissionTemperatureSet"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "Design",
    "ComponentDampingOption",
    "ConceptCouplingSpeedRatioSpecificationMethod",
    "DesignEntity",
    "DesignEntityId",
    "DesignSettings",
    "DutyCycleImporter",
    "DutyCycleImporterDesignEntityMatch",
    "ExternalFullFELoader",
    "HypoidWindUpRemovalMethod",
    "IncludeDutyCycleOption",
    "MAAElectricMachineGroup",
    "MASTASettings",
    "MemorySummary",
    "MeshStiffnessModel",
    "PlanetPinManufacturingErrorsCoordinateSystem",
    "PowerLoadDragTorqueSpecificationMethod",
    "PowerLoadInputTorqueSpecificationMethod",
    "PowerLoadPIDControlSpeedInputType",
    "PowerLoadType",
    "RelativeComponentAlignment",
    "RelativeOffsetOption",
    "SystemReporting",
    "ThermalExpansionOptionForGroundedNodes",
    "TransmissionTemperatureSet",
)
