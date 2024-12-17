import cv2

def compress_frame(frame, compression_level):
    """
    Compresses a frame using the specified JPEG compression level.

    Parameters:
        frame (numpy.ndarray): The input frame to compress.
        compression_level (int): The JPEG compression quality (0-100).

    Returns:
        decompressed_frame (numpy.ndarray): The decompressed frame after compression.
        compressed_size (int): The size of the compressed frame in bytes.
    """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), compression_level]
    success, compressed_frame = cv2.imencode('.jpg', frame, encode_param)
    if not success:
        raise ValueError("Failed to compress the frame.")

    # Return compressed frame and size of compressed data
    return compressed_frame, len(compressed_frame)