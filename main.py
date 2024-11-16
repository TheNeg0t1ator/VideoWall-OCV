import cv2
import time

print("starting")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap = cv2.VideoCapture("C:/Users/kobed/Videos/Labeling/OUT.mp4")

print("camera opened")
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

print("starting read")

ret, frame = cap.read()
print("starting loop")

# Define the target resolution
target_width = 5120
target_height = 3072

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame.")
        break
    
    # Get the dimensions of the frame
    original_height, original_width, _ = frame.shape
    
    # Calculate scaling while maintaining the aspect ratio
    aspect_ratio = original_width / original_height
    if aspect_ratio > target_width / target_height:
        # Scale based on width, add black bars on top and bottom
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
        resized_frame = cv2.resize(frame, (new_width, new_height))
        top_padding = (target_height - new_height) // 2
        bottom_padding = target_height - new_height - top_padding
        padded_frame = cv2.copyMakeBorder(
            resized_frame, top_padding, bottom_padding, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )
    else:
        # Scale based on height, add black bars on left and right
        new_height = target_height
        new_width = int(target_height * aspect_ratio)
        resized_frame = cv2.resize(frame, (new_width, new_height))
        left_padding = (target_width - new_width) // 2
        right_padding = target_width - new_width - left_padding
        padded_frame = cv2.copyMakeBorder(
            resized_frame, 0, 0, left_padding, right_padding, cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )

    # Scale down the frame by 2x without changing the aspect ratio
    downscaled_frame = cv2.resize(padded_frame, (target_width // 5, target_height // 5))
    
    # Update dimensions after resizing
    height, width, _ = downscaled_frame.shape
    frame_width = width // 4
    frame_height = height // 3

    # Create a blank canvas for displaying frames
    new_frame = downscaled_frame.copy()

    # Show each frame
    for i in range(3):
        for j in range(4):
            x = j * frame_width
            y = i * frame_height
            # Extract the sub-frame
            sub_frame = downscaled_frame[y:y+frame_height, x:x+frame_width]
            new_frame[y:y+frame_height, x:x+frame_width] = sub_frame
            cv2.imshow(f"Frame {i*4+j+1}", sub_frame)

    # Wait briefly to refresh frames
    if cv2.waitKey(16) == 27:  # Check if the escape key is pressed
        break
    
cap.release()
cv2.destroyAllWindows()
