# Bill of Materials — Phase 1 (Wheeled Rover)

Prices are approximate Amazon US street prices, mid-2026. Update the "Bought" column as you order.

| Part | Purpose | ~Price | Bought? | Link/notes |
|---|---|---|---|---|
| NVIDIA Jetson Orin Nano Super Dev Kit | Main compute (the brain) | $500 | [ ] | Or repurpose an Nvidia-GPU laptop for early phases |
| NVMe SSD 256 GB (M.2 2280) | OS + storage | $30 | [ ] | Jetson boots better from SSD than SD |
| Slamtec RPLidar C1 | 360 deg 2D lidar (SLAM) | $100 | [ ] | USB via included serial adapter |
| Luxonis OAK-D Lite | Depth camera (3D obstacles + future AI) | $149 | [ ] | USB 3.0; on-camera AI |
| 2x DC gear motors w/ quadrature encoders | Drive + odometry | $30 | [ ] | ENCODERS REQUIRED |
| TB6612FNG motor driver | Dual H-bridge amplifier | $8 | [ ] | Prefer over L298N |
| ESP32 dev board | Real-time motor/encoder MCU | $10 | [ ] | Runs micro-ROS |
| BNO055 IMU | Orientation / sensor fusion | $25 | [ ] | On-chip fusion; I2C. Skippable if using RealSense IMU |
| 3S LiPo battery + charger | Power | $45 | [ ] | Or 12V pack |
| Buck converter 5V / 5A | Clean power for the Jetson | $10 | [ ] | Dedicated rail, not shared with motors |
| Caster wheel + drive wheels/hubs | Rolling | $15 | [ ] | |
| Wiring, standoffs, switch, inline fuse | Assembly | $20 | [ ] | Fuse on the battery! |
| Chassis | Body | 3D-printed | [ ] | Your filament; design in `urdf/` |
| **Total** | | **~$942** | | |

## Notes
- Swapping OAK-D Lite for an Intel RealSense D435i (~$300-350) raises the total but its built-in IMU lets you drop the BNO055.
- For Phases 1-3 you can prototype on a repurposed laptop (Ubuntu + ROS 2) and defer the Jetson until Phase 5.
