# URDF — Robot Description

A URDF (Unified Robot Description Format) file is an XML description of the robot's body: its **links** (rigid parts) and **joints** (how they connect and where sensors sit). ROS uses it to know exactly where each sensor is relative to the robot's center, so sensor data lands in the right place on the map.

## What goes here
- `robot.urdf.xacro` — the main description (use xacro macros to keep it clean)
- meshes/ — optional STL exports of your 3D-printed chassis parts for visualization

## Key frames to define
- `base_link` — the robot's center/origin (everything is measured from here)
- `left_wheel`, `right_wheel`, `caster` — the drive links
- `lidar_link` — position of the RPLidar (e.g. x=0.05, z=0.10 from base_link)
- `camera_link` — position of the OAK-D Lite (front-facing)
- `imu_link` — position of the BNO055

## Tip
Because you're 3D-printing the chassis, take the exact mounting offsets from your CAD model and put them straight into the URDF. Accurate offsets = accurate maps.

Visualize with:
```
ros2 launch <your_pkg> display.launch.py   # opens RViz with the robot model
```
