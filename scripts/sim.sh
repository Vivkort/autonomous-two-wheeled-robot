#!/usr/bin/env bash
# One command to bring up the whole craig2 SLAM stack.
#   bash scripts/sim.sh            -> mapping stack
#   bash scripts/sim.sh nav2:=true -> + Nav2
# Everything lands in ONE terminal. When a node misbehaves and you need its
# output isolated, fall back to the single-node scripts (bridge.sh, etc).
cd "$(dirname "$0")/.." || exit 1
source install/setup.bash
exec ros2 launch launch/craig2_sim.launch.py "$@"
