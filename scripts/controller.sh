#!/usr/bin/env bash
# Workspace root is autonomous-robot/, NOT autonomous-robot/ros2_ws/.
cd "$(dirname "$0")/.." || exit 1
source install/setup.bash
exec ros2 run robot_intro balance_controller
