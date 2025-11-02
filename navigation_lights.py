#!/usr/bin/env python3

import time

from trilobot import BUTTON_A, Trilobot

"""
Navigates forward until an object is detected at 30cm or less, then:
1. Stops and shows red (object detected)
2. Reverses approximately 1cm
3. Turns right 90 degrees (yellow during turn)
4. Continues forward (green)

Also reverses if an invalid distance reading is detected (too close to measure).

LED Colors:
- Green: Moving forward
- Yellow: Turning
- Red: Object detected (30cm or less) or invalid reading

Stop the example by pressing button A.
"""
print("Trilobot Example: Navigate with Obstacle Avoidance\n")

# Distance threshold for obstacle detection (in cm)
OBSTACLE_THRESHOLD = 30.0

# Movement speeds
FORWARD_SPEED = 0.6
REVERSE_SPEED = 0.4
TURN_SPEED = 0.5

# Time estimates for movements (may need calibration)
REVERSE_TIME = 0.15  # Time to reverse ~1cm at REVERSE_SPEED
TURN_TIME = 0.65     # Time to turn ~90 degrees at TURN_SPEED

# Define colors
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

tbot = Trilobot()

print("Starting navigation... Press Button A to exit.\n")
print("Moving forward (green)...\n")

# Set initial state - moving forward with green lights
tbot.fill_underlighting(GREEN)
tbot.forward(FORWARD_SPEED)

while not tbot.read_button(BUTTON_A):
    # Read the distance from the sensor
    distance = tbot.read_distance()
    
    # Check if we have a valid distance reading
    if distance >= 0.0:
        print(f"Distance: {distance:.1f} cm")
        
        # Check if object is too close
        if distance <= OBSTACLE_THRESHOLD:
            print(f"⚠ OBSTACLE DETECTED at {distance:.1f} cm!")
            
            # Stop and show red
            tbot.stop()
            tbot.fill_underlighting(RED)
            time.sleep(0.5)  # Brief pause to show red
            
            print("Reversing 1cm...")
            # Reverse approximately 1cm
            tbot.backward(REVERSE_SPEED)
            time.sleep(REVERSE_TIME)
            
            print("Turning right 90 degrees...")
            # Turn right 90 degrees with yellow lights
            tbot.fill_underlighting(YELLOW)
            tbot.turn_right(TURN_SPEED)
            time.sleep(TURN_TIME)
            
            # Resume forward movement with green lights
            print("Resuming forward movement (green)...\n")
            tbot.fill_underlighting(GREEN)
            tbot.forward(FORWARD_SPEED)
    else:
        # Invalid distance reading (too close to measure)
        print("⚠ INVALID DISTANCE READING - Object too close!")
        
        # Stop and show red
        tbot.stop()
        tbot.fill_underlighting(RED)
        time.sleep(0.5)  # Brief pause to show red
        
        print("Reversing 1cm...")
        # Reverse approximately 1cm
        tbot.backward(REVERSE_SPEED)
        time.sleep(REVERSE_TIME)
        
        print("Turning right 90 degrees...")
        # Turn right 90 degrees with yellow lights
        tbot.fill_underlighting(YELLOW)
        tbot.turn_right(TURN_SPEED)
        time.sleep(TURN_TIME)
        
        # Resume forward movement with green lights
        print("Resuming forward movement (green)...\n")
        tbot.fill_underlighting(GREEN)
        tbot.forward(FORWARD_SPEED)
    
    # No sleep needed - distance sensor provides its own delay

# Clean up when exiting
tbot.stop()
tbot.clear_underlighting()
print("\nExiting...")
