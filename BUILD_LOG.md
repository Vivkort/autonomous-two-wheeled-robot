# Build Log

Newest entries at the top. Keep it honest — log what broke and how you fixed it, not just the wins. Future-you (and anyone reading this repo) learns the most from the debugging.

**Entry template:**
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
