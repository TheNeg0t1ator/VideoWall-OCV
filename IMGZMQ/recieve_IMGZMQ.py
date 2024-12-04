import cv2
import imagezmq

# Initialize ImageHub
image_hub = imagezmq.ImageHub()

# Define screen dimensions
screen_width = 1280  # Replace with your screen width
screen_height = 1024  # Replace with your screen height

# Create a fullscreen window
window_name = "Image Stream"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:  # Show streamed images until Ctrl-C
    rpi_name, image = image_hub.recv_image()
    
    # Resize the image to fit the screen
    image = cv2.resize(image, (screen_width, screen_height), interpolation=cv2.INTER_AREA)
    
    # Display the image
    cv2.imshow(window_name, image)
    cv2.waitKey(1)
    
    # Send acknowledgment to RPi
    image_hub.send_reply(b'OK')