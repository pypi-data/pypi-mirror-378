"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._746 import (
        CalculationError,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._747 import (
        ChartType,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._748 import (
        GearPointCalculationError,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._749 import (
        MicroGeometryDefinitionMethod,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._750 import (
        MicroGeometryDefinitionType,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._751 import (
        PlungeShaverCalculation,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._752 import (
        PlungeShaverCalculationInputs,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._753 import (
        PlungeShaverGeneration,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._754 import (
        PlungeShaverInputsAndMicroGeometry,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._755 import (
        PlungeShaverOutputs,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._756 import (
        PlungeShaverSettings,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._757 import (
        PointOfInterest,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._758 import (
        RealPlungeShaverOutputs,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._759 import (
        ShaverPointCalculationError,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._760 import (
        ShaverPointOfInterest,
    )
    from mastapy._private.gears.manufacturing.cylindrical.plunge_shaving._761 import (
        VirtualPlungeShaverOutputs,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.gears.manufacturing.cylindrical.plunge_shaving._746": [
            "CalculationError"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._747": ["ChartType"],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._748": [
            "GearPointCalculationError"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._749": [
            "MicroGeometryDefinitionMethod"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._750": [
            "MicroGeometryDefinitionType"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._751": [
            "PlungeShaverCalculation"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._752": [
            "PlungeShaverCalculationInputs"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._753": [
            "PlungeShaverGeneration"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._754": [
            "PlungeShaverInputsAndMicroGeometry"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._755": [
            "PlungeShaverOutputs"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._756": [
            "PlungeShaverSettings"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._757": [
            "PointOfInterest"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._758": [
            "RealPlungeShaverOutputs"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._759": [
            "ShaverPointCalculationError"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._760": [
            "ShaverPointOfInterest"
        ],
        "_private.gears.manufacturing.cylindrical.plunge_shaving._761": [
            "VirtualPlungeShaverOutputs"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CalculationError",
    "ChartType",
    "GearPointCalculationError",
    "MicroGeometryDefinitionMethod",
    "MicroGeometryDefinitionType",
    "PlungeShaverCalculation",
    "PlungeShaverCalculationInputs",
    "PlungeShaverGeneration",
    "PlungeShaverInputsAndMicroGeometry",
    "PlungeShaverOutputs",
    "PlungeShaverSettings",
    "PointOfInterest",
    "RealPlungeShaverOutputs",
    "ShaverPointCalculationError",
    "ShaverPointOfInterest",
    "VirtualPlungeShaverOutputs",
)
