import cv2
import time
import imagezmq
import socket

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
sender = imagezmq.ImageSender(connect_to='tcp://192.168.137.210:5555')
rpi_name = socket.gethostname() # send RPi hostname with each image
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame.")
        break
    sender.send_image(rpi_name, frame)
    
cap.release()
cv2.destroyAllWindows()
