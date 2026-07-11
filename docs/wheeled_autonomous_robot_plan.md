# Phase 1 — Wheeled Autonomous Robot: Full Plan (Draft)

Your first *complete* robot: a differential-drive rover that maps a room and drives to a goal on its own, without hitting things. It's the platform that teaches ROS 2, SLAM, and navigation — the backbone everything later (manipulation, the AI brain, legs) hangs on. Your lidar work plugs straight into this.

*Prices below verified July 2026. Note the unusual situation: a global DRAM shortage has spiked single-board-computer prices, which changes the usual board recommendation — see below.*

---

## 1. The brain: Raspberry Pi 5 vs. Jetson Orin Nano Super

These are the two realistic choices. Normally the Pi wins on price by a mile; right now that gap has nearly closed, which matters for you.

| | Raspberry Pi 5 (8 GB) | Jetson Orin Nano Super Dev Kit |
|---|---|---|
| **Price (Jul 2026)** | ~$199 (8 GB) / ~$305 (16 GB) — spiked from DRAM shortage | **$249** (dropped from $499 in late 2024) |
| **AI compute** | ~0 on its own; needs AI HAT+ 2 (+$130) for 40 TOPS | **67 TOPS built in** |
| **GPU / CUDA** | No CUDA (VideoCore GPU) | **1024-core Ampere GPU, 32 Tensor cores, full CUDA** |
| **CPU** | 4-core Cortex-A76 @ 2.4 GHz | 6-core Cortex-A78AE @ 1.7 GHz |
| **RAM** | 8 or 16 GB LPDDR4 | 8 GB LPDDR5 (68 GB/s) |
| **Power draw** | ~5–8 W | ~7–25 W (configurable) |
| **Ecosystem** | Huge hobbyist community, simplest setup | The standard for *edge AI robotics*; runs VLMs/LLMs locally |
| **Runs local LLMs/VLMs well?** | Only with the AI HAT, and modestly | **Yes — this is what it's built for** |
| **Best for** | Simple, low-power, cost-sensitive robots | Robots that will run vision + AI on-board |

**Recommendation for your goal: the Jetson Orin Nano Super.** Two reasons that are specific to *you and to right now*:

1. **The price gap collapsed.** A Pi 5 8 GB is ~$199 and a 16 GB is ~$305 because AI-driven DRAM demand spiked memory costs ~7×. The Jetson at $249 sits right in the middle — but with CUDA and 67 TOPS of AI compute the Pi simply doesn't have without a $130 add-on. Dollar-for-capability, the Jetson is now the clear pick.
2. **Your endgame is an AI robot.** Phase 5 puts a vision-language model on-board. That's CUDA territory. Buying the Jetson now means the same board carries you from this rover all the way to running local VLMs later — no re-platforming.

**When the Pi still wins:** if you want the absolute simplest first setup, lowest power draw, or you're on a tight budget and fine adding AI compute later, the Pi 5 (8 GB) is a perfectly good learning platform and has the friendlier on-ramp. It won't hold you back for Phases 1–3; it only becomes limiting at Phase 5.

> Draft decision: **Jetson Orin Nano Super**. If budget is the deciding factor, Pi 5 8 GB is the fallback and everything below still applies (ROS 2 runs on both).

---

## 2. What the robot is (architecture)

```
            ┌─────────────────────────────┐
            │   Jetson Orin Nano Super     │  ← ROS 2 brain: SLAM, Nav2, decisions
            │   (Ubuntu + ROS 2)           │
            └───┬───────────┬───────────┬──┘
                │ USB       │ USB/serial│ GPIO/I2C
          ┌─────┴────┐ ┌────┴─────┐ ┌───┴──────────┐
          │  LiDAR   │ │  Motor   │ │  IMU + depth │
          │ (RPLidar)│ │ ctrl MCU │ │   camera     │
          └──────────┘ └────┬─────┘ └──────────────┘
                            │ PWM + encoder feedback
                       ┌────┴─────┐
                       │ 2× geared│  ← differential drive
                       │  motors  │
                       └──────────┘
```

**Key design choice — split the brain from the muscles.** The Jetson does high-level thinking (mapping, path planning). A small **microcontroller** (your Arduino, or better an ESP32 / Teensy) handles real-time motor PWM and reads wheel encoders, talking to the Jetson over USB serial (via `micro-ROS` or a simple serial protocol). This "high-level computer + real-time microcontroller" split is how essentially all real robots are built — and it reuses skills you already have.

---

## 3. Bill of materials (draft)

| Part | Purpose | Approx. cost | Notes |
|---|---|---|---|
| Jetson Orin Nano Super Dev Kit | Brain | $249 | Or Pi 5 8 GB @ ~$199 |
| NVMe SSD (256 GB, M.2 2280) | OS + storage | ~$30 | Jetson boots much better from SSD than SD |
| 2× DC gear motors w/ encoders (e.g. 12 V, ~200 RPM) | Drive + odometry | ~$30 | Encoders are **essential** for odometry — don't skip |
| Motor driver (TB6612FNG or L298N; TB6612 preferred) | Drive motors | ~$8 | TB6612 is more efficient than L298N |
| ESP32 or Teensy 4.0 | Real-time motor/encoder MCU | ~$10 | Your Arduino works too; ESP32 adds wireless |
| Robot chassis (2WD/4WD w/ caster) | Body | ~$25 | Or laser-cut/3D-print your own |
| RPLidar C1 or A1 | 360° 2D scanning (SLAM) | ~$100 | The upgrade from your spun VL53L1X |
| IMU (BNO055 or MPU-9250) | Orientation / sensor fusion | ~$15–30 | BNO055 does fusion on-chip (easier) |
| Depth camera (optional, Phase 3+) | Obstacle detection, later AI | ~$0–250 | Skip at first; add Intel RealSense/OAK later |
| 3S/4S LiPo or 12 V battery pack + BEC | Power | ~$30 | Separate clean 5 V for the Jetson |
| Buck converter (5 V/5 A) | Power the Jetson cleanly | ~$8 | Jetson is picky about power — don't under-spec |
| Wiring, standoffs, switch, fuse | Assembly | ~$15 | Add an inline fuse on the battery |

**Rough first-build budget:** ~$500–550 with the Jetson and RPLidar. You can shave ~$150 by starting with the Pi 5 8 GB and reusing your existing Arduino as the motor MCU, deferring the depth camera.

---

## 4. Software stack

- **OS:** Ubuntu (JetPack on Jetson / Ubuntu Server on Pi).
- **Middleware:** **ROS 2** (use the current LTS — Jazzy Jalisco; Humble if a tutorial you follow needs it). This is the non-negotiable core.
- **Robot description:** URDF model of your rover (link/joint dimensions, sensor positions).
- **Motor firmware:** `micro-ROS` on the ESP32/Teensy, or a lightweight serial bridge, exposing velocity commands + publishing encoder odometry.
- **Odometry + fusion:** `robot_localization` (EKF) fusing wheel odometry + IMU.
- **Mapping:** `slam_toolbox` to build a map from the RPLidar.
- **Navigation:** `Nav2` for path planning + obstacle avoidance to a goal pose.
- **Visualization/sim:** **RViz** to see the map/sensors; **Gazebo** (or Isaac Sim) to test *before* touching hardware.

> Strong advice: build the whole thing in **simulation first**. A URDF rover in Gazebo running slam_toolbox + Nav2 lets you get 80% working with zero hardware risk, then you port to the real robot.

---

## 5. Build phases (milestones)

Each is a checkpoint that works on its own — don't move on until the current one does.

1. **Bring-up.** Flash the Jetson (JetPack) to SSD, install ROS 2, confirm `ros2 topic list` works. *Milestone: a working ROS 2 machine.*
2. **Teleop.** Wire motors + driver + encoder MCU. Drive the robot with a keyboard/gamepad over ROS 2. *Milestone: it moves on command.*
3. **Odometry.** Publish wheel odometry + IMU; fuse with `robot_localization`. Drive it and watch its estimated pose in RViz. *Milestone: the robot knows roughly where it is.*
4. **Perception.** Bring up the RPLidar in ROS 2; see the live scan in RViz. *Milestone: it senses the room.*
5. **Mapping (SLAM).** Run `slam_toolbox`; drive it around to build a map. *Milestone: a saved map of your room.*
6. **Autonomous navigation.** Run `Nav2`; set a goal pose in RViz and let it plan + drive there, avoiding obstacles. *Milestone: it goes somewhere on its own. This is the whole phase's payoff.*
7. **Polish.** Tune costmaps, recovery behaviors, and speed. Optionally add the depth camera for better obstacle detection.

Realistic timeline for a focused beginner: **6–12 weeks**, most of it in Phases 1–2 (setup + firmware) and Phase 6 (Nav2 tuning).

---

## 6. What to learn alongside (so it's not just copy-paste)

- **ROS 2 basics:** nodes, topics, services, `tf2`, launch files. Do the official ROS 2 beginner tutorials end-to-end first.
- **PID control** for closed-loop wheel velocity from encoder feedback.
- **Coordinate frames / `tf`** — the concept that trips up most beginners; worth slowing down on.
- **Linux + Python + a little C++.**

---

## 7. Open questions for you (to finalize this draft)

- **Board:** go Jetson (recommended) or start cheaper on the Pi 5?
- **Budget ceiling:** is ~$500 fine, or should I design a ~$300 minimal version reusing your Arduino + spun-VL53L1X instead of an RPLidar?
- **Buy vs. build the chassis:** kit chassis (faster) or fabricate your own (more learning)?
- **Depth camera:** include now or defer to Phase 3?

Answer those and I'll turn this draft into the finalized build guide — wiring diagrams, exact parts links, the URDF, and the ROS 2 launch files — the same depth as your lidar guide.
