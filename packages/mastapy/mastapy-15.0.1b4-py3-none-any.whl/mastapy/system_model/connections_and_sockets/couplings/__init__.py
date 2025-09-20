"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.connections_and_sockets.couplings._2568 import (
        ClutchConnection,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2569 import (
        ClutchSocket,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2570 import (
        ConceptCouplingConnection,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2571 import (
        ConceptCouplingSocket,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2572 import (
        CouplingConnection,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2573 import (
        CouplingSocket,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2574 import (
        PartToPartShearCouplingConnection,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2575 import (
        PartToPartShearCouplingSocket,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2576 import (
        SpringDamperConnection,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2577 import (
        SpringDamperSocket,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2578 import (
        TorqueConverterConnection,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2579 import (
        TorqueConverterPumpSocket,
    )
    from mastapy._private.system_model.connections_and_sockets.couplings._2580 import (
        TorqueConverterTurbineSocket,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.connections_and_sockets.couplings._2568": [
            "ClutchConnection"
        ],
        "_private.system_model.connections_and_sockets.couplings._2569": [
            "ClutchSocket"
        ],
        "_private.system_model.connections_and_sockets.couplings._2570": [
            "ConceptCouplingConnection"
        ],
        "_private.system_model.connections_and_sockets.couplings._2571": [
            "ConceptCouplingSocket"
        ],
        "_private.system_model.connections_and_sockets.couplings._2572": [
            "CouplingConnection"
        ],
        "_private.system_model.connections_and_sockets.couplings._2573": [
            "CouplingSocket"
        ],
        "_private.system_model.connections_and_sockets.couplings._2574": [
            "PartToPartShearCouplingConnection"
        ],
        "_private.system_model.connections_and_sockets.couplings._2575": [
            "PartToPartShearCouplingSocket"
        ],
        "_private.system_model.connections_and_sockets.couplings._2576": [
            "SpringDamperConnection"
        ],
        "_private.system_model.connections_and_sockets.couplings._2577": [
            "SpringDamperSocket"
        ],
        "_private.system_model.connections_and_sockets.couplings._2578": [
            "TorqueConverterConnection"
        ],
        "_private.system_model.connections_and_sockets.couplings._2579": [
            "TorqueConverterPumpSocket"
        ],
        "_private.system_model.connections_and_sockets.couplings._2580": [
            "TorqueConverterTurbineSocket"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ClutchConnection",
    "ClutchSocket",
    "ConceptCouplingConnection",
    "ConceptCouplingSocket",
    "CouplingConnection",
    "CouplingSocket",
    "PartToPartShearCouplingConnection",
    "PartToPartShearCouplingSocket",
    "SpringDamperConnection",
    "SpringDamperSocket",
    "TorqueConverterConnection",
    "TorqueConverterPumpSocket",
    "TorqueConverterTurbineSocket",
)
