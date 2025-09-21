from typing import cast
from gi.repository import Gtk
from ...machine.models.machine import Machine
from ...machine.models.script import Script
from ...icons import get_icon
from ...shared.util.adw import PreferencesGroupWithButton
from .code_editor import CodeEditorDialog


class MacroRow(Gtk.Box):
    """A widget representing a single Macro in a ListBox."""

    def __init__(self, machine: Machine, script: Script):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.machine = machine
        self.script = script
        self._setup_ui()

    def _setup_ui(self):
        """Builds the user interface for the row."""
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_margin_start(12)
        self.set_margin_end(6)

        title_label = Gtk.Label(
            label=self.script.name,
            halign=Gtk.Align.START,
            hexpand=True,
            xalign=0,
        )
        self.append(title_label)

        # Suffix area for switch and buttons
        suffix_box = Gtk.Box(spacing=6, valign=Gtk.Align.CENTER)
        self.append(suffix_box)

        switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        switch.set_active(self.script.enabled)
        switch.connect("notify::active", self._on_enable_toggled)
        suffix_box.append(switch)

        edit_button = Gtk.Button(child=get_icon("document-edit-symbolic"))
        edit_button.add_css_class("flat")
        edit_button.connect("clicked", self._on_edit_clicked)
        suffix_box.append(edit_button)

        delete_button = Gtk.Button(child=get_icon("delete-symbolic"))
        delete_button.add_css_class("flat")
        delete_button.connect("clicked", self._on_remove_clicked)
        suffix_box.append(delete_button)

    def _on_enable_toggled(self, switch: Gtk.Switch, _):
        """Handles the state change of the enable/disable switch."""
        is_active = switch.get_active()
        if self.script.enabled != is_active:
            self.script.enabled = is_active
            self.machine.changed.send(self.machine)

    def _on_remove_clicked(self, button: Gtk.Button):
        """Asks the machine to remove the associated macro."""
        self.machine.remove_macro(self.script.uid)

    def _on_edit_clicked(self, button: Gtk.Button):
        """Opens the CodeEditorDialog to edit the macro."""
        parent_window = cast(Gtk.Window, self.get_ancestor(Gtk.Window))

        # Pass the list of other macros for uniqueness validation
        existing_scripts = list(self.machine.macros.values())

        dialog = CodeEditorDialog(
            parent_window,
            self.script,
            allow_name_edit=True,
            existing_scripts=existing_scripts,
        )
        dialog.connect("close-request", self._on_edit_dialog_closed)
        dialog.present()

    def _on_edit_dialog_closed(self, dialog: CodeEditorDialog):
        """Signals a machine change if the macro was saved."""
        if dialog.saved:
            self.machine.changed.send(self.machine)


class MacroListEditor(PreferencesGroupWithButton):
    """
    An Adwaita widget for displaying and managing a list of G-code macros.
    """

    def __init__(self, machine: Machine, **kwargs):
        super().__init__(button_label=_("Add New Macro"), **kwargs)
        self.machine = machine
        self._setup_ui()
        self.machine.changed.connect(self._on_machine_changed)
        self._on_machine_changed(self.machine)  # Initial population

    def _setup_ui(self):
        """Configures the widget and its placeholder."""
        placeholder = Gtk.Label(
            label=_("No macros configured"),
            halign=Gtk.Align.CENTER,
            margin_top=12,
            margin_bottom=12,
        )
        placeholder.add_css_class("dim-label")
        self.list_box.set_placeholder(placeholder)

    def _on_machine_changed(self, sender: Machine, **kwargs):
        """Callback to rebuild the list when the machine model changes."""
        sorted_macros = sorted(
            self.machine.macros.values(), key=lambda m: m.name
        )
        self.set_items(sorted_macros)

    def create_row_widget(self, item: Script) -> Gtk.Widget:
        """Creates a MacroRow for the given script item."""
        return MacroRow(self.machine, item)

    def _on_add_clicked(self, button: Gtk.Button):
        """Handles the 'Add New Macro' button click."""
        parent = cast(Gtk.Window, self.get_ancestor(Gtk.Window))
        new_script = Script(name=_("New Macro"))

        # Pass the list of existing macros for uniqueness validation
        existing_scripts = list(self.machine.macros.values())

        editor_dialog = CodeEditorDialog(
            parent,
            new_script,
            allow_name_edit=True,
            existing_scripts=existing_scripts,
        )
        editor_dialog.connect(
            "close-request", self._on_new_macro_editor_closed, new_script
        )
        editor_dialog.present()

    def _on_new_macro_editor_closed(
        self, dialog: CodeEditorDialog, new_script: Script
    ):
        """Asks the machine to add the new macro if it was saved."""
        if dialog.saved:
            self.machine.add_macro(new_script)
