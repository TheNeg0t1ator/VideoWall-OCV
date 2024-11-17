import cv2

# Number of streams
num_streams = 12
streams = []

# Open each video stream
for i in range(num_streams):
    cap = cv2.VideoCapture(f"http://127.0.0.1:4012/video_feed/{i}")
    if not cap.isOpened():
        print(f"Error: Could not open video stream {i}.")
        continue
    streams.append((i, cap))

while True:
    for i, cap in streams:
        ret, frame = cap.read()
        if not ret:
            print(f"Stream {i} lost connection.")
            continue

        # Display each stream in its own window
        cv2.imshow(f"Stream {i}", frame)
    
    # Break the loop if the Escape key is pressed
    if cv2.waitKey(100) == 27:  # Escape key
        break

# Release all streams and destroy windows
for _, cap in streams:
    cap.release()
cv2.destroyAllWindows()
