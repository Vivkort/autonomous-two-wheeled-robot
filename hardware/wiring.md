# Wiring Notes

## Power architecture
Keep "dirty" motor power and "clean" logic power separate but sharing a common ground.

```
Battery (3S ~11.1V) --+-- inline fuse --+--> Motor driver (VM) --> motors
                                        `--> Buck converter (5V/5A) --> Jetson
All grounds tied together (battery, driver, buck, MCU, Jetson).
```

## ESP32 <-> TB6612FNG motor driver
| ESP32 | TB6612 | Purpose |
|---|---|---|
| PWM pin A | PWMA | left motor speed |
| GPIO, GPIO | AIN1, AIN2 | left motor direction |
| PWM pin B | PWMB | right motor speed |
| GPIO, GPIO | BIN1, BIN2 | right motor direction |
| 3V3 | STBY | enable (pull high) |
| GND | GND | common ground |

## Encoders -> ESP32
Each motor: channel A + channel B to interrupt-capable GPIO pins. Count ticks in ISR; A-vs-B phase = direction.

## Sensors
- RPLidar C1 -> Jetson USB (via included adapter)
- OAK-D Lite -> Jetson USB 3.0
- BNO055 IMU -> I2C (SDA/SCL) on Jetson or ESP32
- ESP32 -> Jetson USB (micro-ROS transport)

> Fill in exact GPIO pin numbers once hardware is in hand.
