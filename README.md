# Autonomous Robot — Build Journey

Building toward a fully autonomous robot, one working machine at a time. This repo documents the whole journey: hardware, firmware, ROS 2 code, and a running build log.

**Long-term goal:** an AI-driven autonomous robot.
**Current phase:** Phase 1 — a differential-drive wheeled rover that maps a room and navigates to a goal on its own.

---

## The roadmap

Each phase is a complete, working robot that teaches one hard skill. I don't move on until the current rung works.

| Phase | Goal | Status |
|---|---|---|
| 0 | Fundamentals: Arduino, sensors, a 2D lidar plotter, a spinning lidar to point cloud | done |
| 1 | **Wheeled autonomous rover: SLAM + Nav2 navigation** | in progress |
| 2 | ROS 2 mastery + simulation-first workflow | todo |
| 3 | Perception + autonomous navigation (depth camera, costmaps) | todo |
| 4 | Manipulation (a robot arm) | todo |
| 5 | The AI brain (vision-language model as high-level planner) | todo |
| 6 | Legs / humanoid locomotion | todo |

---

## Repo structure

```
autonomous-robot/
|-- README.md            <- you are here
|-- BUILD_LOG.md         <- dated log of what I did, what broke, how I fixed it
|-- LICENSE              <- MIT
|-- docs/                <- design docs and build guides
|-- hardware/            <- bill of materials, wiring, chassis notes
|-- urdf/                <- robot description files (body + sensor positions)
|-- firmware/            <- microcontroller code (ESP32 motor/encoder controller)
|-- ros2_ws/             <- ROS 2 workspace: nodes, launch files, config
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
 Jetson / laptop  -- ROS 2 -->  SLAM + Nav2  -->  velocity commands
        |                                              |
        `-------------->  ESP32 (micro-ROS)  --> motor driver --> motors
                              ^                                     |
                              `---------- encoders <----------------`
```

See `docs/wheeled_robot_systems_deep_dive.md` for the full explanation of how every part works together.

---

## Hardware (Phase 1)

Full bill of materials with prices in `hardware/BOM.md`. Headline parts: NVIDIA Jetson Orin Nano Super (or a repurposed Nvidia laptop for early phases), Slamtec RPLidar C1, Luxonis OAK-D Lite depth camera, DC gear motors with encoders, ESP32, 3D-printed chassis.

## Software

- **OS:** Ubuntu
- **Framework:** ROS 2 (Jazzy)
- **Mapping:** slam_toolbox
- **Navigation:** Nav2
- **Sensor fusion:** robot_localization (EKF)
- **Motor firmware:** micro-ROS on ESP32

---

## Progress checklist (Phase 1)

- [ ] Computer bring-up (Ubuntu + ROS 2 installed, `ros2 topic list` works)
- [ ] Motors + ESP32 + encoders on the bench (micro-ROS driving one motor)
- [ ] Chassis printed and assembled
- [ ] URDF modeled and visualized in RViz
- [ ] RPLidar publishing /scan in RViz
- [ ] IMU + wheel odometry fused (robot_localization)
- [ ] SLAM: a saved map of a room
- [ ] Nav2: robot drives to a goal autonomously
- [ ] Depth camera added to costmap (3D obstacle avoidance)

---

*Started 2026. Follow along in [BUILD_LOG.md](BUILD_LOG.md).*
