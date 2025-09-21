import logging
from typing import cast, TYPE_CHECKING
from ...core.workflow import Step
from ..canvas import CanvasElement
from .workpiece import WorkPieceView

if TYPE_CHECKING:
    from ...pipeline.generator import OpsGenerator


logger = logging.getLogger(__name__)


class StepElement(CanvasElement):
    """
    A non-rendering CanvasElement that manages the view-state for a Step.

    This element is the "controller" for a Step in the view. Its primary job
    is to listen to its model for visibility changes and then broadcast that
    state to all sibling WorkPieceView elements within the same layer.
    Its lifecycle is automatically managed by its parent LayerElement.
    """

    def __init__(
        self,
        step: Step,
        ops_generator: "OpsGenerator",
        **kwargs,
    ):
        """
        Initializes a StepElement.

        Args:
            step: The Step data object.
            ops_generator: The central generator for pipeline operations.
            **kwargs: Additional keyword arguments for CanvasElement.
        """
        super().__init__(
            x=0,
            y=0,
            width=0,
            height=0,  # No dimensions needed
            data=step,
            selectable=False,
            visible=step.visible,  # Sync initial visibility
            **kwargs,
        )
        self.ops_generator = ops_generator

        # Connect to the model signal that drives its behavior
        step.visibility_changed.connect(self._on_visibility_changed)

    def remove(self):
        """Disconnects signals before removing the element."""
        step = cast(Step, self.data)
        step.visibility_changed.disconnect(self._on_visibility_changed)
        super().remove()

    def _on_visibility_changed(self, step: Step):
        """
        Handles visibility changes from the model. It updates its own state
        and then broadcasts the change to its siblings.
        """
        if not self.visible == step.visible:
            self.set_visible(step.visible)
            self._update_sibling_ops_visibility()

    def _update_sibling_ops_visibility(self):
        """
        THE CORE LOGIC: Finds all WorkPieceView siblings in the same parent
        (LayerElement) and tells them to update the visibility of the ops
        layer corresponding to this step.
        """
        if not self.parent:
            return

        step_uid = self.data.uid
        is_visible = self.visible

        logger.debug(
            f"StepElement '{self.data.name}' broadcasting visibility "
            f"({is_visible}) to siblings."
        )

        # Iterate through all children of the parent (the LayerElement)
        for child in self.parent.children:
            if isinstance(child, WorkPieceView):
                child.set_ops_visibility(step_uid, is_visible)
