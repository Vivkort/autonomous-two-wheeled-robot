# Milestone — Full Autonomy in Simulation

**Reached:** July 2026
**Robot:** Craig (a differential-drive rover)

Craig can now **map an unknown space and navigate it autonomously**, entirely in simulation. This is the complete "sense → map → localize → plan → act" loop of an autonomous mobile robot — and every piece was built and debugged from scratch.

## What Craig can do

- **Exist as a physics body.** A URDF-modeled robot — chassis, two driven wheels, a caster, a lidar — with mass, collision, and inertia, standing and driving under gravity in Gazebo.
- **Drive on command.** A differential-drive plugin turns `/cmd_vel` velocity messages into wheel motion. The same `Twist` message used since the turtlesim days.
- **See.** A simulated 360° lidar publishes `/scan`, detecting walls and obstacles out to 12 m.
- **Know where it is.** Wheel odometry flows through the tf tree (`map → odom → base_link → lidar`), so the system always knows how far Craig has moved.
- **Build a map.** `slam_toolbox` stitches lidar scans into a live occupancy-grid map of a room it has never seen, correcting drift with loop closure.
- **Navigate itself.** Nav2 takes a clicked goal, plans a path around the mapped obstacles, and drives Craig there — slowing near walls, routing around the box and cylinder, stopping at the target.

## How it's wired

```
teleop / Nav2 ── /cmd_vel ──► ros_gz bridge ──► Gazebo diff-drive ──► wheels
Gazebo lidar ── /scan ──────► ros_gz bridge ──► slam_toolbox ──► /map
Gazebo odom  ── /tf ────────► ros_gz bridge ──► tf tree
robot_state_publisher ─────► tf (base_link → lidar, wheels)
slam_toolbox ──────────────► map → odom (localization)
Nav2 (costmaps + planner + controller) ──► /cmd_vel
```

All of it comes up with one command: `ros2 launch ~/craig_sim.launch.py` (see `run_sim.md`), plus `slam_toolbox` and `nav2_bringup`.

## Key files

- `urdf/my_robot.urdf` — Craig's body + Gazebo plugins (diff-drive, lidar sensor)
- `worlds/sensor_world.sdf` — the walled test room with obstacles
- `launch/craig_sim.launch.py` — full bringup (Gazebo, robot_state_publisher, spawn, bridges, RViz)
- `config/slam_params.yaml` — slam_toolbox tuned for Craig (base_frame = base_link)
- `config/nav2_params.yaml` — the Nav2 stack config

## Lessons banked along the way

- URDF: links + joints, and why fixed vs continuous joints matter for tf
- Physics needs mass (inertial) + collision, not just visuals
- ROS and Gazebo are separate worlds joined by the `ros_gz` bridge
- SLAM needs a clean `odom → base_link` tf, or it's blind to motion
- Nav2 is config-heavy: every node in the launch needs its params section
- Debugging tells: `~` doesn't expand mid-argument (use `$HOME`); check the node's terminal for the real error; a wall of `.inf` is a *healthy* scan

## Why it matters

None of this is throwaway. When the real hardware (RPLidar C1, OAK-D Lite, compute board, motors) is assembled, this exact ROS 2 stack drives the physical robot. Gazebo's plugins get swapped for real drivers; the URDF, SLAM, and Nav2 configuration stay the same. The brain is built — the body just plugs in.

**Next:** integrate the depth camera in sim, then begin the hardware build.
