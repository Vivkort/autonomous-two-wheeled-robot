# Build Log

Newest entries at the top. Keep it honest — log what broke and how you fixed it, not just the wins. Future-you (and anyone reading this repo) learns the most from the debugging.

**Entry template:**
## 2026-07-20 — Craig V2 BALANCES
**Goal today:** Get craig2 standing on his own, and holding position.
**What I did:** Rebuilt the controller as LQR full-state feedback on torque (pitch, pitch rate, wheel velocity, wheel position) with the gains solved from the URDF's actual physics instead of guessed, then added an integrator on position. Wrote docs/balancing_milestone.md with the full derivation and the gotcha list.
**What worked:** EVERYTHING. 55 s upright at 246 Hz, 0% torque saturation, 3.8° max lean. Drifted 7.25 m during start-up, turned around, and came home to **+0.004 m** — 4 mm from where he started. The integrator settled at 163.5 against a predicted 163.
**What broke / what I'm stuck on:** The two things that actually blocked this all along had nothing to do with control theory. (1) DART's wheel contact chattered — wheel velocity reversing sign on 32–70% of samples — which made velocity feedback useless. (2) A single `get_logger().info()` call was throttling the control loop to **10 Hz** while 222 IMU messages/sec arrived; the node was blocked on terminal I/O at ~0% CPU. Every gain tuned before that was compensating for a print statement. Also lost hours to Gazebo silently ignoring three separate SDF parameters, a ground plane with no friction defined, and spawning 5 cm too high so every run began with a bounce.
**How I fixed it (or next step to try):** Switched physics engine to bullet-featherstone (chatter 32–70% → 1%). Logged to a file handle instead of stdout (10 Hz → 246 Hz). Swapped JointState for Odometry (string arrays are expensive to deserialise in Python). Added integral action to kill the 8.5 m steady-state offset.
**Limit testing:** Recovers from **40°**, fails at **43°**. The traction ceiling is `arctan(μ) = 56°`, so he's at 77% of the physical maximum and 2.5× the LQR's 17° prediction — the linear model under-predicts because it's linearised about upright. Torque saturated only 9% of the time, so he runs out of traction, not motor. First attempt "failed" at 0.6 rad purely because `fall_limit` was set to 0.5 and the controller was switching itself off. **Next:** hardware build.
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
