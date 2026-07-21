# Build Log

Newest entries at the top. Keep it honest — log what broke and how you fixed it, not just the wins. Future-you (and anyone reading this repo) learns the most from the debugging.

## 2026-07-21 — Craig V2 NAVIGATES (SLAM + Nav2 while balancing)
**Goal today:** Mount the lidar on craig2, port SLAM + Nav2 over from craig1, and get autonomous navigation working *while he balances*.
**What I did:** Mounted the lidar, re-derived the LQR gains for the new mass (K_pitch 4.932→4.997). Built the TF tree from scratch (map→odom→base_link→lidar_link) — craig2 had none because I dropped DiffDrive. Wrote a **scan-gate node** that only passes lidar scans when |pitch| < 7.2°. Fixed a phantom odometry velocity. Ported slam_params + nav2_params with balancer-specific accel/velocity limits. Wrote a one-command launch file (`scripts/sim.sh`) and a `reset_craig.sh`. Wrote docs/slam_nav2_milestone.md.
**What worked:** EVERYTHING, eventually. Clean map of the walled room — straight single walls, both obstacles as hollow shapes — and Nav2 drives him goal-to-goal without falling. One command brings the whole stack up.
**What broke / what I'm stuck on:** So much. (1) When he falls, the lidar (bolted to base_link) tilts from horizontal to vertical and sweeps floor+sky — slam scan-matches that garbage and *overwrites the good map*. A fallen balancer doesn't just stop mapping, it eats the map. (2) The odom velocity (twist.linear.x) was a phantom — read a near-constant ~0.11 m/s while he was actually rocking around standstill, so the velocity-damping term had nothing real to damp and he sat in a slow limit cycle. (3) He fell mid-run because a single `CONTROL RATE` print stalled the control loop for **2.5 seconds** (11 tip-doublings past unrecoverable). (4) My one-command launch file ran slam_toolbox as a bare node, which left it stuck `unconfigured` — it showed in `ros2 node list` but never subscribed to scans or published map→odom. Lost a while because "it's in the node list" fooled me. (5) A dozen stale-subscription issues: restart subscribers after you respawn what they publish, or they go quiet with no error.
**How I fixed it (or next step to try):** Scan gate on /scan → /scan_gated, threshold = arcsin(0.5 lidar height / 4.0 range) = 7.2°. Computed wheel velocity by differencing odom *position* (which is clean) instead of trusting the twist. Deleted the print, dropped real_time_factor to 0.5 to double delay tolerance. Made the launch **include** slam_toolbox's own `online_async_launch.py` so the lifecycle configure→activate actually happens. Capped lidar range to 4.0 m so a lean can't put the beam through a wall or into the floor.
**Next:** hardware build. On a real ESP32 none of the latency that dominated this exists, and real rubber has friction without a `<surface>` tag.
**Time spent:** ~big day, 6 hrs.

**Entry template:**
## 2026-07-20 — Craig V2 BALANCES!
**Goal today:** Get craig2 standing on his own, and holding position.
**What I did:** Rebuilt the controller as LQR full-state feedback on torque (pitch, pitch rate, wheel velocity, wheel position) with the gains solved from the URDF's actual physics instead of guessed, then added an integrator on position. Wrote docs/balancing_milestone.md with the full derivation and the gotcha list.
**What worked:** EVERYTHING. 55 s upright at 246 Hz, 0% torque saturation, 3.8° max lean. Drifted 7.25 m during start-up, turned around, and came home to **+0.004 m** - 4 mm from where he started. The integrator settled at 163.5 against a predicted 163.
**What broke / what I'm stuck on:** The two things that actually blocked this all along had nothing to do with control theory. (1) DART's wheel contact chattered - wheel velocity reversing sign on 32–70% of samples - which made velocity feedback useless. (2) A single `get_logger().info()` call was throttling the control loop to **10 Hz** while 222 IMU messages/sec arrived; the node was blocked on terminal I/O at ~0% CPU. Every gain tuned before that was compensating for a print statement. Also lost hours to Gazebo silently ignoring three separate SDF parameters, a ground plane with no friction defined, and spawning 5 cm too high so every run began with a bounce.
**How I fixed it (or next step to try):** Switched physics engine to bullet-featherstone (chatter 32–70% -> 1%). Logged to a file handle instead of stdout (10 Hz -> 246 Hz). Swapped JointState for Odometry (string arrays are expensive to deserialise in Python). Added integral action to kill the 8.5 m steady-state offset.
**Limit testing:** Recovers from **40°**, fails at **43°**. The traction ceiling is `arctan(μ) = 56°`, so he's at 77% of the physical maximum and 2.5× the LQR's 17° prediction - the linear model under-predicts because it's linearised about upright. Torque saturated only 9% of the time, so he runs out of traction, not motor. First attempt "failed" at 0.6 rad purely because `fall_limit` was set to 0.5 and the controller was switching itself off. **Next:** hardware build.
**Time spent:** ~10 hours

## 2026-07-18 & 19 — Balancing
**Goal today:** Try to get Craig V2 to balance on his own
**What I did:** Made Craig V2 (Two wheels, a bit taller), attempted to make him stand.
**What worked:** Craig could stand for about half a second
**What broke / what I'm stuck on:** Literally EVERYTHING
**How I fixed it (or next step to try):** I haven't fixed ANYTHING
**Time spent:** 8 hours

## 2026-07-17 — Simulation
**Goal today:** Get basic autonomy/pathfinding for Craig(my robot's name) and get his lidar up and running.
**What I did:** Modeled Craig's URDF - chassis, wheels, caster, lidar - with visuals, collision, and inertia; viewed in RViz. SLAM with slam_toolbox -> built a live map of a walled room. Added a simulated 360° lidar. Nav2 → autonomous navigation to clicked goals, routing around obstacles.
**What worked:** Everything basically in the end.
**What broke / what I'm stuck on:** Lidar rays wouldn't render in Gazebo (WSL quirk), but /scan published fine. SLAM spammed "failed to compute odom pose" -> params file wasn't loading (fell back to base_footprint). Root cause: ~ doesn't expand in key:=~/path. Nav2 whack-a-mole: collision_monitor needed observation_sources, docking_server needed dock_plugins. Typos: gz_frame -> gz_frame_id & lidar length 0.2 -> 0.02.
**How I fixed it (or next step to try):** Visualized lidar rays in RViz instead, used $HOME for SLAM. Added config sections to Nav2.
**Time spent:** ~6 hours
**Photo/video:** media/filename (**Add this later**)



## 2026-07-16 — Proportional heading controller
**Goal today:** Make the turtle not run into walls
**What I did:** Made the turtle turn away from wall proportionally and head in the right direcction
**What worked:** Turning worked
**What broke / what I'm stuck on:** Turtle kept jittering and orbiting in one spot, forgot indentations at places
**How I fixed it (or next step to try):** Tweaked Kp & Kv values and added proportionality to make the turtle move smoothly
**Time spent:** 3 hours


## 26-7-15 — Starting up
**Goal today:** Learn the basics of Ros2
**What I did:** Made my own node to publish stuff to turtlesim and make him accelerate. Decided to stick with laptop. Created speed_ramp.py
**What worked:** Most of the code for publishing and getting tools worked, kinda just looked at other nodes and did what they had.
**What broke / what I'm stuck on:** Forgot to add main() function, and was stuck figuring out what tools i could get from node
**How I fixed it (or next step to try):** Read documentation/ask Claude
**Time spent:** 2 hrs
---

## 26-7-13 Project Kickoff
**Goal today:** Set up the repo and plan Phase 1.
**What I did:** Created this repository, wrote the roadmap and the systems deep-dive in docs/.
**What worked:** Have a clear parts list and build order.
**What broke / stuck on:** Nothing yet — waiting on parts.
**Next step:** Decide laptop-vs-Jetson for prototyping; check the old laptop's GPU for CUDA.
**Time spent:** 3 hrs


<!-- Copy the template above for each new entry. -->
