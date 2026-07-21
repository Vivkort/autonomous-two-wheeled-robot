# Milestone — craig2 Balances and Holds Position

**Reached:** July 2026
**Robot:** craig2 — a two-wheeled self-balancing robot (inverted pendulum)

craig2 stands upright indefinitely on two wheels, damps disturbances back to vertical,
and returns to his starting position after being displaced. Everything below was built
and debugged from scratch in Gazebo Harmonic.

## The result

```
duration          55.4 s        control rate      246 Hz
saturation        0.0%          max lean          3.82°
peak excursion    +7.25 m       final position    +0.004 m
final velocity    0.002 m/s     final torque      0.0001 N·m
```

He drifted 7.25 m during start-up, turned around, and came home to **4 mm** from where
he started. The return is a clean exponential — 7.25 → 4.40 → 1.28 → 0.14 → 0.004 —
with no overshoot, and torque never exceeded a quarter of what the floor could transmit.

## Tested recovery limit

Spawned at increasing initial lean (`create ... -P <rad>`), craig2 recovers up to
**0.70 rad (40°)** and fails at **0.75 rad (43°)**.

For context, the physical ceiling is set by traction, not by the controller. Holding a
lean of θ requires the base to accelerate at `g·tan(θ)`, and friction caps acceleration
at `μ·g`, so the maximum recoverable lean is:

```
θ_max = arctan(μ) = arctan(1.5) = 56.3°
```

He reaches **77% of the physical maximum**, and **2.5× the 0.30 rad the LQR design
predicted**. The model under-predicts because it's linearised about upright; at 40° the
small-angle approximation is long gone and the real robot outperforms the linear theory.

Torque saturated only 9% of the time during these saves, so authority was never the binding
constraint — velocity peaked near 8 m/s, which is simply what catching a 40° lean costs.
The wall is traction, not motors.

**Caveat when repeating this:** restart the controller between attempts. Rapid-firing
spawns appends every run to one CSV and drags the measured control rate down (110 Hz vs
the usual 246), which makes the data hard to read.

## Final architecture

**Torque control, not velocity.** The controller commands wheel *torque* directly via two
`ApplyJointForce` plugins. This matters: PD on angle with velocity commands
(`/cmd_vel` + DiffDrive) is only *marginally* stabilising. Work the idealised
cart-pendulum through with `v = Kp·θ + Kd·θ̇` and you get

```
θ̈ (L + Kd) = g·θ − Kp·θ̇
```

The `θ` coefficient is `+g/(L+Kd)` — **positive for every possible choice of gains**.
That architecture balances by accident, via secondary effects the ideal model omits.
Torque control has an actual stability proof.

**Full-state feedback plus an integrator.** Five terms, summed directly — no cascade,
no target-pitch trick:

```python
tau = K_pitch·pitch + K_rate·pitch_rate + K_wvel·velocity + K_wpos·position + K_int·∫position
```

| gain | value | units |
|---|---|---|
| `K_pitch` | 4.932 | N·m per rad of lean |
| `K_rate` | 0.446 | N·m per rad/s of tipping |
| `K_wvel` | 0.1971 | N·m per m/s |
| `K_wpos` | 0.02887 | N·m per m |
| `K_int` | 0.0015 | N·m per m·s (clamp ±400) |
| `max_torque` | 0.4 | N·m per wheel (traction ceiling ≈1.30) |

All four LQR gains are **positive**. Wheel-velocity feedback is destabilising *on its own* —
that's why every attempt at a three-gain controller failed in both sign directions. It only
becomes stabilising when paired with the position term. Two gains cannot control four states.

## How the gains were derived

Not tuned by hand. The linearised wheeled-inverted-pendulum model was built directly from
`balancer.urdf` (Mb=2.0 kg, CoM 0.20 m, Ib=0.0283, wheel r=0.08, spin inertia 0.0012):

```
A₁·ẍ + B₁·θ̈ = τ/r                    (ground force drives the cart)
B₁·ẍ + C₁·θ̈ − Mb·g·L·θ = −τ          (reaction torque on the body)
```

giving `θ̈ = 101.3·θ − 115.6·τ` — an open-loop tip rate of **9.2/s**, doubling every 75 ms.
Continuous-time LQR with `Q = diag(0.01, 0.01, 200, 1)`, `R = 3`, then verified in a
discrete simulation at the real control rate against pitch offsets to 0.30 rad, rate kicks
to 3 rad/s, and velocity shocks to 1 m/s.

## Why an integrator was needed

Pure state feedback settled into a stable equilibrium **8.5 m from the origin**, leaning back
2.9°, commanding zero torque. The terms cancelled exactly:

```
K_pitch × (−0.0497) = −0.2467
K_wpos  × ( 8.539)  = +0.2465
                       -------
                        0.0000
```

There is an effective constant offset of ~0.05 rad between "what the controller treats as
upright" and "where the robot actually balances." Proportional state feedback cannot remove
a constant disturbance — it can only trade it against another state, and here it bought pitch
balance with position error. Textbook steady-state error; the fix is integral action.

The algebra predicted the integrator needed to reach `0.245/0.0015 = 163` to cancel it.
It settled at **163.5**.

## Simulation gotchas — every one of these cost hours

**The physics engine matters more than anything else.** Under DART (gz-sim's default) the
wheels chattered — wheel velocity reversing sign on 32–70% of samples, swinging ±30 rad/s,
which made the velocity state useless as feedback. Switching to **bullet-featherstone**
dropped that to 1% and the same controller suddenly worked:

```bash
gz sim --physics-engine gz-physics-bullet-featherstone-plugin ~/balance_world.sdf
```

**A print statement throttled the control loop to 10 Hz.** The node received 222 IMU
messages/second and processed 10, while using ~0% CPU — blocked on stdout → `tee` → the
VS Code terminal, not computing. Every gain tuned before this was compensating for a
logging call. Log to a file handle directly; never to a terminal in a real-time loop.

**Gazebo silently ignores SDF parameters.** Three separate times:
- `ApplyJointForce` ignores `<topic>` — always uses `/model/<model>/joint/<joint>/cmd_force`
- `JointStatePublisher` ignores `<update_rate>` — published at ~700 Hz regardless
- The IMU's `<update_rate>` *does* work

Never assume a parameter took effect. `gz topic -i -t <topic>` and confirm a **subscriber**
exists — `gz topic -l` only proves something is *publishing*, so a bridged-but-unsubscribed
topic looks perfectly healthy while the robot falls over.

**Never use `JointState` in a fast loop.** It carries a list of joint-name *strings*, and
deserialising string arrays in Python at high rate is expensive. Use `OdometryPublisher`
instead: compact, numeric, and `<odom_publish_frequency>` actually works.

**The ground plane had no friction defined at all.** Wheels spun freely at torques far inside
the apparent traction limit for hours before this was found. State `mu`/`mu2` explicitly.

**Spawn height must equal the wheel radius.** Spawning higher drops the robot, and that bounce
is a disturbance at the start of every single run — which we spent a long time interpreting
as spontaneous instability.

**Inertia tensors must satisfy the triangle inequality** (`ixx + izz ≥ iyy`) or Gazebo rejects
the link outright. Also: put the spin inertia on the axis the joint actually rotates about, and
include the motor rotor inertia reflected through the gearbox (≈ rotor × ratio²), which
dominates the bare wheel disc.

**Clamps go last.** Anything computed after a clamp escapes it; anything computed after
`publish()` does nothing at all. Order: compute → clamp → cutoff → publish → log.

## Reading a failure from the log

| what the log shows | what it means |
|---|---|
| clean exponential, pitch doubling, never reversing | wrong sign, or command not arriving — *not* a tuning problem |
| oscillation at constant amplitude, torque pinned at the clamp | saturation → bang-bang → limit cycle |
| oscillation growing slowly | marginally unstable; needs damping or less loop delay |
| pitch fine, position drifting monotonically | missing position/velocity feedback |
| stable but parked away from origin | steady-state error; needs integral action |

## Diagnosing loop delay

A controller can only be as fast as its measurements. The stability threshold here was sharp:
under 25 ms of loop delay it settled, past 30 ms it broke into a limit cycle, and both the
amplitude and frequency tracked the delay. If you can't reduce the delay, you can **design for
it** — raising `R` in the LQR lowers bandwidth and buys delay tolerance, at the cost of a
softer response. Measure the delay first; don't assume it.

## Why it matters

The controller structure transfers directly to hardware. A real ESP32 reading an MPU6500 runs
this loop in microseconds instead of milliseconds — none of the latency that dominated the sim
exists on a microcontroller — and real rubber on a real floor has friction without needing a
`<surface>` tag. The sim's hardest problems are the physical robot's easiest ones.

**Next:** find the actual recovery limit (spawn with `-P 0.15` and up; the design claims 0.30 rad),
then begin the hardware build.
