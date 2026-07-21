#!/usr/bin/env bash
# Publishes base_link -> imu_link / lidar_link as static TF, and /robot_description.
exec ros2 run robot_state_publisher robot_state_publisher "$HOME/balancer.urdf" \
  --ros-args -p use_sim_time:=true
