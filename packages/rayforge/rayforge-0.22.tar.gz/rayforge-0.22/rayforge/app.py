# flake8: noqa: E402
import warnings
import logging
import mimetypes
import argparse
import sys
import os
import gettext
import asyncio  # Import asyncio
from pathlib import Path

# ===================================================================
# SECTION 1: SAFE, MODULE-LEVEL SETUP
# This code will run for the main app AND all subprocesses.
# ===================================================================

# Configure basic logging first.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Suppress NumPy longdouble UserWarning when run under mingw on Windows
warnings.filterwarnings(
    "ignore",
    message="Signature.*for <class 'numpy.longdouble'> does not"
    " match any known type",
)

# Gettext MUST be initialized before importing app modules.
# This MUST run at the module level so that the `_` function is
# available to any module (in any process) that gets imported.
if hasattr(sys, "_MEIPASS"):
    # In a PyInstaller bundle, the project root is in a temporary
    # directory stored in sys._MEIPASS.
    base_dir = Path(sys._MEIPASS)  # type: ignore
else:
    # In other environments, this is safer.
    base_dir = Path(__file__).parent.parent

# Make "_" available in all modules
locale_dir = base_dir / "rayforge" / "locale"
logger.debug(f"Loading locales from {locale_dir}")
gettext.install("rayforge", locale_dir)

# --------------------------------------------------------
# GObject Introspection Repository (gi)
# --------------------------------------------------------
# When running in a PyInstaller bundle, we need to set the GI_TYPELIB_PATH
# environment variable to point to the bundled typelib files.
if hasattr(sys, "_MEIPASS"):
    typelib_path = base_dir / "gi" / "repository"
    logger.info(f"GI_TYPELIB_PATH is {typelib_path}")
    os.environ["GI_TYPELIB_PATH"] = str(typelib_path)
    files = [p.name for p in typelib_path.iterdir()]
    logger.info(f"Files in typelib path: {files}")


def main():
    # ===================================================================
    # SECTION 2: MAIN APPLICATION ENTRY POINT
    # This function contains all logic that should ONLY run in the
    # main process.
    # ===================================================================

    # We need Adw for the class definition, so this one import is okay here.
    import gi

    gi.require_version("Adw", "1")
    from gi.repository import Adw

    class App(Adw.Application):
        def __init__(self, args):
            super().__init__(application_id="com.barebaric.rayforge")
            self.set_accels_for_action("win.quit", ["<Ctrl>Q"])
            self.args = args

        def do_activate(self):
            # Import the window here to avoid module-level side-effects
            from rayforge.mainwindow import MainWindow
            from rayforge.core.vectorization_config import TraceConfig

            win = MainWindow(application=self)
            # self.args.filenames will be a list of paths
            if self.args.filenames:
                for filename in self.args.filenames:
                    mime_type, _ = mimetypes.guess_type(filename)

                    # Default to tracing any file that supports it. If
                    # --direct-vector is passed, attempt to use vectors
                    # directly by passing a None config.
                    vector_config = (
                        None if self.args.direct_vector else TraceConfig()
                    )
                    win.doc_editor.file.load_file_from_path(
                        filename=Path(filename),
                        mime_type=mime_type,
                        vector_config=vector_config,
                    )
            win.present()

    # Import version for the --version flag.
    from rayforge import __version__

    parser = argparse.ArgumentParser(
        description=_("A GCode generator for laser cutters.")
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "filenames",
        help=_("Paths to one or more input SVG or image files."),
        nargs="*",
    )
    parser.add_argument(
        "--direct-vector",
        action="store_true",
        help=_("Import SVG files as direct vectors instead of tracing them."),
    )
    parser.add_argument(
        "--loglevel",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=_("Set the logging level (default: INFO)"),
    )

    args = parser.parse_args()

    # Set logging level based on the command-line argument
    log_level = getattr(logging, args.loglevel.upper(), logging.INFO)
    logging.getLogger().setLevel(log_level)
    logger.info(f"Application starting with log level {args.loglevel.upper()}")

    # ===================================================================
    # SECTION 3: PLATFORM SPECIFIC INITIALIZATION
    # ===================================================================

    # When running on Windows, spawned subprocesses do not
    # know where to find the necessary DLLs (for cairo, rsvg, etc.).
    # We must explicitly add the executable's directory to the
    # DLL search path *before* any subprocesses are created.
    # This must be done inside the main() guard.
    if sys.platform == "win32":
        logger.info(
            f"Windows build detected. Adding '{base_dir}' to DLL search path."
        )
        os.add_dll_directory(str(base_dir))

    # Set the PyOpenGL platform before importing anything that uses OpenGL.
    # 'egl' is generally the best choice for GTK4 on modern Linux (Wayland/X11).
    # On Windows and macOS, letting PyOpenGL auto-detect is more reliable.
    if sys.platform.startswith("linux"):
        logger.info("Linux detected. Setting PYOPENGL_PLATFORM=egl")
        os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

    # Print PyCairo version
    import cairo

    logger.info(f"PyCairo version: {cairo.version}")

    # Register the standalone 'cairo' module
    # as a foreign type *before* the GObject-introspected cairo is loaded.
    gi.require_foreign("cairo")

    # Now, when gi.repository.cairo is loaded, it will know how to
    # interact with the already-imported standalone module.
    gi.require_version("cairo", "1.0")
    gi.require_version("Gtk", "4.0")
    gi.require_version("GdkPixbuf", "2.0")

    # Initialize the 3D canvas module to check for OpenGL availability.
    # This must be done after setting the platform env var and after
    # making Gtk available in gi, as the canvas uses Gtk.
    # The rest of the app can now check `rayforge.canvas3d.initialized`.
    # It is safe to import other modules that depend on canvas3d after this.
    from rayforge.workbench import canvas3d

    canvas3d.initialize()

    # Import modules that depend on GTK or manage global state
    import rayforge.shared.tasker
    import rayforge.config

    # Explicitly initialize the configuration managers. This ensures that
    # this expensive, stateful setup only runs in the main process, not
    # in any subprocesses spawned by the TaskManager.
    rayforge.config.initialize_managers()

    # Run application
    app = App(args)
    exit_code = app.run(None)

    # ===================================================================
    # SECTION 4: SHUTDOWN SEQUENCE
    # ===================================================================

    logger.info("Application exiting.")

    # 1. Define an async function to shut down high-level components.
    async def shutdown_async():
        logger.info("Starting graceful async shutdown...")
        if rayforge.config.machine_mgr:
            await rayforge.config.machine_mgr.shutdown()
        logger.info("Async shutdown complete.")

    # 2. Run the async shutdown on the TaskManager's event loop and wait for it.
    loop = rayforge.shared.tasker.task_mgr._loop
    if loop.is_running():
        future = asyncio.run_coroutine_threadsafe(shutdown_async(), loop)
        try:
            # Block until the async cleanup is finished.
            future.result(timeout=10)
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}")
    else:
        logger.warning(
            "Task manager loop not running, skipping async shutdown."
        )

    # 3. Save configuration. This happens AFTER async tasks are done.
    if rayforge.config.config_mgr:
        rayforge.config.config_mgr.save()
    logger.info("Saved config.")

    # 4. As the final step, shut down the task manager itself.
    rayforge.shared.tasker.task_mgr.shutdown()
    logger.info("Task manager shut down.")

    return exit_code


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()  # needed to use multiprocessing in PyInstaller bundles
    sys.exit(main())
