import base64

from Crypto.Util.number import long_to_bytes
from dataclasses import dataclass
from typing import Any, Callable, Type

from . import sony, nec

@dataclass
class ProtocolDefinition:
    name: str
    type: Type
    encoder: Callable[[Any], str]


PROTOCOLS = [
    ProtocolDefinition("NEC", nec.Command, nec.encode),
    ProtocolDefinition("Sony", sony.Command, sony.encode),
]

AVAILABLE_PROTOCOLS = list(p.name for p in PROTOCOLS)

def _data_to_hex(data):
    pulses = []
    offset = 0
    while offset < len(data):
        pulse = data[offset:offset + 4]
        pulse = int(pulse, 16)
        pulses.append(pulse)
        offset += 4

    dps7_bytes = bytes()
    for p in pulses:
        dps7_bytes += long_to_bytes(p)
    encoded = base64.encodebytes(dps7_bytes)
    encoded = encoded.decode("utf8").replace("\n", "")

    return encoded


def tuya_encode(protocol_name: str, command: Any) -> str:
    for protocol in PROTOCOLS:
        if protocol.name == protocol_name:
            actual_command = protocol.type(**command)
            encoded = protocol.encoder(actual_command)
            return _data_to_hex(encoded)
    
    raise ValueError(f"Unknown protocol {protocol_name}")

