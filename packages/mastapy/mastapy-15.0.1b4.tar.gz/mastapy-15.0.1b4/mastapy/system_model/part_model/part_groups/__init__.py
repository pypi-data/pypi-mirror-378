"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.part_groups._2726 import (
        ConcentricOrParallelPartGroup,
    )
    from mastapy._private.system_model.part_model.part_groups._2727 import (
        ConcentricPartGroup,
    )
    from mastapy._private.system_model.part_model.part_groups._2728 import (
        ConcentricPartGroupParallelToThis,
    )
    from mastapy._private.system_model.part_model.part_groups._2729 import (
        DesignMeasurements,
    )
    from mastapy._private.system_model.part_model.part_groups._2730 import (
        ParallelPartGroup,
    )
    from mastapy._private.system_model.part_model.part_groups._2731 import (
        ParallelPartGroupSelection,
    )
    from mastapy._private.system_model.part_model.part_groups._2732 import PartGroup
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.part_groups._2726": [
            "ConcentricOrParallelPartGroup"
        ],
        "_private.system_model.part_model.part_groups._2727": ["ConcentricPartGroup"],
        "_private.system_model.part_model.part_groups._2728": [
            "ConcentricPartGroupParallelToThis"
        ],
        "_private.system_model.part_model.part_groups._2729": ["DesignMeasurements"],
        "_private.system_model.part_model.part_groups._2730": ["ParallelPartGroup"],
        "_private.system_model.part_model.part_groups._2731": [
            "ParallelPartGroupSelection"
        ],
        "_private.system_model.part_model.part_groups._2732": ["PartGroup"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ConcentricOrParallelPartGroup",
    "ConcentricPartGroup",
    "ConcentricPartGroupParallelToThis",
    "DesignMeasurements",
    "ParallelPartGroup",
    "ParallelPartGroupSelection",
    "PartGroup",
)
