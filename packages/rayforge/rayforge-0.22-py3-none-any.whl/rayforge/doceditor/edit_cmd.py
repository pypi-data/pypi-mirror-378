import uuid
import logging
from typing import TYPE_CHECKING, List, Dict, Tuple, Sequence
from ..core.item import DocItem
from ..core.group import Group
from ..core.workpiece import WorkPiece
from ..core.workflow import Workflow
from ..core.stocklayer import StockLayer
from ..undo import ListItemCommand, ReorderListCommand

if TYPE_CHECKING:
    from .editor import DocEditor

logger = logging.getLogger(__name__)


class EditCmd:
    """Handles clipboard, duplication, and removal of document items."""

    def __init__(self, editor: "DocEditor"):
        self._editor = editor
        # Module-level state for the clipboard is now instance state
        self._clipboard_snapshot: List[Dict] = []
        self._paste_counter = 0
        self._paste_increment_mm: Tuple[float, float] = (10.0, -10.0)

    def can_paste(self) -> bool:
        """Checks if there is anything on the clipboard to paste."""
        return len(self._clipboard_snapshot) > 0

    def _get_top_level_items(
        self, all_items: Sequence[DocItem]
    ) -> List[DocItem]:
        """From a list of items, returns only the top-level ones."""
        if not all_items:
            return []

        item_set = set(all_items)
        top_level = []
        for item in all_items:
            has_selected_ancestor = False
            parent = item.parent
            while parent:
                if parent in item_set:
                    has_selected_ancestor = True
                    break
                parent = parent.parent
            if not has_selected_ancestor:
                top_level.append(item)
        return top_level

    def copy_items(self, items: List[DocItem]):
        """
        Snapshots the current state of the selected items for the clipboard
        and resets the paste sequence. It only copies the top-level items
        from the selection to avoid redundancy.
        """
        if not items:
            return

        top_level_items = self._get_top_level_items(items)

        self._clipboard_snapshot = [item.to_dict() for item in top_level_items]
        self._paste_counter = 1  # For a copy, the next paste should be offset.
        logger.debug(
            f"Copied {len(self._clipboard_snapshot)} top-level items. "
            "Paste counter set to 1."
        )

    def cut_items(self, items: List[DocItem]):
        """
        Copies the selected items to the clipboard and then removes them
        from the document in a single undoable transaction.
        """
        if not items:
            return

        self.copy_items(items)
        # For a cut, the next paste should be at the original location.
        self._paste_counter = 0

        self.remove_items(items, "Cut item(s)")

    def paste_items(self) -> List[DocItem]:
        """
        Pastes a new set of items from the clipboard snapshot. It creates new
        unique IDs for all pasted items and their children, and applies a
        cumulative offset for each subsequent paste.

        Returns:
            A list of the newly created top-level items.
        """
        if not self.can_paste():
            return []

        doc = self._editor.doc
        history = self._editor.history_manager
        newly_pasted_items = []

        active_layer_was_stock = isinstance(doc.active_layer, StockLayer)
        target_layer = self._editor.default_workpiece_layer

        with history.transaction(_("Paste item(s)")) as t:
            offset_x = self._paste_increment_mm[0] * self._paste_counter
            offset_y = self._paste_increment_mm[1] * self._paste_counter

            for item_dict in self._clipboard_snapshot:
                # Recreate item from dictionary. Assumes 'type' key exists.
                if item_dict.get("type") == "group":
                    new_item = Group.from_dict(item_dict)
                else:  # Assume WorkPiece as default
                    new_item = WorkPiece.from_dict(item_dict)

                # Assign new UIDs to the pasted item and all its children
                # recursively
                def assign_new_uids(item: DocItem):
                    item.uid = str(uuid.uuid4())
                    for child in item.children:
                        assign_new_uids(child)

                assign_new_uids(new_item)
                newly_pasted_items.append(new_item)

                # Apply offset to the top-level pasted item's position
                original_pos = new_item.pos
                new_item.pos = (
                    original_pos[0] + offset_x,
                    original_pos[1] + offset_y,
                )

                command = ListItemCommand(
                    owner_obj=target_layer,
                    item=new_item,
                    undo_command="remove_child",
                    redo_command="add_child",
                    name=_("Paste item"),
                )
                t.execute(command)

        # Increment counter for the *next* paste
        self._paste_counter += 1

        if active_layer_was_stock:
            self._editor.notification_requested.send(
                self,
                message=_("Items pasted onto layer '{layer_name}'").format(
                    layer_name=target_layer.name
                ),
            )

        return newly_pasted_items

    def duplicate_items(self, items: List[DocItem]) -> List[DocItem]:
        """
        Creates an exact copy of the selected items in the same location.
        This operation is a single undoable transaction.

        Returns:
            A list of the newly created top-level items.
        """
        if not items:
            return []

        doc = self._editor.doc
        history = self._editor.history_manager
        newly_duplicated_items = []

        active_layer_was_stock = isinstance(doc.active_layer, StockLayer)
        target_layer = self._editor.default_workpiece_layer

        top_level_items = self._get_top_level_items(items)

        with history.transaction(_("Duplicate item(s)")) as t:
            for item in top_level_items:
                item_dict = item.to_dict()

                if item_dict.get("type") == "group":
                    new_item = Group.from_dict(item_dict)
                else:
                    new_item = WorkPiece.from_dict(item_dict)

                def assign_new_uids(item: DocItem):
                    item.uid = str(uuid.uuid4())
                    for child in item.children:
                        assign_new_uids(child)

                assign_new_uids(new_item)
                newly_duplicated_items.append(new_item)

                # A duplicated item has the same position as the original.
                # No offset is applied. The deserialized new_item already
                # has the correct matrix.

                command = ListItemCommand(
                    owner_obj=target_layer,
                    item=new_item,
                    undo_command="remove_child",
                    redo_command="add_child",
                    name=_("Duplicate item"),
                )
                t.execute(command)

        if active_layer_was_stock:
            self._editor.notification_requested.send(
                self,
                message=_("Items duplicated onto layer '{layer_name}'").format(
                    layer_name=target_layer.name
                ),
            )

        return newly_duplicated_items

    def remove_items(
        self,
        items: List[DocItem],
        transaction_name: str = "Remove item(s)",
    ):
        """Removes a list of items from the document."""
        if not items:
            return

        history = self._editor.history_manager
        top_level_items = self._get_top_level_items(items)

        with history.transaction(_(transaction_name)) as t:
            for item in top_level_items:
                if not item.parent:
                    logger.warning(
                        f"Attempted to remove item '{item.name}' which "
                        "has no parent."
                    )
                    continue
                command = ListItemCommand(
                    owner_obj=item.parent,
                    item=item,
                    undo_command="add_child",
                    redo_command="remove_child",
                    name=_("Remove item"),
                )
                t.execute(command)

    def clear_all_items(self):
        """
        Removes all workpieces and groups from all layers in the document in a
        single undoable transaction.
        """
        doc = self._editor.doc
        if not doc.has_workpiece():
            return

        with doc.history_manager.transaction(_("Remove all workpieces")) as t:
            for layer in doc.layers:
                # A layer is considered "not empty" if it has any children
                # besides its mandatory workflow.
                if any(
                    not isinstance(child, Workflow) for child in layer.children
                ):
                    command = ReorderListCommand(
                        target_obj=layer,
                        list_property_name="children",
                        new_list=[layer.workflow],
                        setter_method_name="set_children",
                        name=_("Clear Layer Items"),
                    )
                    t.execute(command)

    def reset_paste_counter(self):
        """
        Resets the paste counter. This is typically called when the context
        changes, such as selecting a new layer, to ensure the next paste
        operation does not continue an offset chain from a previous context.
        The next paste will be "in place".
        """
        if self._paste_counter != 0:
            logger.debug("Paste counter reset to 0 due to context change.")
            self._paste_counter = 0
