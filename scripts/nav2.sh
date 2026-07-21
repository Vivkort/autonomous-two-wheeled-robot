#!/usr/bin/env bash
# navigation_launch.py, NOT bringup_launch.py - bringup starts AMCL, which
# fights slam_toolbox for the map->odom transform.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec ros2 launch nav2_bringup navigation_launch.py \
  params_file:="$ROOT/config/nav2_params.yaml" \
  use_sim_time:=true
