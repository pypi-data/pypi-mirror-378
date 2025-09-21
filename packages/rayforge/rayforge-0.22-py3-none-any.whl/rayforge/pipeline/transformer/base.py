from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from blinker import Signal
from enum import Enum, auto
from ...core.ops import Ops
from ...shared.tasker.proxy import BaseExecutionContext
from ...core.workpiece import WorkPiece


class ExecutionPhase(Enum):
    """
    Defines the execution order for different types of OpsTransformers.

    The pipeline runner does not execute transformers in their simple list
    order; it groups them by phase and runs them sequentially. This ensures
    a logical flow where path continuity is preserved for transformers that
    need it.

    The execution order is always:
    1. GEOMETRY_REFINEMENT: For transformers that modify path geometry but
       require it to be continuous (e.g., Smooth, ArcWeld).
    2. PATH_INTERRUPTION: For transformers that intentionally create gaps or
       discontinuities in paths (e.g., TabOpsTransformer).
    3. POST_PROCESSING: For transformers that operate on the final, potentially
       segmented paths (e.g., Optimize, MultiPass).
    """

    GEOMETRY_REFINEMENT = auto()
    PATH_INTERRUPTION = auto()
    POST_PROCESSING = auto()


class OpsTransformer(ABC):
    """
    Transforms an Ops object in-place.
    Examples may include:

    - Applying travel path optimizations
    - Applying arc welding
    """

    def __init__(self, enabled: bool = True, **kwargs):
        self._enabled = enabled
        self.changed = Signal()

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool):
        """Sets the enabled state and signals a change."""
        if self._enabled != enabled:
            self._enabled = enabled
            self.changed.send(self)

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Convenience setter, delegates to set_enabled."""
        self.set_enabled(enabled)

    @property
    def execution_phase(self) -> ExecutionPhase:
        """Defines when this transformer should run."""
        return ExecutionPhase.POST_PROCESSING

    @property
    @abstractmethod
    def label(self) -> str:
        """A short label for the transformation, used in UI."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief one-line description of the transformation."""
        pass

    @abstractmethod
    def run(
        self,
        ops: Ops,
        workpiece: Optional[WorkPiece] = None,
        context: Optional[BaseExecutionContext] = None,
    ) -> None:
        """
        Runs the transformation.

        Args:
            ops: The Ops object to transform in-place.
            workpiece: The WorkPiece model being processed.
            context: Used for progress and cancellation hooks.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the transformer's configuration to a dictionary."""
        return {
            "name": self.__class__.__name__,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpsTransformer":
        """
        Acts as a factory to create a transformer instance from a dictionary.
        This method should be called on the base class, e.g.,
        `OpsTransformer.from_dict(...)`.
        It determines the correct subclass to instantiate based on the 'name'
        field.
        """
        # If this is called on a subclass, it must be implemented there.
        # This factory logic is only for when called on the base class.
        if cls is not OpsTransformer:
            raise NotImplementedError(
                f"{cls.__name__} must implement its own from_dict classmethod."
            )

        # Lazy import to avoid circular dependency
        from . import transformer_by_name

        name = data.get("name")
        if not name:
            raise ValueError("Transformer data is missing 'name' field.")

        target_cls = transformer_by_name.get(name)
        if not target_cls:
            raise ValueError(f"Unknown transformer name: '{name}'")

        # Dispatch to the specific class's from_dict method
        return target_cls.from_dict(data)
