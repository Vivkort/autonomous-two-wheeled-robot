# Running Craig in Gazebo — Quick Start

How to launch the full simulation from scratch. Run each command in its **own** Ubuntu/WSL terminal (ROS 2 is auto-sourced via `~/.bashrc`).

## The launch sequence

**1. Start the Gazebo world**
```bash
gz sim empty.sdf
```
Opens an empty physics world. If it starts paused, click the ▶ play button (bottom-left).

**2. Spawn Craig into the world**
```bash
ros2 run ros_gz_sim create -file "$HOME/my_robot.urdf" -name craig -z 0.1
```
Adds Craig to the running world. `-z 0.1` drops him from just above the ground so he settles onto his wheels.
(`$HOME/my_robot.urdf` is a symlink to `urdf/my_robot.urdf` — used because the real path has a space in "Engineering Projects" that breaks some tools.)

**3. Start the ROS ↔ Gazebo bridge**
```bash
ros2 run ros_gz_bridge parameter_bridge /cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
```
Connects ROS's `/cmd_vel` to Gazebo's `/cmd_vel` so control nodes can drive the sim robot.

**4. Drive him (keyboard teleop)**
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
Click into THIS terminal, then use the keys it lists: `i` forward, `,` backward, `j` / `l` turn, `k` stop.

## Gotchas (in order of how often they bite)
- **Gazebo must be running before you spawn** (step 1 before step 2).
- **The sim must be PLAYING** (▶) — a paused sim ignores all commands.
- **The teleop terminal must have keyboard focus** — click it before pressing keys.
- If Craig doesn't move: check the ROS side is publishing (`ros2 topic echo /cmd_vel` while pressing keys) and the Gazebo topic name (`gz topic -l | grep cmd_vel`).

## Re-running after editing the URDF
Because `$HOME/my_robot.urdf` is a symlink, any edits you save to `urdf/my_robot.urdf` are picked up automatically — just re-run the spawn command (step 2) in the already-running world, or restart from step 1 for a clean slate.

## Later: one-command launch
This four-terminal dance can be wrapped into a single ROS 2 **launch file** (`ros2 launch ...`) that starts Gazebo, spawns Craig, and runs the bridge together. Worth doing once the setup stabilizes.
