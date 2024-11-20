import cv2
import time

print("starting")

# Open the video capture
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# Uncomment below line to use a video file instead of webcam
# cap = cv2.VideoCapture("C:/Users/kobed/Videos/Labeling/OUT.mp4")

print("camera opened")
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# GStreamer RTSP pipeline
# Configure this pipeline to fit your desired RTSP server IP and port
gst_pipeline = (
    "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast "
    "! rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5000"
)

# Initialize GStreamer writer
out = cv2.VideoWriter(gst_pipeline, cv2.CAP_GSTREAMER, 0, 30.0, (640, 480))

if not out.isOpened():
    print("Error: Unable to open GStreamer pipeline for writing.")
    exit()

print("starting read and stream loop")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # Write frame to GStreamer pipeline
    out.write(frame)

    # Display the frame (optional, useful for debugging)
    cv2.imshow("RTSP Streaming", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()
print("Streaming stopped and resources released.")
