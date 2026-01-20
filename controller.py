#!/usr/bin/env python3

import pygame
import threading
import io
import time
from flask import Flask, Response
from picamera2 import Picamera2
from trilobot import Trilobot, LIGHT_FRONT_LEFT, LIGHT_FRONT_RIGHT, LIGHT_MIDDLE_LEFT, LIGHT_MIDDLE_RIGHT, LIGHT_REAR_LEFT, LIGHT_REAR_RIGHT

"""
Control Trilobot with an 8BitDo Pro 2 Bluetooth controller.
- Left stick: Control movement (forward/backward/turn)
- A button: Purple LEDs
- B button: Teal LEDs
- X button: Pink LEDs
- Y button: Orange LEDs
- LEDs indicate distance: green (>100cm), yellow (30-100cm), red (<=30cm)

Camera stream available at http://<raspberry_pi_ip>:5000

Make sure your controller is paired via Bluetooth before running.
"""

# Flask app for camera streaming
app = Flask(__name__)

# Initialize camera
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(camera_config)
picam2.start()

def generate_frames():
    """Generator function that yields MJPEG frames."""
    while True:
        # Capture frame as JPEG
        stream = io.BytesIO()
        picam2.capture_file(stream, format='jpeg')
        stream.seek(0)
        frame = stream.read()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Main page with embedded video stream."""
    return '''
    <html>
    <head>
        <title>Trilobot Camera</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                background-color: #1a1a2e; 
                color: white; 
                margin: 0; 
                padding: 20px;
            }
            h1 { color: #00d4ff; }
            img { 
                max-width: 100%; 
                border: 3px solid #00d4ff; 
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <h1>Trilobot Camera Stream</h1>
        <img src="/video_feed" />
    </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def run_webserver():
    """Run Flask server in a separate thread."""
    app.run(host='0.0.0.0', port=5000, threaded=True, use_reloader=False)

print("Trilobot Controller Control\n")
print("Camera stream available at http://<your_pi_ip>:5000\n")

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()

# Wait for controller connection
if pygame.joystick.get_count() == 0:
    print("No controller detected. Please connect your 8BitDo Pro 2 controller.")
    exit()

controller = pygame.joystick.Joystick(0)
controller.init()
print(f"Connected to: {controller.get_name()}")

# Start the camera webserver in a background thread
webserver_thread = threading.Thread(target=run_webserver, daemon=True)
webserver_thread.start()

tbot = Trilobot()

# Constants
DEADZONE = 0.15  # Ignore small stick movements
MAX_SPEED = 1.0
DISTANCE_READ_INTERVAL = 0.1  # Read distance every 100ms to avoid GPIO issues

# Distance thresholds with hysteresis to prevent flickering
# To change from green to yellow, must go below 95cm
# To change from yellow to green, must go above 105cm
THRESHOLD_FAR = 100
THRESHOLD_NEAR = 30
HYSTERESIS = 5  # Buffer zone around thresholds

# Distance tracking
last_distance_read = 0
cached_distance = 100  # Default distance
current_color_state = 'green'  # Track current state: 'green', 'yellow', 'red'

try:
    running = True
    while running:
        pygame.event.pump()
        
        # Read left stick axes (axis 0 = horizontal, axis 1 = vertical)
        left_x = controller.get_axis(0)  # Left/right
        left_y = -controller.get_axis(1)  # Forward/backward (inverted)
        
        # Apply deadzone
        if abs(left_x) < DEADZONE:
            left_x = 0
        if abs(left_y) < DEADZONE:
            left_y = 0
        
        # Calculate motor speeds (differential drive)
        if left_y == 0 and left_x == 0:
            tbot.stop()
        else:
            # Combine forward/back with turning
            left_speed = (left_y + left_x) * MAX_SPEED
            right_speed = (left_y - left_x) * MAX_SPEED
            
            # Clamp speeds to [-1, 1]
            left_speed = max(-1, min(1, left_speed))
            right_speed = max(-1, min(1, right_speed))
            
            tbot.set_left_speed(left_speed)
            tbot.set_right_speed(right_speed)
        
        # Read distance at a slower rate to avoid GPIO issues
        current_time = time.time()
        if current_time - last_distance_read >= DISTANCE_READ_INTERVAL:
            try:
                cached_distance = tbot.read_distance()
                last_distance_read = current_time
                print(f"Distance: {cached_distance:.1f}cm | State: {current_color_state}", end='\r')
            except Exception as e:
                print(f"Distance read error: {e}", end='\r')
        
        # Set LED color based on button or distance (with hysteresis)
        if controller.get_button(0):  # A button = purple
            color = (0, 128, 128)
        elif controller.get_button(1):  # B button = teal
            color = (128, 0, 128)
        elif controller.get_button(2):  # X button = pink
            color = (255, 165, 0)
        elif controller.get_button(3):  # Y button = orange
            color = (255, 105, 180)
        else:
            # Apply hysteresis to prevent flickering at thresholds
            if current_color_state == 'green':
                if cached_distance <= THRESHOLD_NEAR - HYSTERESIS:
                    current_color_state = 'red'
                elif cached_distance <= THRESHOLD_FAR - HYSTERESIS:
                    current_color_state = 'yellow'
            elif current_color_state == 'yellow':
                if cached_distance <= THRESHOLD_NEAR - HYSTERESIS:
                    current_color_state = 'red'
                elif cached_distance > THRESHOLD_FAR + HYSTERESIS:
                    current_color_state = 'green'
            elif current_color_state == 'red':
                if cached_distance > THRESHOLD_FAR + HYSTERESIS:
                    current_color_state = 'green'
                elif cached_distance > THRESHOLD_NEAR + HYSTERESIS:
                    current_color_state = 'yellow'
            
            if current_color_state == 'red':
                color = (255, 0, 0)
            elif current_color_state == 'yellow':
                color = (255, 255, 0)
            else:
                color = (0, 255, 0)
        
        tbot.set_underlight(LIGHT_FRONT_LEFT, color)
        tbot.set_underlight(LIGHT_FRONT_RIGHT, color)
        tbot.set_underlight(LIGHT_MIDDLE_LEFT, color)
        tbot.set_underlight(LIGHT_MIDDLE_RIGHT, color)
        tbot.set_underlight(LIGHT_REAR_LEFT, color)
        tbot.set_underlight(LIGHT_REAR_RIGHT, color)
        
        pygame.time.wait(20)  # Small delay for ~50Hz update rate

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    tbot.stop()
    tbot.clear_underlighting()
    picam2.stop()
    pygame.quit()
