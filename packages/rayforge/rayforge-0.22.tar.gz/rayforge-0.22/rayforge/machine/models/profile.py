import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
from .machine import Machine, Laser
from .script import Script, ScriptTrigger
from ..driver import get_driver_cls


logger = logging.getLogger(__name__)


@dataclass
class MachineProfile:
    """
    A template for creating a new Machine instance with pre-configured
    settings. All fields are optional to allow for partial profiles.
    """

    name: str
    driver_class_name: Optional[str] = None
    dialect_name: Optional[str] = None
    gcode_precision: Optional[int] = None
    dimensions: Optional[Tuple[int, int]] = None
    y_axis_down: Optional[bool] = None
    max_travel_speed: Optional[int] = None
    max_cut_speed: Optional[int] = None
    driver_args: Optional[Dict[str, Any]] = None
    home_on_start: Optional[bool] = None
    heads: Optional[List[Dict[str, Any]]] = None
    hookscripts: Optional[List[Dict[str, Any]]] = None

    def create_machine(self) -> Machine:
        """
        Creates a Machine instance from this profile.

        Only attributes that are not None in the profile will be applied
        to the new Machine instance, allowing the Machine's own defaults to
        be used for any unspecified profile values.
        """
        m = Machine()
        m.name = self.name

        if self.driver_class_name:
            try:
                driver_cls = get_driver_cls(self.driver_class_name)
                m.set_driver(driver_cls, self.driver_args)
            except (ValueError, ImportError):
                # If driver class not found, we fall back to the default
                # NoDeviceDriver, which is a safe state.
                logger.error(
                    f"failed to create driver {self.driver_class_name}"
                    f" with args {self.driver_args}"
                )

        if self.dialect_name is not None:
            m.dialect_name = self.dialect_name
        if self.gcode_precision is not None:
            m.gcode_precision = self.gcode_precision
        if self.dimensions is not None:
            m.dimensions = self.dimensions
        if self.y_axis_down is not None:
            m.y_axis_down = self.y_axis_down
        if self.max_travel_speed is not None:
            m.max_travel_speed = self.max_travel_speed
        if self.max_cut_speed is not None:
            m.max_cut_speed = self.max_cut_speed
        if self.home_on_start is not None:
            m.home_on_start = self.home_on_start
        if self.hookscripts is not None:
            for s_data in self.hookscripts:
                try:
                    # Profiles define hooks with an internal trigger field
                    trigger = ScriptTrigger[s_data["trigger"]]
                    m.hookscripts[trigger] = Script.from_dict(s_data)
                except (KeyError, ValueError) as e:
                    logger.warning(f"Skipping invalid hook in profile: {e}")

        m.cameras = []

        if self.heads:
            # The machine is initialized with one head. We clear it before
            # applying profile-specific heads. This safely disconnects
            # signals.
            for head in m.heads[:]:
                m.remove_head(head)

            for head_profile in self.heads:
                # Create a laser head from the profile data. The dictionary
                # for each head should have a flat structure with keys that
                # Laser.from_dict can parse, such as "max_power",
                # "frame_power", and "spot_size_mm".
                m.add_head(Laser.from_dict(head_profile))

        return m


PROFILES: List[MachineProfile] = [
    MachineProfile(
        name="Sculpfun iCube",
        driver_class_name="GrblDriver",
        dialect_name="GRBL",
        gcode_precision=3,
        dimensions=(120, 120),
        y_axis_down=False,
        max_travel_speed=3000,
        max_cut_speed=1000,
        home_on_start=True,
        heads=[
            {
                "frame_power": 10.0,
                "spot_size_mm": [0.1, 0.1],
            }
        ],
    ),
    MachineProfile(
        name="Sculpfun S30",
        driver_class_name="GrblSerialDriver",
        dialect_name="GRBL",
        gcode_precision=3,
        dimensions=(400, 400),
        y_axis_down=False,
        max_travel_speed=3000,
        max_cut_speed=1000,
        heads=[
            {
                "frame_power": 10.0,
                "spot_size_mm": [0.1, 0.1],
            }
        ],
    ),
    MachineProfile(
        name=_("Other Device"),
        driver_class_name="GrblDriver",
        dialect_name="GRBL",
        y_axis_down=False,
    ),
]
