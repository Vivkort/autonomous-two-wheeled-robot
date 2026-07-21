#!/usr/bin/env bash
# Stand craig2 back up after a fall WITHOUT restarting the whole stack.
# Removes the fallen model and respawns a fresh one (zero velocity, upright).
# Gazebo, bridge, SLAM, scan_gate and RViz keep running; SLAM keeps its map.
#
# NOTE: this resets odometry to zero, so the balance controller's integrator
# and target_pos are now stale. Restart the controller after this:
#     Ctrl+C in the controller terminal, then  bash scripts/controller.sh
#
# World name is baked into the remove service path - change it if you switch worlds.
WORLD=sensor_world

echo "removing craig2..."
gz service -s /world/$WORLD/remove \
  --reqtype gz.msgs.Entity --reptype gz.msgs.Boolean --timeout 3000 \
  --req 'name: "craig2", type: MODEL'

sleep 1

echo "respawning craig2 upright at z=0.08..."
ros2 run ros_gz_sim create -file "$HOME/balancer.urdf" -name craig2 -z 0.08

echo "done. Now restart the controller for a clean integrator state:"
echo "    Ctrl+C the controller terminal, then  bash scripts/controller.sh"
