"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.optimization.machine_learning._2459 import (
        CylindricalGearFlankOptimisationParameter,
    )
    from mastapy._private.system_model.optimization.machine_learning._2460 import (
        CylindricalGearFlankOptimisationParameters,
    )
    from mastapy._private.system_model.optimization.machine_learning._2461 import (
        CylindricalGearFlankOptimisationParametersDatabase,
    )
    from mastapy._private.system_model.optimization.machine_learning._2462 import (
        GearFlankParameterSelection,
    )
    from mastapy._private.system_model.optimization.machine_learning._2463 import (
        LoadCaseConstraint,
    )
    from mastapy._private.system_model.optimization.machine_learning._2464 import (
        LoadCaseSettings,
    )
    from mastapy._private.system_model.optimization.machine_learning._2465 import (
        LoadCaseTarget,
    )
    from mastapy._private.system_model.optimization.machine_learning._2466 import (
        ML1MicroGeometryOptimiser,
    )
    from mastapy._private.system_model.optimization.machine_learning._2467 import (
        ML1MicroGeometryOptimiserGroup,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.optimization.machine_learning._2459": [
            "CylindricalGearFlankOptimisationParameter"
        ],
        "_private.system_model.optimization.machine_learning._2460": [
            "CylindricalGearFlankOptimisationParameters"
        ],
        "_private.system_model.optimization.machine_learning._2461": [
            "CylindricalGearFlankOptimisationParametersDatabase"
        ],
        "_private.system_model.optimization.machine_learning._2462": [
            "GearFlankParameterSelection"
        ],
        "_private.system_model.optimization.machine_learning._2463": [
            "LoadCaseConstraint"
        ],
        "_private.system_model.optimization.machine_learning._2464": [
            "LoadCaseSettings"
        ],
        "_private.system_model.optimization.machine_learning._2465": ["LoadCaseTarget"],
        "_private.system_model.optimization.machine_learning._2466": [
            "ML1MicroGeometryOptimiser"
        ],
        "_private.system_model.optimization.machine_learning._2467": [
            "ML1MicroGeometryOptimiserGroup"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "CylindricalGearFlankOptimisationParameter",
    "CylindricalGearFlankOptimisationParameters",
    "CylindricalGearFlankOptimisationParametersDatabase",
    "GearFlankParameterSelection",
    "LoadCaseConstraint",
    "LoadCaseSettings",
    "LoadCaseTarget",
    "ML1MicroGeometryOptimiser",
    "ML1MicroGeometryOptimiserGroup",
)
