from copy import copy
from typing import List, cast
from .commands import (
    ArcToCommand,
    MovingCommand,
    MoveToCommand,
    ScanLinePowerCommand,
)


def flip_segment(segment: List[MovingCommand]) -> List[MovingCommand]:
    """
    Reverses a segment of path commands, correctly adjusting states and
    ArcToCommand parameters.

    The states attached to each point describe the intended machine state
    while traveling TO that point. When flipping, states must be shifted
    to maintain this relationship. Arcs must also have their parameters
    recalculated relative to their new start point.
    """
    length = len(segment)
    if length <= 1:
        return segment

    new_segment: List[MovingCommand] = []

    # The first command of the new segment is a MoveTo, created from the
    # original segment's first MoveTo command.
    first_cmd = MoveToCommand(end=segment[-1].end)
    first_cmd.state = segment[0].state
    new_segment.append(first_cmd)

    # Process the rest of the commands in reverse
    for i in range(length - 2, -1, -1):
        original_cmd = segment[i + 1]
        new_cmd = copy(original_cmd)  # Copies type (LineTo, ArcTo) and state
        new_cmd.end = segment[i].end

        if isinstance(new_cmd, ArcToCommand):
            # The original arc's start point is the endpoint of the command
            # before it in the original segment.
            original_start = segment[i].end
            assert original_start is not None
            # Delegate the complex recalculation to the command itself.
            new_cmd.reverse_geometry(
                original_start=original_start,
                original_end=original_cmd.end,
            )
        elif isinstance(new_cmd, ScanLinePowerCommand):
            # We know original_cmd must also be a ScanLinePowerCommand
            # because new_cmd is a copy of it.
            original_scan_cmd = cast(ScanLinePowerCommand, original_cmd)

            # Manually perform the reversal to avoid side-effects on the
            # original command object.
            # The new start_point is the original command's end point.
            new_cmd.start_point = original_scan_cmd.end
            # The new end point was already set correctly above.
            # Create a reversed COPY of the power values.
            new_cmd.power_values = original_scan_cmd.power_values[::-1]
        new_segment.append(new_cmd)

    return new_segment
