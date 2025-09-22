"""Helper functions for codec operations."""

import struct


def generate_multican_payload(
    can_id: int, data: bytes | bytearray | memoryview
) -> list[bytes]:
    """Generate multiple CAN frames for data longer than 8 bytes."""
    b = bytes(data)  # ensure immutable bytes
    length = len(b) & 0xFF
    # header = bytes((0x14, length))
    # full = header + b # header + payload
    full = b  # payload only
    checksum = sum(full) & 0xFF

    # First chunk: [(length>>1)+2, checksum] with uint8 wrap-around
    first_byte = ((length + 1) >> 1) & 0xFF
    chunks: list[bytes] = [bytes((first_byte, checksum))]

    # Then the data, split into 2-byte pieces
    for i in range(0, len(full), 2):
        chunks.append(full[i : i + 2])

    function_code = 0x16
    payloads: list[bytes] = []
    for idx, chunk in enumerate(chunks):
        # Each chunk is prefixed with [function_code, ifd]
        payload = struct.pack(">I", can_id) + bytes((function_code, idx & 0xFF)) + chunk
        payloads.append(payload)
    return payloads
