from flask import Flask, Response, render_template_string
import cv2
import threading

# Define target resolution
target_width = 5120
target_height = 3072

# Open the video stream
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap = cv2.VideoCapture("C:/Users/kobed/Videos/Content-warning.mp4", cv2.CAP_FFMPEG)
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

print("Video opened and streaming started.")

# Resize and split frames into smaller pieces
def process_frame(frame):
    original_height, original_width, _ = frame.shape
    aspect_ratio = original_width / original_height

    if aspect_ratio > target_width / target_height:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
        resized_frame = cv2.resize(frame, (new_width, new_height))
        top_padding = (target_height - new_height) // 2
        bottom_padding = target_height - new_height - top_padding
        padded_frame = cv2.copyMakeBorder(
            resized_frame, top_padding, bottom_padding, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )
    else:
        new_height = target_height
        new_width = int(target_height * aspect_ratio)
        resized_frame = cv2.resize(frame, (new_width, new_height))
        left_padding = (target_width - new_width) // 2
        right_padding = target_width - new_width - left_padding
        padded_frame = cv2.copyMakeBorder(
            resized_frame, 0, 0, left_padding, right_padding, cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )

    # Scale down the frame
    downscaled_frame = cv2.resize(padded_frame, (target_width // 5, target_height // 5))
    return downscaled_frame

# Generate frames for each video feed
def generate_frame(frame_number):
    while True:
        ret, frame = cap.read()  # Read a new frame from the camera
        if not ret:
            print("Error: Failed to read frame.")
            break
            
        downscaled_frame = process_frame(frame)

        # Split the downscaled frame into smaller segments
        height, width, _ = downscaled_frame.shape
        frame_width = width // 4
        frame_height = height // 3
        x_offset = (frame_number % 4) * frame_width
        y_offset = (frame_number // 4) * frame_height
        sub_frame = downscaled_frame[y_offset:y_offset+frame_height, x_offset:x_offset+frame_width]
        ret, buffer = cv2.imencode('.jpg', sub_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# Create a single Flask app to handle all video streams
app = Flask(__name__)

@app.route('/video_feed/<int:frame_number>')
def video_feed(frame_number):
    return Response(generate_frame(frame_number), mimetype='multipart/x-mixed-replace; boundary=frame')

# HTML template to display all streams in a 4x3 grid
@app.route('/')
def index():
    # Create a grid of 12 streams
    streams_html = ""
    for i in range(12):
        streams_html += f'''
        <div style="display:inline-block; margin: 10px;">
            <h3>Stream {i+1}</h3>
            <img src="/video_feed/{i}" width="720" height="480" />
        </div>
        '''

    return render_template_string(f'''
    <html>
    <head>
        <title>Video Streaming</title>
        <style>
            body {{ text-align: center; }}
            .grid-container {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                grid-template-rows: repeat(3, 1fr);
                gap: 10px;
                justify-items: center;
            }}
        </style>
    </head>
    <body>
        <h1>Multiple Video Streams</h1>
        <div class="grid-container">
            {streams_html}
        </div>
    </body>
    </html>
    ''')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4012, threaded=True, use_reloader=False)

# Release the video capture when done
cap.release()
cv2.destroyAllWindows()
