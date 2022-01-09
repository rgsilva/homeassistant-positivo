import random
from dataclasses import dataclass

from .common import bits_to_pulses, pulses_to_hex

NEC_START_RANGE = [
    range(9000, 9500),
    range(4000, 5000)
]
NEC_END_RANGE = range(400, 600)

NEC_SHORT_RANGE = range(200,800)
NEC_LONG_RANGE = range(1400,2100)

NEC_SHORT = 600
NEC_LONG = 1500


@dataclass
class Command:
    address: int
    command: int


def encode(command: Command) -> str:
    pulses = []

    # NEC begin
    for r in NEC_START_RANGE:
        pulses.append(random.randint(r.start, r.stop - 1))
    
    data = (
        (~command.command & 0xFF) << 24 | \
        command.command << 16 | \
        (~command.address & 0xFF) << 8 | \
        command.address)

    # the 8-bit address for the receiving device
    # the 8-bit logical inverse of the address
    # the 8-bit command
    # the 8-bit logical inverse of the command

    # Now generate the pulses for each bit of the raw data.
    nec_pulse = lambda value: bits_to_pulses(value, 8, True, NEC_SHORT, NEC_LONG, NEC_SHORT, NEC_SHORT)

    addr = (data & 0xFF)
    pulses += nec_pulse(addr)

    addr_inv = (data >> 8 & 0xFF)
    pulses += nec_pulse(addr_inv)

    cmd = (data >> 16 & 0xFF)
    pulses += nec_pulse(cmd)

    cmd_inv = (data >> 24 & 0xFF)
    pulses += nec_pulse(cmd_inv)

    # NEC end
    pulses.append(random.randint(NEC_END_RANGE.start, NEC_END_RANGE.stop - 1))

    pulses_hex = pulses_to_hex(pulses)

    # Required suffix?
    pulses_hex += "220cb"

    return pulses_hex