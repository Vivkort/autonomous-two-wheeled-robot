#!/usr/bin/env bash
# craig2 ros_gz bridge. One line, no interactive continuations to fight.
exec ros2 run ros_gz_bridge parameter_bridge \
  "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU" \
  "/model/craig2/joint/left_wheel_joint/cmd_force@std_msgs/msg/Float64]gz.msgs.Double" \
  "/model/craig2/joint/right_wheel_joint/cmd_force@std_msgs/msg/Float64]gz.msgs.Double" \
  "/model/craig2/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry" \
  "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan" \
  "/model/craig2/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V" \
  "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock" \
  --ros-args -r /model/craig2/tf:=/tf -r /model/craig2/odometry:=/odom
