import cv2
import time
import imagezmq
import socket
import yt_dlp
from Test_Examples.Compression.compressor import compress_frame as ImageCompressor
from concurrent.futures import ThreadPoolExecutor

def get_youtube_stream_url(youtube_url):
    ydl_opts = {
        'quiet': True,
        'format': 'best[ext=mp4]/best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        return info_dict['url']

print("starting")

youtube_url = "https://www.youtube.com/watch?v=rhvF2_JkDhQ"
stream_url = get_youtube_stream_url(youtube_url)
cap = cv2.VideoCapture(stream_url)
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap = cv2.VideoCapture("C:\\Users\\kobed\\Videos\\Content-warning.mp4")
# cap = cv2.VideoCapture("C:\\Users\\kobed\\Videos\\Max\\miami.mp4")

ips = [
    ['tcp://192.168.137.210:5555', 'tcp://192.168.137.119:5555', 'tcp://192.168.137.62:5555', 'tcp://192.168.137.141:5555'],
    ['tcp://192.168.137.151:5555', 'tcp://192.168.137.122:5555', 'tcp://192.168.137.108:5555', 'tcp://192.168.137.100:5555'],
    ['tcp://192.168.137.205:5555', 'tcp://192.168.137.56:5555', 'tcp://192.168.137.80:5555', 'tcp://192.168.137.144:5555']
]

# Create a 3x4 array of ImageSender instances
senders = [
    [imagezmq.ImageSender(connect_to=ip) for ip in row]
    for row in ips
]

rpi_name = socket.gethostname()  # Send RPi hostname with each image

print("camera opened")
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

print("starting read")

# Define the target resolution
target_width = 5120
target_height = 3072

# Global subframes array
global_subframes = [[None for _ in range(4)] for _ in range(3)]

# Function to send subframes
def send_subframe(i, j):
    senders[i][j].send_image(rpi_name, global_subframes[i][j])

with ThreadPoolExecutor(max_workers=12) as executor:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame.")
            break
        # capheight, capwidth, _ = frame.shape
        # print(capheight, capwidth)
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
        downscaled_frame = cv2.resize(padded_frame, (target_width // 4, target_height // 4))
        
        # Update dimensions after resizing
        height, width, _ = downscaled_frame.shape
        frame_width = width // 4
        frame_height = height // 3

        # Extract subframes and send them in separate threads
        for i in range(3):
            for j in range(4):
                x = j * frame_width
                y = i * frame_height
                global_subframes[i][j] = downscaled_frame[y:y+frame_height, x:x+frame_width]
                if (i == 0 and j in [0, 1, 2, 3]) or (i == 1 and j in [0, 1, 2, 3]) or (i == 2 and j in [0,2, 3]):
                    executor.submit(send_subframe, i, j)

cap.release()
cv2.destroyAllWindows()