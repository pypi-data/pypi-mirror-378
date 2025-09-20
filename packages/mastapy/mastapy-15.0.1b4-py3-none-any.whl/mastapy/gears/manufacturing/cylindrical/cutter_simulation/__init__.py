"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._835 import (
        CutterSimulationCalc,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._836 import (
        CylindricalCutterSimulatableGear,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._837 import (
        CylindricalGearSpecification,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._838 import (
        CylindricalManufacturedRealGearInMesh,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._839 import (
        CylindricalManufacturedVirtualGearInMesh,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._840 import (
        FinishCutterSimulation,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._841 import (
        FinishStockPoint,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._842 import (
        FormWheelGrindingSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._843 import (
        GearCutterSimulation,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._844 import (
        HobSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._845 import (
        ManufacturingOperationConstraints,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._846 import (
        ManufacturingProcessControls,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._847 import (
        RackSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._848 import (
        RoughCutterSimulation,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._849 import (
        ShaperSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._850 import (
        ShavingSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._851 import (
        VirtualSimulationCalculator,
    )
    from mastapy._private.gears.manufacturing.cylindrical.cutter_simulation._852 import (
        WormGrinderSimulationCalculator,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.cylindrical.cutter_simulation._835": [
            "CutterSimulationCalc"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._836": [
            "CylindricalCutterSimulatableGear"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._837": [
            "CylindricalGearSpecification"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._838": [
            "CylindricalManufacturedRealGearInMesh"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._839": [
            "CylindricalManufacturedVirtualGearInMesh"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._840": [
            "FinishCutterSimulation"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._841": [
            "FinishStockPoint"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._842": [
            "FormWheelGrindingSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._843": [
            "GearCutterSimulation"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._844": [
            "HobSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._845": [
            "ManufacturingOperationConstraints"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._846": [
            "ManufacturingProcessControls"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._847": [
            "RackSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._848": [
            "RoughCutterSimulation"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._849": [
            "ShaperSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._850": [
            "ShavingSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._851": [
            "VirtualSimulationCalculator"
        ],
        "_private.gears.manufacturing.cylindrical.cutter_simulation._852": [
            "WormGrinderSimulationCalculator"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CutterSimulationCalc",
    "CylindricalCutterSimulatableGear",
    "CylindricalGearSpecification",
    "CylindricalManufacturedRealGearInMesh",
    "CylindricalManufacturedVirtualGearInMesh",
    "FinishCutterSimulation",
    "FinishStockPoint",
    "FormWheelGrindingSimulationCalculator",
    "GearCutterSimulation",
    "HobSimulationCalculator",
    "ManufacturingOperationConstraints",
    "ManufacturingProcessControls",
    "RackSimulationCalculator",
    "RoughCutterSimulation",
    "ShaperSimulationCalculator",
    "ShavingSimulationCalculator",
    "VirtualSimulationCalculator",
    "WormGrinderSimulationCalculator",
)
