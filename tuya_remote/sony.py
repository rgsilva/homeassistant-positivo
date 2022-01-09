from dataclasses import dataclass

from .common import bits_to_pulses

@dataclass
class Command:
    address: int
    command: int
    repeat: int = 2


def encode(command: Command) -> str:
    command_pulses = []

    # SIRC begin
    command_pulses.append(2400)
    command_pulses.append(600)

    # Encode command and address
    command_pulses += bits_to_pulses(command.command, 7, True, 600, 1200, 600, suffix=600)
    command_pulses += bits_to_pulses(command.address, 5, True, 600, 1200, 600, suffix=600)

    gap = [10, 45000 - sum(command_pulses)]
    pulses = []
    for rep in range(0, command.repeat):
        pulses += command_pulses
        if rep < command.repeat - 1:
            pulses += gap

    pulses_hex = ""
    for pulse in pulses:
        pulse_hex = "{0:04x}".format(pulse)
        pulse_hex = pulse_hex[2:4] + pulse_hex[0:2]
        pulses_hex += pulse_hex

    return pulses_hex
