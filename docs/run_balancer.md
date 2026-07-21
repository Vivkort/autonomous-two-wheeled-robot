# Running the Self-Balancing Robot (craig2) in Sim

**Current architecture:** torque control + LQR full-state feedback, in a dedicated
`balance_world` with pinned physics.

## One-time setup (symlinks — skip if already done)
```bash
ln -sf "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/urdf/balancer.urdf" $HOME/balancer.urdf
ln -sf "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/worlds/balance_world.sdf" $HOME/balance_world.sdf
ln -sf "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/worlds/sensor_world.sdf" $HOME/sensor_world.sdf
```

## Launch sequence — one command per Ubuntu terminal

**1. Gazebo world**
```bash
gz sim ~/balance_world.sdf
```
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

**3. Bridge — IMU + wheel torques + odometry**
```bash
ros2 run ros_gz_bridge parameter_bridge "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU" "/model/craig2/joint/left_wheel_joint/cmd_force@std_msgs/msg/Float64]gz.msgs.Double" "/model/craig2/joint/right_wheel_joint/cmd_force@std_msgs/msg/Float64]gz.msgs.Double" "/model/craig2/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry"
```
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

**4. Run the balance controller**

⚠️ Workspace root is **`autonomous-robot/`**, NOT `autonomous-robot/ros2_ws/`.

```bash
cd "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot"
source install/setup.bash
PYTHONUNBUFFERED=1 RCUTILS_LOGGING_BUFFERED_STREAM=0 ros2 run robot_intro balance_controller 2>&1 | tee "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/log/balance_run.txt"
```
> The env vars are required when piping to `tee`. Without them Python block-buffers
> and Ctrl+C kills the process before the buffer flushes, leaving a 0-byte log.
>
> `colcon build --symlink-install` (from the project root) is only needed when you
> **add a new entry point** to `setup.py`. Editing an existing node is live.

**5. Press ▶ play in Gazebo.**

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
