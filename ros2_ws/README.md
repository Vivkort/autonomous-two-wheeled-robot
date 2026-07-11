# ROS 2 Workspace

The ROS 2 side of the robot. This is a colcon workspace; your packages live under `src/`.

## Structure (once populated)
```
ros2_ws/
`-- src/
    `-- my_robot/
        |-- launch/      # launch files that start the whole graph
        |-- config/      # Nav2 params, EKF params, costmap config
        |-- description/ # (or link to /urdf)
        `-- my_robot/    # Python/C++ nodes
```

## Build & run
```
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch my_robot bringup.launch.py
```

## Planned launch files
- `bringup.launch.py` — start drivers (lidar, camera, micro-ROS agent, IMU)
- `slam.launch.py` — slam_toolbox mapping
- `nav.launch.py` — Nav2 navigation
- `localization.launch.py` — robot_localization EKF

## Key dependencies
`slam_toolbox`, `nav2_bringup`, `robot_localization`, `micro_ros_agent`, RPLidar + depthai (OAK-D) ROS 2 drivers.

> Placeholder — packages to be added during Phase 1.
