from typing import List, Optional

def bits_to_pulses(
        value: int,
        value_bits: int,
        lsb_first: bool,
        space: int,
        one: int,
        zero: int,      
        prefix: Optional[int] = None,
        suffix: Optional[int] = None,
    ) -> List[int]:

    # The pulse representing a logical "1" is a 1.2ms long burst of the 40kHz carrier
    # while the burst width for a logical "0" is 0.6ms long.
    # All bursts are separated by a 0.6ms long space interval.

    pulses = []
    binvalue = "{0:b}".format(value)
    if len(binvalue) > value_bits:
        raise ValueError(f"Value {value} has more bits than expected ({value_bits})")
    elif len(binvalue) < value_bits:
        padding = "0" * (value_bits - len(binvalue))
        binvalue = padding + binvalue

    if lsb_first:
        binvalue = binvalue[::-1]

    if prefix is not None:
        pulses.append(prefix)

    for index in range(0, value_bits):
        bit = binvalue[index]

        if bit == "0":
            pulses.append(zero)
        elif bit == "1":
            pulses.append(one)
        
        if index < (len(binvalue) - 1):
            pulses.append(space)

    if suffix is not None:
        pulses.append(suffix)

    return pulses


def pulses_to_hex(pulses: List[int]) -> str:
    pulses_hex = ""
    for pulse in pulses:
        pulse_hex = "{0:04x}".format(pulse)
        pulse_hex = pulse_hex[2:4] + pulse_hex[0:2]
        pulses_hex += pulse_hex
    
    return pulses_hex
