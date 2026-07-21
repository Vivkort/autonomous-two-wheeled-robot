# Running the Self-Balancing Robot (craig2) in Sim

**Current architecture:** torque control + LQR full-state feedback, in a dedicated
`balance_world` with pinned physics.

## One-time setup (symlinks — skip if already done)
```bash
ln -sf "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/urdf/balancer.urdf" $HOME/balancer.urdf
ln -sf "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/worlds/balance_world.sdf" $HOME/balance_world.sdf
ln -sf "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/worlds/sensor_world.sdf" $HOME/sensor_world.sdf
```

## Launch scripts

The long commands live in `scripts/`, so there are no interactive backslash
continuations to fight. Run them from the project root:

| script | replaces |
|---|---|
| `bash scripts/bridge.sh` | the 7-topic parameter_bridge + both remaps |
| `bash scripts/state_pub.sh` | robot_state_publisher with sim time |
| `bash scripts/controller.sh` | `source install/setup.bash` + balance_controller |
| `bash scripts/slam.sh` | slam_toolbox with the right params path |
| `bash scripts/nav2.sh` | Nav2 `navigation_launch.py` with the right params path |

**Order matters:** Gazebo → spawn → bridge → state_pub → controller → **play** →
verify TF → slam → rviz → teleop. Starting slam_toolbox before TF exists is what
produced every confusing error in this file.

## Launch sequence — one command per Ubuntu terminal

**1. Gazebo world — DART (the default)**
```bash
gz sim ~/balance_world.sdf
```
> ⚠️ **Do NOT use `--physics-engine gz-physics-bullet-featherstone-plugin`.**
> Bullet-featherstone balances fine but **cannot steer** — it does not transmit
> differential wheel torque into yaw. Measured: 0.74 N·m of yaw moment held for
> 30 s produced *zero* rotation on craig2, and a minimal two-wheeled test rig
> managed 0.014° in four seconds against a predicted ~100 rad/s². Under DART the
> same rig spins freely.
>
> We originally moved to bullet-featherstone because DART's wheel contact
> chattered (wheel velocity reversing sign on 32–70% of samples). That turned out
> to be a **cylinder-on-plane line contact** problem, not a DART problem — once the
> wheel collisions became spheres, DART behaves perfectly. Both fixes were made,
> but the solver switch was never re-tested afterwards.
>
> `balance_world`, not `sensor_world`. No walls, no obstacles — nothing craig2 can
> collide with while drifting. A collision looks identical to a control failure in
> the logs. `sensor_world` is for SLAM/Nav2 work.

**2. Spawn craig2 — note `-z 0.08`**
```bash
ros2 run ros_gz_sim create -file $HOME/balancer.urdf -name craig2 -z 0.08
```
> **Spawn height must equal the wheel radius** (now 0.08 m) so he's set down exactly
> on the ground. Spawn higher and he's dropped, and the bounce is a disturbance at
> the start of every single run. If you change the wheel radius, change this too.

**3. Bridge — IMU + wheel torques + odometry + lidar + TF + clock**
```bash
ros2 run ros_gz_bridge parameter_bridge \
  "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU" \
  "/model/craig2/joint/left_wheel_joint/cmd_force@std_msgs/msg/Float64]gz.msgs.Double" \
  "/model/craig2/joint/right_wheel_joint/cmd_force@std_msgs/msg/Float64]gz.msgs.Double" \
  "/model/craig2/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry" \
  "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan" \
  "/model/craig2/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V" \
  "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock" \
  --ros-args -r /model/craig2/tf:=/tf
```
> The remap goes last, after every topic spec. Gazebo publishes the odom TF on
> `/model/craig2/tf`; the remap is what puts it on `/tf` where ROS looks for it.
>
> **Bridge `/clock` before starting anything with `use_sim_time:=true`.** A node set to
> sim time with no `/clock` blocks forever at t=0 and publishes nothing, silently. That
> failure looks identical to a missing-TF failure — don't stack the two.
>
> The lidar also needs `gz-sim-sensors-system` in the world file, or the sensor loads
> silently and `/scan` never publishes.
> **Odometry, not JointState.** `JointState` carries a list of joint-name strings;
> deserialising those in Python at ~700 Hz starved the control loop down to 10 Hz
> while the IMU was publishing at 222. `JointStatePublisher` also ignores
> `<update_rate>`, so it can't be capped. Odometry is numeric, compact, and its
> `<odom_publish_frequency>` works.
> `]` = ROS→Gazebo (we publish torque), `[` = Gazebo→ROS (IMU, joint states).
>
> **The long topic names are mandatory.** `ApplyJointForce` ignores a custom
> `<topic>` and only listens on `/model/<model>/joint/<joint>/cmd_force`.
>
> The joint_state path contains the **world name** — it is `balance_world` now,
> not `sensor_world`. Wrong world name = silently no wheel feedback.

**3b. Verify Gazebo is actually listening** (10 s, catches the #1 silent failure)
```bash
gz topic -i -t /model/craig2/joint/left_wheel_joint/cmd_force
```
Must show **both** a publisher (the bridge) and a subscriber (the plugin).
Publisher only = the robot will fall and no tuning will help.

**3c. robot_state_publisher — needed for SLAM/Nav2, skip for plain balance tests**
```bash
ros2 run robot_state_publisher robot_state_publisher ~/balancer.urdf --ros-args -p use_sim_time:=true
```
> Positional URDF path, **not** `-p robot_description:="$(cat ...)"`. The parameter form
> parses its value as YAML, and the `: ` sequences inside the URDF's comments get read as
> mapping keys — it either errors or silently mangles the model.
>
> Two warnings on startup are expected and harmless:
> - *"No robot_description parameter, assuming argument is name of URDF file"* — the
>   deprecation notice for the positional form. It loaded fine.
> - *"root link base_link has an inertia... KDL does not support a root link with an
>   inertia"* — KDL only needs geometry to compute transforms, so it discards the root
>   mass. Gazebo parses the same URDF separately and keeps it. **Physics is unaffected.**
>   The "add a dummy link" workaround only matters if you do dynamics through KDL.
>
> `Robot initialized` on the last line means it's up.

**3d. Verify the TF tree** (with the sim *playing* — a paused sim publishes no TF)
```bash
ros2 topic hz /tf                 # ~50 Hz
ros2 run tf2_ros tf2_echo odom base_link
```
Expect `Translation: [x, y, 0.080]` — z is the wheel radius, because `base_link` sits at
the axle. **The pitch in the RPY line must track reality.** Confirmed by killing the
controller and letting him fall: TF reported `pitch = -85.7°` on the fallen robot, so
`<dimensions>3</dimensions>` on the OdometryPublisher is genuinely delivering 3D pose.
Near ±90° the roll/yaw split goes degenerate (gimbal lock) — read pitch only.

Chain is: `odom → base_link` (Gazebo, bridged) and `base_link → lidar_link`
(robot_state_publisher, static). SLAM adds `map → odom` on top.

**4. Run the balance controller**

⚠️ Workspace root is **`autonomous-robot/`**, NOT `autonomous-robot/ros2_ws/`.

```bash
cd "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot"
source install/setup.bash
ros2 run robot_intro balance_controller
```
> Data goes to the CSV, not stdout — the only thing printed here is `CONTROL RATE`
> every 2 s. **That number should read ~240.** If it reads 10, something in the loop
> is blocking (see the CSV note above).
>
> `colcon build --symlink-install` (from the project root) is only needed when you
> **add a new entry point** to `setup.py`. Editing an existing node is live.

**5. Press ▶ play in Gazebo.**

**6. Drive him (optional)** — teleop, in its own terminal:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```
> Install if missing: `sudo apt install ros-jazzy-teleop-twist-keyboard`.
>
> `i`/`,` = forward/back, `j`/`l` = turn, `k` = stop. Start slow — `-` a few times to
> drop the speed before touching anything; teleop defaults to 0.5 m/s, which is a
> brisk shove for a balancing robot.
>
> The controller integrates the commanded velocity into a **moving position setpoint**,
> so releasing the key parks him where he stopped rather than letting him coast. No
> command = position hold, which is exactly the standing behaviour.

**Nothing to bridge for `/cmd_vel`** — it's ROS-side only, teleop straight to the
controller. Gazebo never sees it.

## SLAM + Nav2 (use `sensor_world`, not `balance_world`)

Everything above still applies — only step 1 changes to `gz sim ~/sensor_world.sdf`, and
step 3c (robot_state_publisher) becomes mandatory. Then:

**7. slam_toolbox**
```bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:="/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/config/slam_params.yaml" \
  use_sim_time:=true
```

**8. RViz**
```bash
ros2 run rviz2 rviz2 --ros-args -p use_sim_time:=true
```
> **RViz needs `use_sim_time` too**, or it looks up transforms at wall-clock stamps that
> don't exist in a sim-time buffer and shows an empty world — which looks exactly like
> SLAM having failed. Check the Time panel: **ROS Time must be advancing.** Frozen at
> 0.00 means `/clock` isn't arriving (sim paused, or `/clock` missing from the bridge).
>
> Fixed Frame → `map`. Add **Map** (`/map`), **LaserScan** (`/scan`), **RobotModel**
> (Description Topic `/robot_description`). RViz will not draw the robot from TF alone —
> RobotModel is a separate display.
>
> Expect `left_wheel` / `right_wheel` to show *No transform* and both wheel meshes to pile
> up at the origin as a white blob. The wheel joints are `continuous`, so
> robot_state_publisher needs `/joint_states` to place them, and nothing publishes it —
> we removed `JointStatePublisher` because it starved the control loop. **Cosmetic only:**
> SLAM uses `map → odom → base_link → lidar_link`, none of which involves wheels. Run
> `ros2 run joint_state_publisher joint_state_publisher --ros-args -p use_sim_time:=true`
> to silence it (wheels won't spin, but they'll sit in the right place).

**9. Nav2**
```bash
ros2 launch nav2_bringup navigation_launch.py \
  params_file:="/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/config/nav2_params.yaml" \
  use_sim_time:=true
```
> ⚠️ **`navigation_launch.py`, NOT `bringup_launch.py`.** Bringup also starts `map_server`
> and AMCL, and AMCL publishes `map → odom` — the transform slam_toolbox is already
> publishing. Two publishers on one transform makes the robot teleport around the map,
> and it presents as a localisation bug rather than a launch-file mistake.
>
> Keep slam_toolbox running. Nav2's static layer reads its live `/map`; no need to save
> a map first.

### Verification ladder
```bash
ros2 topic hz /clock                   # sim time is flowing
ros2 topic hz /scan                    # 10 Hz
ros2 run tf2_ros tf2_echo map odom     # exists = SLAM latched onto the scans
ros2 topic hz /map                     # ~1 Hz
```
> `minimum_travel_distance: 0.2` means slam_toolbox only adds a scan node after 20 cm of
> travel or 0.2 rad of turn. **Standing still produces one snapshot and then nothing** —
> that is not a failure. The map fills in as you drive.
>
> The walls sit 3.9 m from the origin and the lidar is capped at 4.0 m, so from dead
> centre the far walls barely register. Expected: you map an 8 m room with a 4 m sensor
> by driving it, not by looking around.

## Reading the CSV

The controller writes every sample (no throttling, no terminal) to
`/home/viktor/balance_data.csv`. Copy it over after a run:
```bash
cp /home/viktor/balance_data.csv "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/log/"
```
Columns: `t, pitch, rate, vel, pos, tau, pint, cmd, tgt`

> **Never log to stdout in the control loop.** A single throttled `get_logger().info()`
> piped through `tee` into a terminal held the loop at **10 Hz** while 222 IMU messages
> a second arrived — blocked on I/O at ~0% CPU. Write to a file handle.

## Gotchas — each of these cost real hours

- **Controller before play.** He must be caught from the first instant.
- **`gz topic -l` proves nothing.** It lists a topic if anything merely *publishes*
  to it, so a bridged-but-unsubscribed topic looks healthy. Use `gz topic -i -t`
  and confirm a **subscriber** exists.
- **Check the RTF** (bottom-right in Gazebo). It must be ~100%. `balance_world`
  pins it, but if it reads 300% you're on fast-forward and the ROS node — which
  runs on wall time — is seeing a different effective control rate than designed.
- **Clean exponential fall** (pitch doubling every sample, never reversing) is
  *not* a tuning problem. It's a wrong sign, or torque not arriving. A controller
  with authority produces wobble or overshoot, never a smooth exponential.
- **Torque doing nothing?** Sanity check with the sim playing:
  `gz topic -t /model/craig2/joint/left_wheel_joint/cmd_force -m gz.msgs.Double -p "data: 0.2"`.
  The wheel should snap hard. If it creeps, the problem is upstream of the controller.
- **Clamps go last.** Anything computed after a clamp escapes it; anything computed
  after `publish()` does nothing at all. Order is:
  compute → clamp → cutoff → publish → log.
- For a clean reset: Ctrl+C Gazebo and restart from step 1.

## Physics settings now pinned in balance_world.sdf
| setting | value | why |
|---|---|---|
| `max_step_size` | 0.001 | 1000 Hz physics vs 250 Hz control |
| `real_time_factor` | 1.0 | sim time locked to wall time |
| gravity | −9.81 | stated, not inherited |
| ground `mu`/`mu2` | 1.5 | traction stops being the limit |
| contact `kp`/`kd` | 1e6 / 100 | stops a light robot chattering on rigid contact |
| IMU `update_rate` | 250 Hz | ~20 samples per 82 ms doubling time |
