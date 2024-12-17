import requests
import cv2
import numpy as np
from collections import deque

# Number of streams
num_streams = 12
stream_urls = [f"http://127.0.0.1:4012/video_feed/{i}" for i in range(num_streams)]
buffers = {i: deque(maxlen=10) for i in range(num_streams)}

def parse_headers_and_frame(response_chunk):
    # Split HTTP headers and the image data
    header_end = response_chunk.find(b'\r\n\r\n')
    if header_end == -1:
        return None, None

    headers = response_chunk[:header_end].decode('utf-8').split('\r\n')
    body = response_chunk[header_end + 4:]
    
    # Extract timestamp
    timestamp = None
    for header in headers:
        if header.startswith("X-Timestamp:"):
            timestamp = float(header.split(": ")[1])
            break
    
    return timestamp, body

def fetch_stream(stream_id, url):
    stream = requests.get(url, stream=True)
    stream_buffer = b""
    for chunk in stream.iter_content(chunk_size=4096):
        stream_buffer += chunk
        while b'\r\n--frame\r\n' in stream_buffer:
            # Split the stream into individual frames
            frame_start = stream_buffer.find(b'\r\n--frame\r\n')
            frame_end = stream_buffer.find(b'\r\n--frame\r\n', frame_start + 1)
            if frame_end == -1:
                break
            
            frame_data = stream_buffer[frame_start:frame_end]
            stream_buffer = stream_buffer[frame_end:]
            
            timestamp, frame_body = parse_headers_and_frame(frame_data)
            if timestamp is not None and frame_body:
                # Decode the frame
                frame = cv2.imdecode(np.frombuffer(frame_body, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is not None:
                    buffers[stream_id].append((timestamp, frame))

# Start fetching streams
import threading
threads = []
for i, url in enumerate(stream_urls):
    thread = threading.Thread(target=fetch_stream, args=(i, url), daemon=True)
    threads.append(thread)
    thread.start()

# Synchronize and display frames
while True:
    timestamps = []
    for i in range(num_streams):
        if buffers[i]:
            timestamps.append(buffers[i][0][0])

    if len(timestamps) == num_streams:
        target_timestamp = max(timestamps) - 0.01  # 10ms tolerance
        for i in range(num_streams):
            while buffers[i] and buffers[i][0][0] < target_timestamp:
                buffers[i].popleft()  # Drop outdated frames
            
            if buffers[i]:
                _, frame = buffers[i][0]
                cv2.imshow(f"Stream {i}", frame)
    
    if cv2.waitKey(1) == 27:  # Escape key
        break

cv2.destroyAllWindows()
