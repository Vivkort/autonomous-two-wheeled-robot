# ESP32 Motor Controller (micro-ROS)

Real-time firmware: the "cerebellum". Subscribes to wheel velocity commands from the Jetson and publishes wheel odometry from the encoders.

## Responsibilities
1. Receive target wheel speeds (via micro-ROS, subscribed topic).
2. Run a PID loop per wheel: compare target speed to encoder-measured speed, output PWM to the TB6612.
3. Count encoder ticks with hardware interrupts (never miss a pulse).
4. Publish odometry (tick counts / wheel velocities) back to the Jetson.

## Toolchain
- PlatformIO or Arduino IDE
- micro-ROS for Arduino (transport: USB serial to the Jetson)

## Files (to add)
- `src/main.cpp` — the firmware
- `platformio.ini` — build config

## Interface (ROS topics)
- Subscribes: `cmd_wheels` (or standard `cmd_vel` if doing diff-drive math on-board)
- Publishes: `wheel_odom` / encoder ticks

> Placeholder — firmware to be written once motors + encoders are in hand.
