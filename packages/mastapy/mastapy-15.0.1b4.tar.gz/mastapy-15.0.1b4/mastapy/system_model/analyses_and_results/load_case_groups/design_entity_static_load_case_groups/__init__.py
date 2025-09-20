"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5967 import (
        AbstractAssemblyStaticLoadCaseGroup,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5968 import (
        ComponentStaticLoadCaseGroup,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5969 import (
        ConnectionStaticLoadCaseGroup,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5970 import (
        DesignEntityStaticLoadCaseGroup,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5971 import (
        GearSetStaticLoadCaseGroup,
    )
    from mastapy._private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5972 import (
        PartStaticLoadCaseGroup,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5967": [
            "AbstractAssemblyStaticLoadCaseGroup"
        ],
        "_private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5968": [
            "ComponentStaticLoadCaseGroup"
        ],
        "_private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5969": [
            "ConnectionStaticLoadCaseGroup"
        ],
        "_private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5970": [
            "DesignEntityStaticLoadCaseGroup"
        ],
        "_private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5971": [
            "GearSetStaticLoadCaseGroup"
        ],
        "_private.system_model.analyses_and_results.load_case_groups.design_entity_static_load_case_groups._5972": [
            "PartStaticLoadCaseGroup"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractAssemblyStaticLoadCaseGroup",
    "ComponentStaticLoadCaseGroup",
    "ConnectionStaticLoadCaseGroup",
    "DesignEntityStaticLoadCaseGroup",
    "GearSetStaticLoadCaseGroup",
    "PartStaticLoadCaseGroup",
)
