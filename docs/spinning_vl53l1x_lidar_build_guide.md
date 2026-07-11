# DIY 3D LiDAR — Spinning VL53L1X + Point Cloud (Path A)

A beginner-friendly build guide that takes you from your existing 2D VL53L1X plotter to a 2-axis spinning scanner that produces a real 3D **point cloud**. Uses the Elegoo Mega kit and VL53L1X you already own, plus about $25–30 of extra parts.

> This is the low-cost, high-learning path. It mirrors the *architecture* of the pro "tilting laser" rigs (a rangefinder moved on two axes, scans stitched into a cloud) but with hardware you already have. Once this clicks, upgrading to a 360° LiDAR (RPLidar) or ROS + PCL is a much smaller step.

---

## 1. What you're building

A scanning head with **two axes of motion**:

- **Pan (azimuth)** — a stepper motor rotates the whole head horizontally.
- **Tilt (elevation)** — a small servo tips the VL53L1X sensor up and down.

At each (pan, tilt) position the sensor reports a distance. That triple — `azimuth, elevation, distance` — is one point in space. Sweep both axes across a grid and you collect thousands of points: a 3D point cloud of the room.

Your current 2D plot is the special case where tilt is always flat. Adding the tilt axis is what turns a flat slice into a 3D volume.

```
        tilt servo (elevation)
             \
              [VL53L1X]  ── measures distance r
              /
   ┌─────────────────┐
   │  turntable       │  ← stepper rotates this (azimuth)
   └───────┬─────────┘
           │ base: Arduino Mega + driver
```

---

## 2. How it works — the one equation that matters

Every reading is a point in **spherical coordinates**: a distance `r` at a horizontal angle (azimuth `θ`) and a vertical angle (elevation `φ`). To draw it you convert to **Cartesian** (x, y, z):

```
x = r * cos(φ) * cos(θ)
y = r * cos(φ) * sin(θ)
z = r * sin(φ)
```

- `θ` (azimuth) comes from the stepper position.
- `φ` (elevation) comes from the servo angle.
- `r` is the VL53L1X distance.

That's the whole idea. The mechanics below just move the sensor to known angles; the Python at the end applies this equation to every reading.

---

## 3. Bill of materials

| Part | Purpose | Approx. cost | Notes |
|---|---|---|---|
| Arduino Mega 2560 (Elegoo) | Controller | have it | Any Uno/Mega works |
| VL53L1X ToF sensor | Distance | have it | ~4 m range, 27° cone |
| 28BYJ-48 stepper + ULN2003 driver | Pan/azimuth axis | ~$5 | Comes in most kits; geared, ~2038 steps/rev |
| SG90 or MG90S micro servo | Tilt/elevation axis | ~$3 | MG90S (metal gear) is steadier |
| Capsule slip ring, 6+ wire, 12 mm | Pass wires across spinning joint | ~$10 | **Optional** — see two mounting options below |
| Lazy-susan bearing or 3D-printed turntable | Smooth rotation | ~$5 | Or print/laser-cut a disc |
| 5 V supply (2 A) | Power servo + stepper cleanly | ~$5 | Don't run the servo off the Arduino 5V pin |
| Jumper wires, breadboard | Wiring | have it | |
| Double-sided tape / M2 screws / hot glue | Mounting | have it | |

Total new spend: roughly **$25–30**.

---

## 4. Two ways to handle the spinning wires

The one genuinely fiddly part of a spinning sensor is getting power and I²C **across a joint that rotates**. Pick one:

**Option 1 — No slip ring (start here).** Don't spin fully around. Pan back and forth across a limited arc (e.g. 0°→300°, then unwind back to 0°). The sensor wires simply flex and untwist each pass. Zero extra parts, dead simple, perfect for learning. Downside: you lose a slice of coverage behind the mount and scanning is a little slower.

**Option 2 — Slip ring (upgrade).** A capsule slip ring lets the head spin continuously 360°, forever, without twisting wires. Route the VL53L1X's 4 wires (VIN, GND, SDA, SCL) plus the servo's 3 wires through it. This is exactly why the pro ForgeHub project ships a "Slip Ring Housing" STL — same problem, same solution. Do this once Option 1 works.

Start with Option 1. Everything below works for both; only the pan range differs.

---

## 5. Mechanical assembly

1. **Base.** Mount the 28BYJ-48 stepper pointing up. Fix the ULN2003 driver and Arduino to the base plate.
2. **Turntable.** Attach a disc (lazy-susan bearing or printed turntable) to the stepper shaft. This is your rotating platform.
3. **Tilt bracket.** On the turntable, mount the SG90 servo on its side so its horn tilts up/down. Attach the VL53L1X to the servo horn, sensor window facing outward.
4. **Center the sensor** over the axis of rotation as closely as you can — it keeps the math clean (otherwise you add a small offset for the lever arm). Close is fine for a first build.
5. **Wires.** For Option 1, leave a gentle service loop of wire so it can flex. For Option 2, run them through the slip ring bore.

Keep the sensor's tiny window clean and unobstructed — no glue or tape over it.

---

## 6. Wiring

**VL53L1X (I²C):**

| Sensor | Arduino Mega |
|---|---|
| VIN | 5V |
| GND | GND |
| SDA | pin 20 (SDA) |
| SCL | pin 21 (SCL) |

> On an Uno, SDA/SCL are A4/A5. On the Mega they're pins 20/21.

**28BYJ-48 via ULN2003:** IN1→pin 8, IN2→pin 9, IN3→pin 10, IN4→pin 11. Power the ULN2003 from your **external 5 V** supply, not the Arduino.

**SG90 servo:** signal→pin 6, V+→external 5 V, GND→common ground.

**Critical:** tie all grounds together (Arduino GND, servo GND, stepper GND, supply GND). Powering the servo and stepper from the Arduino's onboard 5 V will cause brownouts and random resets — use the external supply and share ground.

---

## 7. Arduino sketch

Install the **Pololu VL53L1X** library (Library Manager → search "VL53L1X" by Pololu). This sketch walks a grid: for each pan step it sweeps the tilt servo through a range, reads distance at each stop, and prints `azimuth_deg,elevation_deg,distance_mm` over serial at 115200 baud.

```cpp
#include <Wire.h>
#include <VL53L1X.h>
#include <Servo.h>
#include <Stepper.h>

// ---------- Pan (28BYJ-48) ----------
const int STEPS_PER_REV = 2038;      // 28BYJ-48 with ULN2003 (4-step sequence)
Stepper panMotor(STEPS_PER_REV, 8, 10, 9, 11);  // note IN order: 8,10,9,11

const float PAN_MAX_DEG   = 300.0;   // Option 1: sweep arc, then unwind
const float PAN_STEP_DEG  = 2.0;     // horizontal resolution

// ---------- Tilt (servo) ----------
Servo tiltServo;
const int   TILT_PIN      = 6;
const int   TILT_MIN_DEG  = 60;      // servo angle at lowest look-down
const int   TILT_MAX_DEG  = 120;     // servo angle at highest look-up
const int   TILT_STEP_DEG = 2;       // vertical resolution
const int   TILT_CENTER   = 90;      // servo angle that points straight out (elevation 0)

VL53L1X sensor;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(400000);

  sensor.setTimeout(500);
  if (!sensor.init()) {
    Serial.println("# VL53L1X init failed");
    while (1);
  }
  sensor.setDistanceMode(VL53L1X::Long);      // up to ~4 m
  sensor.setMeasurementTimingBudget(50000);   // 50 ms per reading
  sensor.startContinuous(50);

  tiltServo.attach(TILT_PIN);
  panMotor.setSpeed(10);                       // RPM

  Serial.println("# azimuth_deg,elevation_deg,distance_mm");
}

// convert degrees of pan into stepper steps
int degToSteps(float deg) {
  return (int)(deg / 360.0 * STEPS_PER_REV);
}

void scanColumn(float azimuthDeg) {
  for (int a = TILT_MIN_DEG; a <= TILT_MAX_DEG; a += TILT_STEP_DEG) {
    tiltServo.write(a);
    delay(120);                                // let servo settle
    uint16_t mm = sensor.read();               // blocking read
    if (sensor.timeoutOccurred()) return;
    float elevationDeg = (float)(a - TILT_CENTER);   // 0 = straight out
    Serial.print(azimuthDeg, 2); Serial.print(",");
    Serial.print(elevationDeg, 2); Serial.print(",");
    Serial.println(mm);
  }
}

void loop() {
  long stepsTaken = 0;                         // track EXACT steps so unwind matches
  // sweep out to PAN_MAX_DEG
  for (float az = 0; az <= PAN_MAX_DEG; az += PAN_STEP_DEG) {
    scanColumn(az);
    int s = degToSteps(PAN_STEP_DEG);
    panMotor.step(s);
    stepsTaken += s;
  }
  // unwind by the exact number of steps we took (Option 1: prevents wire twist/drift)
  panMotor.step(-stepsTaken);

  Serial.println("# frame_complete");
  delay(2000);        // pause between full scans
}
```

Notes:
- The stepper coil order `8,10,9,11` is the standard fix that makes a 28BYJ-48 turn smoothly with the `Stepper` library; if it just vibrates, that ordering is usually the culprit.
- If you later add a slip ring (Option 2), delete the "unwind" line and let `az` keep increasing / wrap past 360°.
- `elevationDeg = servoAngle - 90`. Calibrate `TILT_CENTER` so that the sensor points level when elevation reads 0.

---

## 8. Capture + build the point cloud (Python)

On your computer, log the serial stream to a CSV, then convert and view it.

**Step 1 — capture to CSV:**

```python
# capture.py  ->  python capture.py
import serial, sys

PORT = "COM3"        # Windows: check Device Manager. Mac/Linux: /dev/ttyUSB0 or /dev/ttyACM0
BAUD = 115200
OUT  = "scan.csv"

ser = serial.Serial(PORT, BAUD, timeout=2)
with open(OUT, "w") as f:
    f.write("azimuth_deg,elevation_deg,distance_mm\n")
    print("Logging... press Ctrl+C after '# frame_complete'")
    try:
        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if not line or line.startswith("#"):
                print(line)
                if line == "# frame_complete":
                    break
                continue
            f.write(line + "\n")
    except KeyboardInterrupt:
        pass
print("Saved", OUT)
```

**Step 2 — convert to XYZ and view:**

```python
# view.py  ->  pip install open3d numpy   then   python view.py
import numpy as np, open3d as o3d

data = np.genfromtxt("scan.csv", delimiter=",", names=True)
az  = np.radians(data["azimuth_deg"])
el  = np.radians(data["elevation_deg"])
r   = data["distance_mm"] / 1000.0            # mm -> meters

# drop invalid/out-of-range readings
mask = (r > 0.04) & (r < 4.0)
az, el, r = az[mask], el[mask], r[mask]

# spherical -> cartesian (the one equation from section 2)
x = r * np.cos(el) * np.cos(az)
y = r * np.cos(el) * np.sin(az)
z = r * np.sin(el)

pts = np.column_stack((x, y, z))
pc = o3d.geometry.PointCloud()
pc.points = o3d.utility.Vector3dVector(pts)

# color by height for readability
zc = (z - z.min()) / (np.ptp(z) + 1e-9)
pc.colors = o3d.utility.Vector3dVector(np.column_stack((zc, 0.4*np.ones_like(zc), 1-zc)))

o3d.io.write_point_cloud("scan.ply", pc)      # open later in MeshLab/CloudCompare
o3d.visualization.draw_geometries([pc])       # interactive: drag to rotate
```

Run `capture.py`, let one full frame complete, then `view.py`. You'll get an interactive, rotatable 3D point cloud, plus a `scan.ply` you can open in CloudCompare or MeshLab.

---

## 9. Tuning and gotchas

- **Noisy / jumpy points:** increase `setMeasurementTimingBudget` (e.g. 100000 = 100 ms) and the settle `delay` after each servo move. Slower but cleaner.
- **Servo jitter:** power it from the external 5 V, not the Arduino; add a 470–1000 µF capacitor across the servo's 5 V/GND.
- **Stepper only buzzes:** wrong coil order — keep `8, 10, 9, 11`.
- **Everything resets randomly:** grounds not shared, or too much load on Arduino 5 V. Use the external supply.
- **Cloud looks "smeared":** the sensor isn't centered on the rotation axis, or the servo hasn't settled before reading. Center it better, increase settle delay.
- **Resolution vs. speed:** `PAN_STEP_DEG` and `TILT_STEP_DEG` set density. 2° is a good start; drop to 1° once it works. Total points ≈ (PAN_MAX / PAN_STEP) × (tilt range / TILT_STEP).
- **Slight azimuth scale error:** 2° of pan rounds to 11 steps ≈ 1.94°, so the logged azimuth drifts a few percent from the true mechanical angle across a wide sweep. Fine for a first cloud; for accuracy, compute azimuth from cumulative steps (`az = stepsTaken / 2038.0 * 360`) instead of the commanded value.
- **Range limits:** the VL53L1X tops out near 4 m and has a ~27° cone, so fine detail beyond ~2 m blurs. That's the sensor, not your build — it's the reason to move to an RPLidar later.

---

## 10. Where this leads (toward the humanoid goal)

Once you have a clean cloud, natural next steps, each a small hop:

1. **Better sensor:** swap the spun VL53L1X for an **RPLidar A1/C1** (360° 2D out of the box) on the same tilt axis → far denser clouds. This is essentially the ForgeHub project at 1/10th the cost.
2. **Real-time streaming** instead of one-frame-at-a-time.
3. **ROS 2 + RViz/PCL:** publish your points as a `PointCloud2` message. This is the ecosystem robots actually use, and it's built around exactly the data you're already producing — so your mental model transfers directly to a mobile/humanoid platform.
4. **SLAM:** once the sensor moves, mapping + localization is the bridge from "scanner" to "robot that knows where it is."

You're building the right muscle: sensor → geometry → point cloud → visualization is the same pipeline all the way up to the humanoid. Get Section 8 rendering a recognizable room and you've done the hard conceptual part.
