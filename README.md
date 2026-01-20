# Trilobot Control Scripts

Python scripts for controlling the Pimoroni Trilobot robot on Raspberry Pi.

## Scripts

### controller.py

A Bluetooth controller interface for the Trilobot with live camera streaming.

**Features:**
- Control movement using an 8BitDo Pro 2 Bluetooth controller (left stick)
- Live MJPEG camera stream via Flask web server (port 5000)
- Distance-based LED indicators with hysteresis:
  - 🟢 Green: >100cm (clear)
  - 🟡 Yellow: 30-100cm (caution)
  - 🔴 Red: ≤30cm (obstacle)
- Button-activated LED colors:
  - A: Purple
  - B: Teal
  - X: Pink
  - Y: Orange

**Usage:**
```bash
# Pair your 8BitDo Pro 2 controller via Bluetooth first
python3 controller.py
```

Access the camera stream at: `http://<raspberry_pi_ip>:5000`

---

### navigation_lights.py

An autonomous obstacle avoidance script that navigates the Trilobot forward and automatically avoids obstacles.

**Features:**
- Moves forward until an obstacle is detected (≤30cm)
- On obstacle detection:
  1. Stops and displays red LEDs
  2. Reverses approximately 1cm
  3. Turns right 90 degrees (yellow LEDs)
  4. Resumes forward movement (green LEDs)
- Handles invalid distance readings (objects too close to measure)
- Press Button A to stop

**Usage:**
```bash
python3 navigation_lights.py
```

**LED Color Guide:**
- 🟢 Green: Moving forward
- 🟡 Yellow: Turning
- 🔴 Red: Obstacle detected

---

## Requirements

Install dependencies with:
```bash
pip install -r requirements.txt
```

**Note:** The `trilobot` library should be installed via Pimoroni's installer script. The `picamera2` library is typically pre-installed on Raspberry Pi OS.

## Hardware

- Raspberry Pi (with camera module for controller.py)
- [Pimoroni Trilobot](https://shop.pimoroni.com/products/trilobot)
- 8BitDo Pro 2 Bluetooth controller (for controller.py)

## License

See [LICENSE](LICENSE) for details.