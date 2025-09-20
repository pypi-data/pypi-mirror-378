"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.part_model.configurations._2862 import (
        ActiveFESubstructureSelection,
    )
    from mastapy._private.system_model.part_model.configurations._2863 import (
        ActiveFESubstructureSelectionGroup,
    )
    from mastapy._private.system_model.part_model.configurations._2864 import (
        ActiveShaftDesignSelection,
    )
    from mastapy._private.system_model.part_model.configurations._2865 import (
        ActiveShaftDesignSelectionGroup,
    )
    from mastapy._private.system_model.part_model.configurations._2866 import (
        BearingDetailConfiguration,
    )
    from mastapy._private.system_model.part_model.configurations._2867 import (
        BearingDetailSelection,
    )
    from mastapy._private.system_model.part_model.configurations._2868 import (
        DesignConfiguration,
    )
    from mastapy._private.system_model.part_model.configurations._2869 import (
        PartDetailConfiguration,
    )
    from mastapy._private.system_model.part_model.configurations._2870 import (
        PartDetailSelection,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.part_model.configurations._2862": [
            "ActiveFESubstructureSelection"
        ],
        "_private.system_model.part_model.configurations._2863": [
            "ActiveFESubstructureSelectionGroup"
        ],
        "_private.system_model.part_model.configurations._2864": [
            "ActiveShaftDesignSelection"
        ],
        "_private.system_model.part_model.configurations._2865": [
            "ActiveShaftDesignSelectionGroup"
        ],
        "_private.system_model.part_model.configurations._2866": [
            "BearingDetailConfiguration"
        ],
        "_private.system_model.part_model.configurations._2867": [
            "BearingDetailSelection"
        ],
        "_private.system_model.part_model.configurations._2868": [
            "DesignConfiguration"
        ],
        "_private.system_model.part_model.configurations._2869": [
            "PartDetailConfiguration"
        ],
        "_private.system_model.part_model.configurations._2870": [
            "PartDetailSelection"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ActiveFESubstructureSelection",
    "ActiveFESubstructureSelectionGroup",
    "ActiveShaftDesignSelection",
    "ActiveShaftDesignSelectionGroup",
    "BearingDetailConfiguration",
    "BearingDetailSelection",
    "DesignConfiguration",
    "PartDetailConfiguration",
    "PartDetailSelection",
)
