# Autonomous Robot — Build Journey

Building toward a fully autonomous robot, one working machine at a time. This repo documents the whole journey: hardware, firmware, ROS 2 code, and a running build log.

**Long-term goal:** an AI-driven autonomous robot.
**Status:** 🎉 **Full autonomy achieved in simulation.** The robot — **Craig** — maps an unknown room with SLAM and navigates to clicked goals with Nav2, in Gazebo. Next up: assemble the physical robot and run the *same* ROS 2 stack on real hardware.

---

## The roadmap

Each phase is a complete, working robot that teaches one hard skill. I don't move on until the current rung works.

| Phase | Goal | Status |
|---|---|---|
| 0 | Fundamentals: Arduino, sensors, a 2D lidar plotter, a spinning lidar to point cloud | ✅ done |
| 1 | Wheeled rover: URDF, physics body, differential drive | ✅ done (sim) |
| 2 | ROS 2 mastery + simulation-first workflow | ✅ done |
| 3 | Perception + autonomous navigation: lidar → SLAM → Nav2 | ✅ done (sim) |
| — | *Hardware build: assemble Craig, run the same stack for real* | 🔨 next (parts arriving) |
| 4 | Manipulation (a robot arm) | ⬜ todo |
| 5 | The AI brain (vision-language model as high-level planner) | ⬜ todo |
| 6 | Legs / humanoid locomotion | ⬜ todo |
| side | Self-balancing two-wheeler (control theory: IMU + PID) | ⬜ planned |

Phases 1–3 are complete **in simulation**. The physical build is pending hardware (RPLidar C1, OAK-D Lite, compute, motors) — but the software is done and transfers directly.

---

## Repo structure

```
autonomous-robot/
|-- README.md            <- you are here
|-- BUILD_LOG.md         <- dated log of what I did, what broke, how I fixed it
|-- LICENSE              <- MIT
|-- docs/                <- design docs, build guides, tutorials, run instructions
|-- hardware/            <- bill of materials, wiring, chassis notes
|-- urdf/                <- Craig's description: chassis, wheels, caster, lidar, physics
|-- worlds/              <- Gazebo world files (the SLAM test room)
|-- launch/              <- ROS 2 launch files (one-command sim bringup)
|-- config/              <- SLAM (slam_toolbox) + Nav2 parameter files
|-- ros2_ws/             <- ROS 2 workspace: my nodes (turtlesim control exercises)
|-- firmware/            <- microcontroller code (ESP32 motor/encoder controller) [pending]
|-- scripts/             <- helper scripts (lidar capture + point-cloud viewer)
`-- media/               <- photos and videos of milestones
```

---

## The system at a glance

A two-brain design: a high-level computer thinks, a microcontroller handles real-time motor control.

```
 Sensors (lidar, depth cam, IMU, encoders)
        |
        v
 Compute  -- ROS 2 -->  SLAM + Nav2  -->  velocity commands (/cmd_vel)
        |                                              |
        `-------------->  motor controller  --> motor driver --> motors
                              ^                                     |
                              `---------- encoders <----------------`
```

In **simulation**, Gazebo plays the role of the sensors + motors. On **real hardware**, the RPLidar C1, OAK-D Lite, and an ESP32 motor controller take their place — and the ROS 2 stack above stays identical.

See `docs/wheeled_robot_systems_deep_dive.md` for how every part fits together.

---

## Software stack

- **OS:** Ubuntu 24.04 (via WSL2)
- **Framework:** ROS 2 Jazzy
- **Simulator:** Gazebo Harmonic (+ ros_gz bridge)
- **Mapping:** slam_toolbox
- **Navigation:** Nav2
- **Motor firmware (hardware):** micro-ROS on ESP32

Run the full sim with one command — see `docs/run_sim.md`.

## Hardware (pending)

Full bill of materials with prices in `hardware/BOM.md`. Headline parts: compute board (Jetson Orin Nano Super or an RTX-4060 laptop for dev), Slamtec RPLidar C1, Luxonis OAK-D Lite depth camera, DC gear motors with encoders, ESP32, 3D-printed chassis.

---

## Progress

### Simulation — ✅ complete
- [x] Ubuntu 24.04 + ROS 2 Jazzy installed (WSL2)
- [x] First ROS 2 package: publisher / subscriber nodes
- [x] Reactive control: wall-avoider → proportional control → go-to-goal controller
- [x] Craig modeled in URDF and visualized in RViz
- [x] Gazebo: physics body + differential-drive plugin (drives via `/cmd_vel`)
- [x] Simulated 360° lidar publishing `/scan`
- [x] Odometry tf (`odom → base_link`) bridged from Gazebo
- [x] SLAM: builds a live map of an unknown room (slam_toolbox)
- [x] Nav2: autonomously plans and drives to clicked goals, avoiding obstacles
- [x] One-command launch: Gazebo + robot + bridges + RViz

### Hardware — ⬜ pending (parts arriving)
- [ ] Assemble 3D-printed chassis + motors + ESP32
- [ ] micro-ROS firmware: motor control + wheel encoders
- [ ] RPLidar C1 driver → real `/scan`
- [ ] OAK-D Lite depth camera integration
- [ ] Run the same SLAM + Nav2 stack on the physical robot

### Side project — ⬜ planned
- [ ] Self-balancing two-wheeled robot (inverted-pendulum control: IMU + PID) — prep for humanoid balance

---

*Started 2026. Follow along in [BUILD_LOG.md](BUILD_LOG.md).*
