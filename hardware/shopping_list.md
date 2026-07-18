# Hardware Shopping List — Physical Craig

What's left to order to build the real robot. Prices are approximate US street prices (mid-2026) — verify on Amazon before ordering.

## ✅ Already have
- **RPLidar C1** — 360° lidar (the "eyes")
- **Luxonis OAK-D Lite** — depth camera
- **RTX 4060 laptop** — compute (run ROS off-board over WiFi for now; a Jetson can come later)
- **3D printer** — for the chassis (just need filament)

## 🛒 To order

### Drivetrain
| Item | Notes | ~Price |
|---|---|---|
| 2× DC gear motor **with quadrature encoder** (12V, ~100–200 RPM) | Encoders are essential for odometry — don't buy motors without them | ~$35 / pair |
| Wheels + hubs to fit the motor shafts | Some motors include these — check the listing first | ~$10 |
| Caster wheel or ball | The third contact point | ~$6 |

### Control electronics
| Item | Notes | ~Price |
|---|---|---|
| **ESP32 dev board** | The real-time motor/encoder brain (micro-ROS). ELEGOO 3-pack is great value | ~$16 (3-pack) |
| **TB6612FNG** motor driver | Dual H-bridge; more efficient than the older L298N | ~$8 |
| **IMU** — see note below | For balancing *and* better rover odometry | $7–30 |

### Power
| Item | Notes | ~Price |
|---|---|---|
| **3S LiPo battery** (11.1V, ~2200 mAh) | Matches the 12V motors. **New LiPo → read safety notes below** | ~$20 |
| **LiPo balance charger** | Required to charge LiPo safely (skip if you already own one) | ~$30 |
| **Buck converter** (5V / 5A) | Clean 5V rail for the ESP32 from the battery | ~$9 |

### Wiring & assembly
| Item | Notes | ~Price |
|---|---|---|
| Jumper wires, small perfboard/breadboard | | ~$10 |
| XT60 connectors, inline fuse + holder, power switch | Fuse the battery! | ~$10 |
| M2/M3 standoffs + screws | Mount the decks and boards | ~$8 |

**Estimated total: ~$150–170** (or ~$120 if you already have a LiPo charger).

## 💡 On the IMU (important — it serves both projects)
- **MPU6050** (~$7) — 6-axis, raw data, the *classic* choice for **self-balancing** robots. Cheap and everywhere. Get this for tomorrow's balancer.
- **BNO055** (~$30) — 9-axis with *onboard sensor fusion* (drift-free heading). The better pick for the **rover's** odometry (fuses with wheel encoders via robot_localization).
- Reasonable plan: grab an **MPU6050 now** for self-balancing; add a **BNO055** later for the rover if you want drift-free heading.

## ⚠️ LiPo safety (first-time LiPo)
- **Balance-charge only**, on a fireproof surface / LiPo bag, and never leave it charging unattended.
- Don't over-discharge (stop around 3.3V/cell) or puncture it.
- Add the **inline fuse** on the battery line.
- If you'd rather avoid LiPo entirely at first, a **USB power bank** can run the ESP32 + sensors, with a separate cheaper NiMH pack for the motors — safer, slightly bulkier.

## Shared with the self-balancing robot
Most of this list does double duty: the **motors, encoders, driver, ESP32, IMU, and battery** are exactly what the self-balancing two-wheeler needs too. The balancer just uses a different (taller, narrow) 3D-printed frame and leans on the IMU for balance. So ordering this set sets up **both** builds.

## Compute later (optional)
- **NVIDIA Jetson Orin Nano Super** (~$250–500) — only needed when you move on-board AI (Phase 5). The laptop covers everything until then.
