"""
Defines the Layer class, a central component for organizing and processing
workpieces within a document.
"""

from __future__ import annotations
import logging
from typing import List, Tuple, Optional, TypeVar, Iterable, Dict
from blinker import Signal

from ..core.step import Step
from ..core.workflow import Workflow
from .item import DocItem
from .workpiece import WorkPiece

logger = logging.getLogger(__name__)

# For generic type hinting in add_child
T = TypeVar("T", bound="DocItem")


class Layer(DocItem):
    """
    Represents a group of workpieces processed by a single workflow.

    A Layer acts as a container for `WorkPiece` objects and owns a
    `Workflow`. It is a `DocItem` and automatically manages its children
    and bubbles up signals.
    """

    def __init__(self, name: str):
        """Initializes a Layer instance.

        Args:
            name: The user-facing name of the layer.
        """
        super().__init__(name=name)
        self.visible: bool = True

        # Signals for notifying other parts of the application of changes.
        # This one is special and is bubbled manually.
        self.post_step_transformer_changed = Signal()

        # A new layer gets a workflow automatically.
        workflow = Workflow(f"{name} Workflow")
        self.add_child(workflow)

    def to_dict(self) -> Dict:
        """Serializes the layer and its children to a dictionary."""
        return {
            "uid": self.uid,
            "type": "layer",
            "name": self.name,
            "matrix": self.matrix.to_list(),
            "visible": self.visible,
            "children": [child.to_dict() for child in self.children],
        }

    @property
    def workpieces(self) -> List[WorkPiece]:
        """
        Returns a list of all child items that are WorkPieces.
        Note: This only returns direct children.
        """
        return [
            child for child in self.children if isinstance(child, WorkPiece)
        ]

    @property
    def all_workpieces(self) -> List["WorkPiece"]:
        """
        Recursively finds and returns a flattened list of all WorkPiece
        objects contained within this layer, including those inside groups.
        """
        return self.get_descendants(of_type=WorkPiece)

    def get_content_items(self) -> List["DocItem"]:
        """
        Returns a list of user-facing items in this layer (e.g.,
        WorkPieces, Groups), excluding internal objects like Workflows.
        """
        return [
            child for child in self.children
            if not isinstance(child, Workflow)
        ]

    @property
    def workflow(self) -> Optional[Workflow]:
        """Returns the layer's workflow. A layer must have one workflow."""
        for child in self.children:
            if isinstance(child, Workflow):
                return child
        # This state should be unreachable for a standard Layer, but subclasses
        # like StockLayer may not have a workflow.
        return None

    def _on_workflow_post_transformer_changed(self, sender):
        """
        Bubbles up the post_transformer_changed signal from the workflow.
        """
        self.post_step_transformer_changed.send(self)

    def add_child(self, child: T, index: Optional[int] = None) -> T:
        if isinstance(child, Workflow):
            child.post_step_transformer_changed.connect(
                self._on_workflow_post_transformer_changed
            )
        super().add_child(child, index)
        return child

    def remove_child(self, child: DocItem):
        if isinstance(child, Workflow):
            # Check if the workflow actually exists before trying to disconnect
            wf = self.workflow
            if wf and wf is child:
                wf.post_step_transformer_changed.disconnect(
                    self._on_workflow_post_transformer_changed
                )
        super().remove_child(child)

    def set_children(self, new_children: Iterable[DocItem]):
        # Disconnect any existing workflow signal handlers
        if self.workflow:
            self.workflow.post_step_transformer_changed.disconnect(
                self._on_workflow_post_transformer_changed
            )

        # Connect to the new ones
        for child in new_children:
            if isinstance(child, Workflow):
                child.post_step_transformer_changed.connect(
                    self._on_workflow_post_transformer_changed
                )

        super().set_children(new_children)

    @property
    def active(self) -> bool:
        """
        Returns True if this layer is the currently active layer in the
        document.
        """
        return self.doc.active_layer is self if self.doc else False

    def set_name(self, name: str):
        """Sets the name of the layer.

        Args:
            name: The new name for the layer.
        """
        if self.name == name:
            return
        self.name = name
        wf = self.workflow
        if wf:
            wf.name = f"{name} Workflow"
        self.updated.send(self)

    def set_visible(self, visible: bool):
        """Sets the visibility of the layer.

        Args:
            visible: The new visibility state.
        """
        if self.visible == visible:
            return
        self.visible = visible
        self.updated.send(self)

    def add_workpiece(self, workpiece: "WorkPiece"):
        """Adds a single workpiece to the layer."""
        self.add_child(workpiece)

    def remove_workpiece(self, workpiece: "WorkPiece"):
        """Removes a single workpiece from the layer."""
        self.remove_child(workpiece)

    def set_workpieces(self, workpieces: List["WorkPiece"]):
        """
        Sets the layer's workpieces to a new list, preserving the
        existing workflow.
        """
        current_workflow = self.workflow
        new_children: List[DocItem] = list(workpieces)
        if current_workflow:
            new_children.append(current_workflow)
        self.set_children(new_children)

    def get_renderable_items(self) -> List[Tuple[Step, WorkPiece]]:
        """
        Gets a list of all visible step/workpiece pairs for rendering.

        Returns:
            A list of (Step, WorkPiece) tuples that are currently
            visible and have valid geometry for rendering.
        """
        if not self.visible or not self.workflow:
            return []
        items = []
        # Use the correct recursive method to find all workpieces
        for workpiece in self.all_workpieces:
            if any(s <= 0 for s in workpiece.size):
                continue
            for step in self.workflow.steps:
                if step.visible:
                    items.append((step, workpiece))
        return items
