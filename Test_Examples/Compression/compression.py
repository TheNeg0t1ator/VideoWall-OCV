import cv2
from Server.libs.VideoSelector import ChooseCapDevice

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

# Main Program
# Open the video file
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap = cv2.VideoCapture("C:\\Users\\kobed\\Pictures\\EXPORT\\Maoro-004.jpg")
cap = ChooseCapDevice()


if not cap.isOpened():
    print("Error: Cannot open video file.")
    exit()

# Create a window with a slider for quality adjustment
cv2.namedWindow('Decompressed Frame')
cv2.createTrackbar('Quality', 'Decompressed Frame', 50, 100, lambda x: None)  # Slider range: 0-100

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Get the quality value from the slider
    quality = cv2.getTrackbarPos('Quality', 'Decompressed Frame')

    try:
        # Compress the frame using the reusable function
        compressed_frame, compressed_size = compress_frame(frame, quality)
    except ValueError as e:
        print(e)
        break

    # Get the size of the input frame
    input_size = frame.nbytes

    # Display the sizes on the frame
    input_text = f'Input Size: {input_size / 1024:.2f} KB'
    compressed_text = f'Compressed Size: {compressed_size / 1024:.2f} KB'

    decompressed_frame = cv2.imdecode(compressed_frame, cv2.IMREAD_COLOR)
    cv2.putText(decompressed_frame, input_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(decompressed_frame, compressed_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Display the decompressed frame
    cv2.imshow('Decompressed Frame', decompressed_frame)
    
    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
