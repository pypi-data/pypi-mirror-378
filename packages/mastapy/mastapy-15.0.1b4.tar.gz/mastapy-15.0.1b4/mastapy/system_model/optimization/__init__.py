"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.optimization._2442 import (
        ConicalGearOptimisationStrategy,
    )
    from mastapy._private.system_model.optimization._2443 import (
        ConicalGearOptimizationStep,
    )
    from mastapy._private.system_model.optimization._2444 import (
        ConicalGearOptimizationStrategyDatabase,
    )
    from mastapy._private.system_model.optimization._2445 import (
        CylindricalGearOptimisationStrategy,
    )
    from mastapy._private.system_model.optimization._2446 import (
        CylindricalGearOptimizationStep,
    )
    from mastapy._private.system_model.optimization._2447 import (
        MeasuredAndFactorViewModel,
    )
    from mastapy._private.system_model.optimization._2448 import (
        MicroGeometryOptimisationTarget,
    )
    from mastapy._private.system_model.optimization._2449 import OptimizationParameter
    from mastapy._private.system_model.optimization._2450 import OptimizationStep
    from mastapy._private.system_model.optimization._2451 import OptimizationStrategy
    from mastapy._private.system_model.optimization._2452 import (
        OptimizationStrategyBase,
    )
    from mastapy._private.system_model.optimization._2453 import (
        OptimizationStrategyDatabase,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.optimization._2442": ["ConicalGearOptimisationStrategy"],
        "_private.system_model.optimization._2443": ["ConicalGearOptimizationStep"],
        "_private.system_model.optimization._2444": [
            "ConicalGearOptimizationStrategyDatabase"
        ],
        "_private.system_model.optimization._2445": [
            "CylindricalGearOptimisationStrategy"
        ],
        "_private.system_model.optimization._2446": ["CylindricalGearOptimizationStep"],
        "_private.system_model.optimization._2447": ["MeasuredAndFactorViewModel"],
        "_private.system_model.optimization._2448": ["MicroGeometryOptimisationTarget"],
        "_private.system_model.optimization._2449": ["OptimizationParameter"],
        "_private.system_model.optimization._2450": ["OptimizationStep"],
        "_private.system_model.optimization._2451": ["OptimizationStrategy"],
        "_private.system_model.optimization._2452": ["OptimizationStrategyBase"],
        "_private.system_model.optimization._2453": ["OptimizationStrategyDatabase"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConicalGearOptimisationStrategy",
    "ConicalGearOptimizationStep",
    "ConicalGearOptimizationStrategyDatabase",
    "CylindricalGearOptimisationStrategy",
    "CylindricalGearOptimizationStep",
    "MeasuredAndFactorViewModel",
    "MicroGeometryOptimisationTarget",
    "OptimizationParameter",
    "OptimizationStep",
    "OptimizationStrategy",
    "OptimizationStrategyBase",
    "OptimizationStrategyDatabase",
)
