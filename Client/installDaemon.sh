#!/bin/bash

# Variables
SERVICE_NAME="StreamClient"
DESKTOP_PATH="/home/pxl/Desktop"
PYTHON_FILE="$DESKTOP_PATH/client.py"
SCRIPT_FILE="$DESKTOP_PATH/client.sh"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

pip install cv2 --break-system-packages
pip install imagezmq --break-system-packages

# Create the Python file
cat > "$PYTHON_FILE" <<EOL
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
print("configured.... start recieving")
while True:  # Show streamed images until Ctrl-C
    rpi_name, compressed_frame = image_hub.recv_image()
    # Resize the image to fit the screen
    decompressed_frame = cv2.resize(compressed_frame, (screen_width, screen_height), interpolation=cv2.INTER_AREA)
    
    # Display the image
    cv2.imshow(window_name, decompressed_frame)
    cv2.waitKey(1)
    
    # Send acknowledgment to RPi
    image_hub.send_reply(b'OK')
EOL

# Create the shell script file
cat > "$SCRIPT_FILE" <<EOL
#!/bin/bash
DISPLAY=:0 sudo -u pxl python3 $PYTHON_FILE
EOL

# Make the shell script executable
chmod +x "$SCRIPT_FILE"

# Check if the script exists
if [ ! -f "$SCRIPT_FILE" ]; then
    echo "Error: Script $SCRIPT_FILE does not exist."
    exit 1
fi

# Create systemd service file
echo "Creating systemd service file at $SERVICE_FILE"
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Service to run $SCRIPT_FILE
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/bin/bash $SCRIPT_FILE
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

# Enable and start the service
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

# Check the status of the service
sudo systemctl status "$SERVICE_NAME"

# now reboot the system for it to take effect
sudo reboot
