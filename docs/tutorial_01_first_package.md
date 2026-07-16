# Tutorial 1 — Your First ROS 2 Package (Publisher + Subscriber)

This is your first real ROS 2 code. By the end you'll have written (well, *understood*, since I pre-wrote it for you) a node that **drives the turtle in a circle**, and a second node that **listens** to those commands — the exact publish/subscribe pattern your rover will use to drive its wheels.

Everything is already created in your project at:
`autonomous-robot/ros2_ws/src/robot_intro/`

Your job in this tutorial is to **understand** each piece, then **build and run** it. Read the explanations, then do the commands in the "▶ DO THIS" boxes.

---

## 0. The mental model (read this first)

Three words you'll use forever:

- **Workspace** — a folder that holds one or more packages and knows how to build them. Ours is `ros2_ws`. (`ws` = workspace.)
- **Package** — a single unit of ROS software: some nodes, plus files describing its name and dependencies. Ours is `robot_intro`.
- **Node** — one running program that does one job. We have two: `turtle_driver` (sends commands) and `velocity_listener` (receives them).

Nodes talk by **publishing** and **subscribing** to **topics** (named channels). A **message** is the data that travels on a topic. We use the `Twist` message — the standard "how fast to move + how fast to turn" message.

You saw all of this live in turtlesim. Now you're writing it.

---

## 1. The package layout

Here's what's in `ros2_ws/src/robot_intro/` and what each file is for:

```
robot_intro/
├── package.xml        ← package's ID card: name, version, dependencies
├── setup.py           ← build/install instructions + node command names
├── setup.cfg          ← tells ROS where to install the runnable scripts
├── resource/
│   └── robot_intro    ← empty "marker" file so ROS can index the package
└── robot_intro/       ← the actual python code lives here
    ├── __init__.py    ← empty; marks this folder as a python package
    ├── turtle_driver.py       ← the PUBLISHER node
    └── velocity_listener.py   ← the SUBSCRIBER node
```

> Normally you'd generate this skeleton with one command:
> `ros2 pkg create --build-type ament_python robot_intro --dependencies rclpy geometry_msgs`
> I created it for you this time so we could focus on the code, but that's the command to remember for making your *next* package. `ament_python` means "this is a Python package"; the `--dependencies` list pre-fills package.xml.

---

## 2. package.xml — the package's ID card

This file tells ROS the package's name and, importantly, its **dependencies** (what it needs to run):

```xml
<depend>rclpy</depend>          <!-- the Python ROS library -->
<depend>geometry_msgs</depend>  <!-- provides the Twist message -->
<exec_depend>turtlesim</exec_depend>  <!-- we drive the turtle at runtime -->
```

Think of it like the "requirements" section of a recipe. When you (or a teammate) build the package on a fresh machine, ROS reads this to know what must be installed first. `<depend>` means "needed to build AND run"; `<exec_depend>` means "only needed to run."

---

## 3. setup.py — how it builds, and the node command names

Most of `setup.py` is boilerplate, but **one part is the most important thing in the whole package** — the `entry_points`:

```python
entry_points={
    'console_scripts': [
        'turtle_driver = robot_intro.turtle_driver:main',
        'velocity_listener = robot_intro.velocity_listener:main',
    ],
},
```

Read one line as: **`command_name = python_module.file : function`**.

So `turtle_driver = robot_intro.turtle_driver:main` means:
> "When someone runs `ros2 run robot_intro turtle_driver`, execute the `main()` function inside `robot_intro/turtle_driver.py`."

This is the bridge between a command you type and the code that runs. If you add a new node later, you add a line here — otherwise `ros2 run` can't find it.

---

## 4. The PUBLISHER — `turtle_driver.py`, line by line

The full file is in your folder; here are the parts that matter and exactly what each does.

**Imports:**
```python
import rclpy                          # ROS Client Library for Python
from rclpy.node import Node           # base class for every node
from geometry_msgs.msg import Twist   # the velocity message type
```
`rclpy` is how Python speaks ROS 2. `Node` is the class your node inherits from — it hands you all the ROS machinery (publishers, timers, logging) for free. `Twist` is the message describing motion.

**The node class + constructor:**
```python
class TurtleDriver(Node):
    def __init__(self):
        super().__init__('turtle_driver')
```
`super().__init__('turtle_driver')` registers the node with ROS under the name `turtle_driver` (this is the name you'd see in `ros2 node list`).

**Creating the publisher:**
```python
self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
```
This says "I will publish `Twist` messages on the topic `/turtle1/cmd_vel`." The `10` is the **queue size** — a small buffer in case the receiver is momentarily busy. `/turtle1/cmd_vel` is turtlesim's "drive" topic — the same one the teleop keys used.

**The timer:**
```python
timer_period = 0.5  # seconds
self.timer = self.create_timer(timer_period, self.send_command)
```
ROS nodes don't use `while True` loops. Instead you register a **timer**: "call `send_command` every 0.5 seconds." ROS handles the looping. This is the event-driven style all ROS code uses.

**The command itself:**
```python
def send_command(self):
    msg = Twist()          # all zeros to start
    msg.linear.x = 1.0     # forward speed
    msg.angular.z = 0.5    # turning speed -> combined = a circle
    self.publisher_.publish(msg)
```
A `Twist` has `linear` (x, y, z) and `angular` (x, y, z). For a ground robot you only ever use `linear.x` (forward/back) and `angular.z` (turn left/right). Setting both makes it arc — a circle. `publish(msg)` sends it out to anyone listening.

**The entry point:**
```python
def main(args=None):
    rclpy.init(args=args)   # start ROS communications
    node = TurtleDriver()   # build our node
    rclpy.spin(node)        # keep it alive, firing the timer forever
    ...
    rclpy.shutdown()        # clean up on exit
```
`rclpy.spin(node)` is the key line — it hands control to ROS, which keeps the node running and calls your timer/callbacks until you press Ctrl+C.

---

## 5. The SUBSCRIBER — `velocity_listener.py`

It's the mirror image. Instead of a publisher + timer, it has a **subscription** + **callback**:

```python
self.subscription = self.create_subscription(
    Twist,                 # message type to expect
    '/turtle1/cmd_vel',    # topic to listen on (SAME as the driver publishes)
    self.on_velocity,      # function to run when a message arrives
    10)                    # queue size
```

The magic: because both nodes use the **same topic and message type**, they connect automatically — no wiring, no addresses. The publisher doesn't even know the subscriber exists. That decoupling is the whole point of ROS.

```python
def on_velocity(self, msg):
    self.get_logger().info(f'heard -> forward: {msg.linear.x:.2f} ...')
```
`on_velocity` runs **every time a message arrives**, with the received `Twist` as `msg`. Here we just print it, but on your real robot this is where you'd convert the command into motor speeds.

---

## 6. ▶ DO THIS — build the package

Open your Ubuntu terminal and go to the workspace:

```bash
cd "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot/ros2_ws"
```

Build it:

```bash
colcon build
```

**What `colcon build` does:** colcon is ROS 2's build tool. It looks in `src/`, finds every package, and "installs" each one into a new `install/` folder (it also makes `build/` and `log/` folders — all three are git-ignored). Installing is what makes `ros2 run` able to find your nodes. You'll see something like `Finished <<< robot_intro`.

> First build is slow-ish; later builds are fast. If you edit a Python node, you often don't even need to rebuild thanks to `--symlink-install` (optional: `colcon build --symlink-install`).

Now **source** the workspace so this terminal knows about your new package:

```bash
source install/setup.bash
```

**What sourcing does:** it adds your freshly built package to the terminal's ROS search path. (Remember `source /opt/ros/jazzy/setup.bash` from setup? Same idea, but for *your* workspace.) You must run this in every new terminal where you want to use your package. Do it after every build.

---

## 7. ▶ DO THIS — run it and drive the turtle

You'll need **three terminals** (open the Ubuntu app three times). In each new one, first `cd` to the workspace and `source install/setup.bash`.

**Terminal 1 — the turtle simulator:**
```bash
ros2 run turtlesim turtlesim_node
```
The blue window with the turtle appears.

**Terminal 2 — YOUR driver node:**
```bash
source install/setup.bash        # if you haven't in this terminal
ros2 run robot_intro turtle_driver
```
🎉 The turtle starts driving in a circle — commanded by code you now understand. It logs "sending -> forward: 1.0, turn: 0.5" twice a second.

**Terminal 3 — YOUR listener node:**
```bash
source install/setup.bash
ros2 run robot_intro velocity_listener
```
It prints "heard -> forward: 1.00 units/s, turn: 0.50 rad/s" — it's receiving the very same messages the driver is sending to the turtle. Two of your nodes, communicating.

Press `Ctrl+C` in each terminal to stop.

---

## 8. ▶ DO THIS — inspect it with the tools you learned

While the driver is running, in a spare terminal (sourced):

```bash
ros2 node list       # -> /turtlesim, /turtle_driver, /velocity_listener
ros2 topic list      # -> /turtle1/cmd_vel and others
ros2 topic echo /turtle1/cmd_vel   # watch the raw Twist messages fly by
```

These are the same debugging tools from the turtlesim lesson — now pointed at *your* code.

---

## 9. How this becomes your real robot

The leap from turtle to rover is smaller than it looks:

- Change the topic from `/turtle1/cmd_vel` to `/cmd_vel` (the robot's standard drive topic).
- Instead of the listener just *printing*, it converts the `Twist` into left/right wheel speeds and sends them to the ESP32 motor controller.
- The `turtle_driver` (which sends fixed circles) gets replaced by **Nav2**, which sends smart `Twist` commands to steer around obstacles.

Same message. Same publish/subscribe. That's why this tiny package is the real foundation.

---

## 10. Recap — what you learned

- A **workspace** holds **packages**, which contain **nodes**.
- `package.xml` declares dependencies; `setup.py` `entry_points` map commands to code.
- A **publisher** sends messages on a **topic**; a **subscriber** receives them via a **callback**. They connect automatically by sharing a topic + message type.
- `rclpy.init` → create node → `rclpy.spin` → `rclpy.shutdown` is the skeleton of every Python node.
- `colcon build` then `source install/setup.bash` then `ros2 run <package> <node>`.

## Next steps

1. **Experiment:** change `linear.x` and `angular.z` in `turtle_driver.py`, rebuild, and watch the turtle's path change. (Try `angular.z = 0.0` for a straight line.)
2. Then: **Tutorial 2** — writing a node that *reacts* to sensor data (a subscriber that publishes), which is the core loop of an autonomous robot.

> Log your progress in BUILD_LOG.md, and push to GitHub: `git add .` / `git commit -m "First ROS 2 package: turtle_driver + velocity_listener"` / `git push`.
