#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:="$ROOT/config/slam_params.yaml" \
  use_sim_time:=true
