# Hardware Shopping List — Physical Craig

What's left to build the real robot. Prices are approximate US street prices (mid-2026). ✅ = bought/ordered.

> **Design update:** Craig is now a **self-balancing** robot (Segway-style) — it balances on two wheels *and* carries the sensors, rather than being a stable 3-wheeled rover. That changes three things: **no caster**, **beefier high-torque motors**, and the **IMU becomes central** (it's the balance sensor, not just an odometry helper).

## ✅ Already have
- **RPLidar C1** — 360° lidar (the "eyes")
- **Luxonis OAK-D Lite** — depth camera
- **RTX 4060 laptop** — compute (run ROS off-board over WiFi for now; a Jetson can come later)
- **3D printer** — for the chassis (just need filament)

## Parts

### Drivetrain
| Item | Notes | Status |
|---|---|---|
| 2× **JGB37-520 gear motor WITH encoder** (12V, 333 RPM) | Encoder version (6-wire). Comes with wheels. | ✅ ordered (AliExpress, ~2–4 wk ship) |
| Wheels + hubs (6 mm D-shaft) | Likely included with the motor kit | ✅ included w/ motors (verify) |
| ~~Caster~~ — not needed | Self-balancer stands on 2 wheels only | — |

### Control electronics
| Item | Notes | Status |
|---|---|---|
| **ESP32 dev board** | Real-time motor/encoder brain (micro-ROS) | ✅ ordered |
| **TB6612FNG** motor driver | Dual H-bridge; more efficient than L298N | ✅ ordered |
| **MPU6500** IMU (balance) | Fast raw gyro/accel for the PID balance loop | ✅ ordered |
| **BNO055** IMU (heading/nav) | Fused, drift-free orientation | ✅ ordered |

### Power
| Item | Notes | Status |
|---|---|---|
| **3S LiPo battery** (11.1V, ~2200 mAh) | Matches the 12V motors. Read LiPo safety below | ⬜ still needed |
| **LiPo balance charger** | Safe charging | ✅ ordered |
| **Buck converter** (5V / 5A) | Clean 5V rail for the ESP32 | ✅ ordered |

### Wiring & assembly
| Item | Notes | Status |
|---|---|---|
| Jumper wires, small perfboard/breadboard | | ⬜ still needed |
| XT60 connectors, inline fuse + holder | Fuse the battery! | ⬜ still needed |
| M2/M3 standoffs + screws | Mount the boards | ⬜ still needed |

**Still to get:** 3S LiPo battery, jumper wires/perfboard, hookup wire, XT60 + inline fuse holder, M2/M3 standoffs. (Electronics are basically done — motors, both IMUs, ESP32, driver, buck, charger all ✅.)

## ⚠️ LiPo safety (first-time LiPo)
- **Balance-charge only**, on a fireproof surface / LiPo bag, never unattended.
- Don't over-discharge (stop ~3.3V/cell) or puncture it.
- Add the **inline fuse** on the battery line.
- Prefer to avoid LiPo at first? A **USB power bank** can run the ESP32 + sensors, with a separate NiMH pack for the motors.

## Note on the design
A **single self-balancing robot** (Craig v2) — balances on two wheels *and* carries the sensors, on a tall, narrow 3D-printed frame.

## 🔧 Hardware-store / auto-parts run
General hardware store (Home Depot / Lowe's / ACE); *[auto]* items are better at an auto-parts store.

**Power & wiring**
- Small SPST rocker switch, ~5 A+ — main power cutoff — ✅ got it
- Inline blade-fuse holder + assorted fuses (5 A, 10 A) *[auto]* — ⬜ still needed
- Stranded hookup wire: 18 AWG (motor power) + 22 AWG (signals) *[auto]* — ⬜ still needed
- Heat-shrink tubing (+ electrical tape) — ✅ got heat-shrink

**Mounting & assembly**
- Zip ties (assorted) — ✅ got it
- Industrial Velcro strips (mount the battery) — ✅ got it
- Double-sided foam / VHB tape (mount boards & sensors) — ✅ got it
- Super glue or 2-part epoxy — ⬜ optional
- Fine sandpaper — ⬜ optional

**Tools (if you don't own them)**
- **Multimeter** (~$15–25) — essential for voltages / continuity / debugging
- Wire strippers/cutters, precision screwdrivers, needle-nose pliers
- Soldering iron + solder — for the motor/encoder leads

## Compute later (optional)
- **NVIDIA Jetson Orin Nano Super** (~$250–500) — only for on-board AI (Phase 5). The laptop covers everything until then.
