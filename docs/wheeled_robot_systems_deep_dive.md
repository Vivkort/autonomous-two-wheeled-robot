# Wheeled Autonomous Robot — How Every Part Works Together (Deep Dive)

Configuration locked in: **Jetson Orin Nano Super** (from Amazon, ~$500), **real RPLidar**, **3D-printed chassis**, depth camera included. Below is the full systems explanation — what each part does, how it works internally, and, most importantly, **how the data flows between them** to turn "spinning wheels" into "a robot that decides where to go."

*Prices are current-Amazon-street as of July 2026 and noted per line.*

---

## 0. First: can you build your own RPLidar instead?

Technically yes — it's the same idea as your spinning VL53L1X, just faster and 360°. But for SLAM it's not worth it, and here's the concrete reason: `slam_toolbox` needs a scan that is **fast** (5–10 full rotations/sec), **dense** (thousands of points/sec), **accurate to millimeters**, and **angularly precise** (it must know the exact bearing of every point). A DIY spun sensor gives you maybe 1–5 rev/sec, sparse points, and jittery angles — SLAM will produce a smeared, drifting map. The **RPLidar C1** (~$100) solves all four in one sealed unit with a factory-calibrated encoder. Buy it; spend your build energy on the parts that teach you more. Keep DIY lidar as a "for fun" side project.

---

## 1. The big picture: the sense → think → act loop

Every autonomous robot runs one loop, forever:

```
   SENSE ───────────► THINK ───────────► ACT ───────┐
 (lidar, camera,   (localize, map,   (motor commands)│
  IMU, encoders)    plan a path)                      │
      ▲                                               │
      └───────────── the world changes ◄──────────────┘
```

Your job as the builder is to wire up each arrow so data flows cleanly. The parts split into two brains:

- **The Jetson = the cerebrum.** Slow, smart, thinks in maps and goals. Runs Linux + ROS 2. Asks questions like "where am I and how do I get to the kitchen?"
- **The microcontroller = the cerebellum.** Fast, dumb, reflexive. Runs a tiny real-time program. Answers "spin the left wheel at exactly this speed *right now*, and count how far it turned."

**Why split them?** The Jetson runs a full operating system, so its timing isn't guaranteed — a background task could delay it by milliseconds. Motor control and encoder counting need microsecond precision or the robot jerks and loses track of itself. So the MCU handles the hard-real-time muscle work, and the Jetson handles the thinking. This split is how essentially every real robot is built.

---

## 2. Part-by-part: what each does and how it works

### The Jetson Orin Nano Super — the brain (~$500 on Amazon)

A small Linux computer with a CUDA-capable GPU. It runs **ROS 2**, the software framework that ties everything together. Internally, ROS 2 is a set of small programs ("**nodes**") that pass messages to each other over named channels ("**topics**"). One node talks to the lidar, one builds the map, one plans paths — and they communicate by publishing/subscribing to topics like `/scan`, `/odom`, `/cmd_vel`.

The Jetson's GPU matters for two things: later AI (Phase 5 vision-language models), and *now* if you use an AI-capable depth camera or run vision. It connects to the outside world through **USB** (lidar, camera, motor MCU) and **GPIO/I²C pins** (IMU, if wired directly). Note: the $500 Amazon price is a third-party markup over the $249 MSRP — that board is chronically out of stock at MSRP, so paying for availability is reasonable given budget isn't the constraint.

### The motor-control microcontroller — the cerebellum (~$10)

An **ESP32** or **Teensy 4.0**. It runs one small firmware program with two jobs:

1. **Drive the motors:** it receives target wheel speeds from the Jetson and outputs **PWM** (pulse-width modulation — rapidly switching the motor power on/off; more "on" time = faster) to the motor driver.
2. **Read the encoders:** it counts encoder ticks (below) using hardware interrupts, so it never misses a pulse, and reports the counts back to the Jetson.

It talks to the Jetson over a single **USB cable** using **micro-ROS**, which makes the microcontroller appear as just another ROS 2 node — it subscribes to a wheel-command topic and publishes an odometry topic. To the Jetson, the whole motor subsystem looks like two ROS topics.

### DC gear motors with encoders — the muscles + the odometer (~$30/pair)

Two DC motors, each with a **gearbox** (trades speed for torque so the robot can actually push its own weight) and a **quadrature encoder** on the shaft. The encoder is the critical part: it's a small disc with two sensors (channels A and B) that emit pulses as the shaft turns. Counting pulses tells you **how far** each wheel rotated; the A-vs-B phase order tells you **which direction**. This is what gives the robot **odometry** — a dead-reckoning estimate of how far and which way it has moved. Without encoders the robot is blind to its own motion, so **do not buy motors without encoders.**

### The motor driver (TB6612FNG) — the amplifier (~$8)

The MCU's PWM signal is a tiny logic-level pulse — nowhere near enough current to move a motor. The **motor driver** is a dual **H-bridge**: it takes the weak PWM + direction signals and switches the *battery's* full current to the motors accordingly. An H-bridge can also reverse polarity, which is how one signal makes a motor go forward or backward. (TB6612FNG is more efficient and cooler-running than the older L298N — prefer it.) So the chain is: **MCU logic → driver → battery power → motor spins.**

### The RPLidar C1 — the primary spatial sense (~$100)

A sealed, spinning **DTOF** (direct time-of-flight) laser scanner. A laser + detector rotate 5–10 times per second, firing thousands of pulses and timing each round trip to measure distance, while a built-in encoder tags each measurement with its exact angle. The result is a **`LaserScan`**: a full 360° ring of distances in one horizontal plane, ~12 m range. It plugs into the Jetson by **USB** (through a little USB-serial adapter that comes with it). This single flat ring is what SLAM uses to recognize walls and figure out where the robot is. Its one limitation: it only sees **one height** — a single slice — which is exactly why you also want a depth camera.

### The IMU (BNO055) — the inner ear (~$25)

An **Inertial Measurement Unit**: a gyroscope (measures rotation rate) + accelerometer (measures linear acceleration), and in the BNO055's case a magnetometer plus an on-chip processor that fuses them into a clean orientation estimate. Its job is to tell the robot **which way it's facing and how fast it's turning**, independent of the wheels. This matters because wheels **slip** — on a turn, encoders alone will mis-estimate heading. Fusing the IMU with wheel odometry (next section) gives a far steadier pose. Connects to the Jetson (or the MCU) over **I²C**.

### The depth camera — 3D vision (see Section 4 for options/cost)

Where the lidar sees one flat ring, the depth camera sees a **full 2D grid of distances** — a depth image — giving the robot 3D perception in front of it. It produces a **point cloud** (there's your lidar work again, but dense and real-time). This lets the robot detect obstacles the lidar's single plane misses entirely: a tabletop edge, a step down, a low box, a chair seat. It plugs in by **USB 3.0**. Full cost breakdown in Section 4.

### Power system — the heart (~$40)

A **battery** (3S LiPo ~11.1 V, or a 12 V pack) feeds two branches through a common ground:

- **Motors:** the battery voltage goes straight to the motor driver — motors are noisy, high-current loads.
- **Jetson:** the battery goes through a **buck converter** (a DC-DC regulator that steps the voltage down to a clean, stable 5 V at up to ~5 A). The Jetson is **picky** — an unstable or under-rated supply causes random reboots. Give it its own dedicated buck converter; don't power it off the same rail as the motors.

Add an **inline fuse** on the battery and a master switch. Keeping the "dirty" motor power and "clean" logic power separate (but sharing ground) is one of the most important reliability choices in the whole build.

### The 3D-printed chassis — the skeleton (your filament)

Holds everything in fixed, known positions. This last point is not cosmetic: ROS needs to know **exactly** where each sensor sits relative to the robot's center — the lidar 10 cm up and 5 cm forward, the camera at the front, etc. You'll encode these offsets in a **URDF** file (a description of the robot's body and joint/sensor positions). Because you're printing it, you control those dimensions precisely and can put them straight into the URDF. Design it in two decks: battery + motors + driver on the bottom, Jetson + lidar (needs a clear 360° view, so mount it on top) + camera (facing forward) up high.

---

## 3. How it all works together — one navigation cycle, step by step

Here's the actual data flow when you say "go to the kitchen." Follow the topics:

```
 RPLidar ──/scan──►┐
                   ├──► slam_toolbox ──► /map  +  map→odom correction
 IMU ──/imu──►┐    │        (builds map, fixes drift)
              ├────┤
 encoders ──/odom──┤──► robot_localization (EKF) ──► smooth odom→base_link
   (via MCU)       │        (fuses wheels + IMU into a clean pose)
                   │
 depth cam ─/points─┘
                   │
        ┌──────────▼───────────────────────────────────┐
        │  Nav2  (the planner)                          │
        │  inputs: /map, robot pose, goal, costmaps     │
        │  (costmaps built from /scan + /points)        │
        │  output: /cmd_vel  (drive this fast + turn)   │
        └──────────┬───────────────────────────────────┘
                   │ /cmd_vel  (geometry_msgs/Twist)
                   ▼
        diff-drive controller → left/right wheel speeds
                   │  (over USB / micro-ROS)
                   ▼
              ESP32/Teensy → PWM → TB6612 → motors turn
                   │
                   └─ encoders count ticks → /odom → (back to the top)
```

Walking through it in plain language:

1. **The lidar** streams a 360° ring of distances (`/scan`). **The encoders**, via the MCU, stream wheel-based odometry (`/odom`). **The IMU** streams orientation (`/imu`).
2. **`robot_localization` (an EKF filter)** fuses wheel odometry + IMU into one smooth, drift-resistant estimate of the robot's motion — better than either alone, because it trusts the IMU for rotation and the wheels for distance.
3. **`slam_toolbox`** takes the lidar scans + that motion estimate and does two things at once: **builds a map** of the room (an occupancy grid — free space vs. walls) and **corrects long-term drift** by matching each new scan against the map. It publishes the crucial `map → odom` transform that anchors the robot in the map.
4. **`tf2`** (the transform system) stitches all these frames into one tree: `map → odom → base_link → each sensor`. Now every sensor reading can be expressed in map coordinates. This is the glue — every node uses `tf` to know where things are relative to everything else.
5. You send a **goal pose** ("kitchen") in RViz. **Nav2** takes the map, the robot's current pose, and the goal, and computes a path with its **global planner**. Its **local planner/controller** then continuously watches the **costmaps** — live obstacle maps built from the lidar *and* the depth-camera point cloud — and emits velocity commands (`/cmd_vel`: "go 0.3 m/s forward, turn 0.2 rad/s left") that follow the path while dodging anything new.
6. **The diff-drive controller** converts that single `/cmd_vel` (body-level "forward + turn") into two wheel speeds, sends them to the **MCU**, which drives the **motor driver**, which spins the **motors**.
7. The wheels turn, the **encoders** count the motion, and the fresh odometry flows right back to step 1. The loop runs ~10–50 times a second. The robot is now navigating itself.

The elegance: no single part is smart. The lidar just measures, the motors just spin, the MCU just counts. **Intelligence is an emergent property of the data flow** — of these dumb parts publishing to the right topics and a few ROS 2 nodes fusing it all. That's the whole game, and it's the same architecture that scales up to your humanoid.

---

## 4. The depth camera: options and what it adds to the budget

You asked specifically what including it costs. Three realistic Amazon choices:

| Camera | ~Amazon price | Depth method | Why pick it |
|---|---|---|---|
| **Luxonis OAK-D Lite** | **~$149** | Stereo + on-camera AI (Myriad X VPU) | **Best for your endgame** — runs neural nets *on the camera*, offloading the Jetson. Great stepping stone to Phase 5 AI. |
| Intel RealSense D435i | ~$300–350 | Active stereo (IR projector) + built-in IMU | Industry standard, best-documented ROS 2 support, and its built-in IMU can double as your robot's IMU. |
| Luxonis OAK-D (full) | ~$200–250 | Stereo + on-camera AI, wider baseline | More range/accuracy than the Lite, still does on-camera AI. |

**What it adds to the budget: ~$149** if you take the OAK-D Lite (my recommendation), up to ~$350 for the RealSense.

**Recommendation:** the **OAK-D Lite at ~$149**. It gives you 3D obstacle perception now *and* on-camera AI inference that directly seeds your Phase-5 vision work — the same reasoning that led us to the Jetson. If you'd rather have the most turnkey ROS 2 support and don't mind spending more, the RealSense D435i is the safe classic (and its onboard IMU means you could skip the separate BNO055, clawing back ~$25).

---

## 5. Full Amazon bill of materials

| Part | ~Amazon price |
|---|---|
| Jetson Orin Nano Super Dev Kit | $500 |
| NVMe SSD 256 GB (M.2 2280) | $30 |
| RPLidar C1 (360° lidar) | $100 |
| OAK-D Lite depth camera | $149 |
| 2× DC gear motors w/ quadrature encoders | $30 |
| TB6612FNG motor driver | $8 |
| ESP32 dev board (motor MCU) | $10 |
| BNO055 IMU | $25 |
| 3S LiPo battery (or 12 V pack) + charger | $45 |
| Buck converter 5 V / 5 A | $10 |
| Caster wheel + wheels/hubs | $15 |
| Wiring, standoffs, switch, inline fuse, connectors | $20 |
| Chassis | 3D-printed (your filament) |
| **Total** | **~$942** |

Notes: swap to the RealSense D435i and you land near ~$1,140 but can drop the $25 IMU. Everything here is stocked on Amazon US with reasonable ship times. The Jetson at $500 is the one marked-up line — that's the availability premium you already flagged.

---

## 6. Recommended build order (so nothing fights you)

1. **Jetson bring-up** — flash JetPack to the SSD, install ROS 2, confirm it boots and `ros2 topic list` runs.
2. **Motors + MCU on the bench** (no chassis yet) — get micro-ROS driving one motor and reporting encoder ticks.
3. **Print + assemble the chassis** — two decks, sensor mounts at known offsets.
4. **Model the URDF** — put those exact offsets in; visualize in RViz.
5. **Add the lidar** — see `/scan` live in RViz.
6. **Add IMU + fuse odometry** — watch the pose estimate hold steady as you push the robot by hand.
7. **SLAM** — drive it around, build and save a map.
8. **Nav2** — set a goal, watch it plan and drive there.
9. **Add the depth camera** to the costmap — now it dodges 3D obstacles the lidar misses.

Get through step 8 and you have a genuinely autonomous robot. Step 9 makes it robust.

---

Want me to take this to the next level of detail next: the **URDF file** for a 3D-printed two-deck chassis, the **ESP32 micro-ROS firmware** for the motors/encoders, and the **ROS 2 launch files** that start this whole graph? I can also generate a printable chassis design spec for your 3D printer.
