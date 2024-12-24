import chardet


def detect_encoding_from_bytes(bytes, chunk_size=1024):
    """
    Detect the encoding of bytes data.

    :param bytes: The bytes data to detect the encoding from.
    :param chunk_size: Chunk size to feed into the encoding detector.

    :return: The detected encoding.
    """
    detector = chardet.UniversalDetector()
    offset = 0
    while offset < len(bytes):
        # Extract a chunk of data
        data = bytes[offset : offset + chunk_size]

        # Feed the chunk of data to the encoding detector
        detector.feed(data)

        # Check if the detector has reached a conclusion
        if detector.done:
            break

        # Update the offset to process the next chunk
        offset += chunk_size

    # Close the encoding detector
    detector.close()

    return detector.result["encoding"]
