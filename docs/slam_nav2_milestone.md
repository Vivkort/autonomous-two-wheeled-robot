# Milestone — craig2 Navigates Autonomously While Balancing

**Reached:** July 2026
**Robot:** craig2 — a two-wheeled self-balancing robot (inverted pendulum)

craig2 builds a live map of an unknown room, localizes himself in it, and drives to
navigation goals routing around obstacles — all while actively balancing on two wheels.
SLAM and Nav2 were ported from craig1 (a statically-stable four-wheeled robot) and adapted
to the one thing craig1 never had to worry about: the robot can fall over, and the sensor
is bolted to a body that leans.

## The result

```
map                clean rectangular room, walls single and straight
obstacles          box + cylinder mapped as hollow shells (lidar sees faces only)
loop closure       room outline meets itself, no drift ghosting
navigation         Nav2 goal-to-goal, obstacle routing, balances throughout
bringup            one command (scripts/sim.sh) - the whole stack
```

## Final architecture

Nine nodes, one balancing robot. The stack, and who publishes what:

```
Gazebo (sensor_world)  ─ physics, lidar, IMU, wheel odometry
parameter_bridge       ─ /imu /scan /odom /clock, wheel torques, and the odom TF
balance_controller     ─ 250 Hz LQR torque loop (unchanged from the balancing milestone)
scan_gate              ─ /scan -> /scan_gated, gated on pitch (the new piece)
robot_state_publisher  ─ base_link -> lidar_link (static)
slam_toolbox           ─ map -> odom, builds the occupancy grid
nav2 (navigation_launch) ─ planner, controller, costmaps, behaviors, lifecycle mgr
joint_state_publisher  ─ wheel joint angles (cosmetic, for RViz)
rviz2                  ─ visualization
```

### The TF tree had to be built from nothing

craig1 got its transforms for free from the DiffDrive plugin. craig2 uses `ApplyJointForce`
for torque control, which publishes no odometry and no TF — so the entire tree was missing
and SLAM had nothing to stand on. The chain now:

```
map ──slam_toolbox──▶ odom ──Gazebo odom, bridged──▶ base_link ──robot_state_publisher──▶ lidar_link
```

Confirmed 3D: killing the controller and letting him fall showed `base_link` reading
**pitch −85.7°** in TF, so `<dimensions>3</dimensions>` on the OdometryPublisher genuinely
carries the lean, not a flattened 2D pose. (Near ±90° the roll/yaw split goes degenerate —
gimbal lock — so read pitch only when he's down.)

## The balancer-specific problem: a fall eats the map

This is the core lesson of the port. The lidar is rigidly mounted to `base_link`, 0.50 m up
(0.08 axle + 0.42). Upright, it sweeps a horizontal plane and sees a floor plan. **Tip him
over and it sweeps a vertical plane** — straight up into empty space and straight down into
the floor a few centimeters away. Those returns are geometrically valid and completely
meaningless as a 2D map.

slam_toolbox doesn't know he fell. It scan-matches the garbage against the map it had, fails,
drifts the pose to force a match, and writes the result into the occupancy grid. Every second
he lies there, more of the good map is overwritten. **A fallen balancing robot doesn't stop
mapping — it actively destroys the map it already built.** We watched a clean room dissolve
into streaks in about ten seconds.

### The fix: a scan gate

A ~20-line node (`scan_gate.py`) subscribes to `/scan` and `/odom`, and republishes each scan
on `/scan_gated` **only when the body is upright enough** to trust:

```
|pitch| < arcsin(lidar_height / max_range) = arcsin(0.50 / 4.0) = 7.2° = 0.1257 rad
```

Past that lean the beam starts hitting floor or clearing walls, so the scan stops describing
the room whether he's mid-recovery or flat on the ground. slam_toolbox reads `/scan_gated`
instead of `/scan`. Now a fall simply **pauses** mapping and resumes it automatically once
he's level — the map survives.

Two implementation notes that cost time:

- **Take pitch from `/odom` (50 Hz), not `/imu` (250 Hz).** The gate only decides when a scan
  arrives (10 Hz), so 250 Hz input is wasted CPU on a machine that was already saturated.
- **The gate republishes the message unchanged**, so it preserves the lidar's original
  sim-time stamp. That means slam accepts it regardless of the gate node's own clock — no
  `use_sim_time` gymnastics needed on the relay.

## The phantom velocity

With no command, craig2 sat in a slow position limit cycle — rocking ±0.11 m with a ~13 s
period — while his attitude stayed flawless (±0.02°). The CSV explained it:

- `vel` (from odometry `twist.linear.x`) read a near-constant **+0.11 m/s**.
- The *true* velocity, d(`pos`)/dt, swung **±0.05 m/s around zero**.

The odometry velocity was decoupled from reality — a phantom. That starved the velocity-damping
term: `K_wvel` was fed a signal that never tracked the motion, so it provided no damping, and a
position loop with no velocity damping rings. The integrator had quietly wound to −73.8 to cancel
the constant 0.11 offset (`0.0015 × −73.8 = −0.11` exactly), which is why he held roughly steady
instead of accelerating away — but it couldn't damp the oscillation.

**Fix:** stop trusting the odom twist. Derive velocity by differencing odom *position*, which is
clean, inside `update_odom` (50 Hz, using the message's sim-time stamp for dt). That gave `K_wvel`
an honest signal and the ring damped out.

## The fall that was really a logging bug

Mid-run he fell for no visible reason. The CSV showed the control loop **stopped for 2.5 seconds**
— the last healthy sample was dead level and cruising, then a 2.5 s gap, then 76°. His tip angle
doubles every ~77 ms, so 2.5 s of silence is eleven doublings past unrecoverable.

The cause was a single `CONTROL RATE` print firing every 2.00 seconds and stalling the loop ~50 ms
each time — right at the measured 25–30 ms stability threshold. It survived most of the time and
killed him when a scheduling hiccup stacked on top. Same disease as the 10 Hz throttle from the
balancing milestone, just intermittent. Two fixes:

- **Delete the print.** The rate is already recoverable from the CSV timestamp column.
- **`real_time_factor: 0.5`.** Running sim at half wall-speed means a 50 ms scheduling stall costs
  25 ms of *simulated* falling — it doubles the delay tolerance for free, at the cost of patience.

Underlying truth worth stating: a 250 Hz control loop in Python, on a general-purpose scheduler,
sharing a machine with a physics engine and a Ceres solver, is fighting jitter that will not exist
on the real robot. The ESP32 does nothing but balance.

## One-command bringup, and the lifecycle lesson

`scripts/sim.sh` (wrapping `launch/craig2_sim.launch.py`) brings up the entire stack in one
command; `sim.sh nav2:=true` adds Nav2. The trick that makes it safe for a balancer: **Gazebo
starts running but craig2 is spawned 7 seconds late, on a timer**, so the controller, bridge and
gate are all listening before he exists. The instant he drops in he's caught — the automated
version of "controller before play."

The last bug of the whole port lived here. The launch first ran slam_toolbox as a bare
`Node(...)`. It started, appeared in `ros2 node list`, and did nothing — because **slam_toolbox is
a lifecycle node** and a raw node is never transitioned `configure → activate`. It sat
`unconfigured`, never subscribed to scans, never published `map → odom`. "It's in the node list"
is not "it's working" for lifecycle nodes — check `ros2 lifecycle get <node>`. The fix: have the
launch **include** slam_toolbox's own `online_async_launch.py`, which does the transitions. Nav2's
`navigation_launch.py` was already correct because it ships its own lifecycle manager.

## Configs that had to change for a balancer

| setting | craig1 | craig2 | why |
|---|---|---|---|
| lidar `max_range` | 12.0 | **4.0** | at 0.50 m height, a 2.4° lean puts a 12 m beam through the wall; 4 m gives immunity to 7.2° |
| `slam max_laser_range` | 12.0 | **4.0** | match the sensor, or max-range no-returns get mapped as a phantom wall |
| Nav2 `max_accel` (x) | 2.5 | **1.0** | 2.5 m/s² demands a 14° lean held; `g·tan(7.2°) = 1.24`, so 1.0 stays in the pitch-immune envelope |
| Nav2 `desired_linear_vel` | 0.5 | **0.3** | accuracy over speed — every acceleration is a lean |
| `rotate_to_heading_angular_vel` | 1.0 | **0.5** | matches the yaw loop's authority (`K_yaw = 0.5`) |

The acceleration limit is the one that matters. To accelerate at rate `a`, an inverted pendulum
must lean at `θ = arctan(a/g)`. Braking is worse — it's the non-minimum-phase direction, so he
must briefly speed *up* to lean back before he can slow down. The stop at a goal is the single
most dangerous moment in a Nav2 run, which is exactly why `max_decel` is clamped to −1.0.

## Failure modes, and what each looked like

| symptom | what it actually was |
|---|---|
| RViz "Frame [map] does not exist", planner "waiting for transform to map" | slam not publishing map→odom — always trace to *no map being built* |
| slam "queue is full", scans dropped | slam receiving scans but can't transform them — a TF gap, not a scan gap |
| node in `ros2 node list` but doing nothing | lifecycle node left `unconfigured` — check `ros2 lifecycle get` |
| subscriber goes silent after a respawn, no error | stale subscription — restart subscribers after respawning their publisher |
| slow forward "drift" that never stops | phantom odom velocity feeding an undamped position loop |
| clean map suddenly turning to streaks | the robot fell and the tilted lidar is poisoning the map |

## Why it matters

This is craig2's jump from "balances and drives" to "knows where he is and goes where you point."
The structure transfers to hardware unchanged — a real lidar on a real ESP32-class machine reads
this loop without the scheduler jitter that dominated the sim, and real rubber on a real floor has
friction without a `<surface>` tag. The scan gate, the position-differenced velocity, and the
acceleration envelope are all things the *physical* balancer will need too — the sim's hardest
problems are the hardware's easiest ones, but these three are real on both.

**Next:** the hardware build.
