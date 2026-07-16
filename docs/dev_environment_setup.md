# Dev Environment Setup — Ubuntu + ROS 2 on Windows (via WSL2)

Goal: get a working robotics development environment on your RTX 4060 laptop without dual-booting or repartitioning. We use **WSL2** (Windows Subsystem for Linux), which runs **Ubuntu 24.04** inside Windows and borrows disk space as needed — ideal given limited free storage.

**What we're installing:** Ubuntu 24.04 (in WSL2) → ROS 2 **Jazzy Jalisco** (the current LTS) → verify it works.

**Time:** ~45–60 minutes, most of it unattended downloads.
**Disk needed:** ~10–15 GB for this setup. Fine within 50 GB free (leave room; AI models come later).

> Canonical references if a command ever drifts: WSL — https://learn.microsoft.com/windows/wsl/install ; ROS 2 Jazzy — https://docs.ros.org/en/jazzy/Installation.html

---

## Part 1 — Install WSL2 + Ubuntu 24.04

1. Open **PowerShell as Administrator** (Start menu → type "PowerShell" → right-click → Run as administrator).
2. Install WSL with Ubuntu 24.04:

   ```powershell
   wsl --install -d Ubuntu-24.04
   ```

3. **Reboot** your PC when it asks (or reboot manually if it doesn't).
4. After reboot, an Ubuntu terminal window opens by itself and says "Installing, this may take a few minutes." When done, it asks you to create a Linux user:
   - **Enter a username** (lowercase, no spaces — e.g. `viktor`).
   - **Enter a password** (you won't see characters as you type — that's normal). Remember it; you'll use it for `sudo`.

You now have Ubuntu running inside Windows. To reopen it later: Start menu → "Ubuntu", or type `wsl` in any terminal.

> If `wsl --install` says it's not recognized, your Windows may need updating (Settings → Windows Update), then retry.

---

## Part 2 — Update Ubuntu

In the Ubuntu terminal, refresh the package lists and upgrade:

```bash
sudo apt update && sudo apt upgrade -y
```

Enter your Linux password when prompted. This may take a few minutes.

---

## Part 3 — Install ROS 2 Jazzy

Run these blocks in the Ubuntu terminal, one at a time.

### 3a. Set locale (UTF-8)

```bash
sudo apt update && sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

### 3b. Enable the required repositories

```bash
sudo apt install software-properties-common -y
sudo add-apt-repository universe -y
sudo apt update && sudo apt install curl -y
```

### 3c. Add the ROS 2 apt source

```bash
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo $VERSION_CODENAME)_all.deb"
sudo apt install /tmp/ros2-apt-source.deb -y
```

### 3d. Install ROS 2 (desktop = includes RViz + demos)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install ros-jazzy-desktop -y
```

This is the big download (a few GB). Let it run.

> Tight on space? Use `ros-jazzy-ros-base` instead of `ros-jazzy-desktop` (no GUI tools). But `desktop` is recommended — you'll want RViz.

### 3e. Install build tools (for later, when you write packages)

```bash
sudo apt install ros-dev-tools -y
```

---

## Part 4 — Make ROS 2 load automatically

So every new terminal knows about ROS 2, add it to your shell startup:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## Part 5 — Verify it works (the "hello world" of ROS 2)

Open **two** Ubuntu terminals (or two tabs).

Terminal 1 — a talker node:

```bash
ros2 run demo_nodes_cpp talker
```

Terminal 2 — a listener node:

```bash
ros2 run demo_nodes_py listener
```

If ROS 2 is working, the talker prints "Publishing: Hello World: 1, 2, 3..." and the listener prints "I heard: Hello World: 1, 2, 3...". That means two independent programs are passing messages over ROS 2 topics — the exact mechanism your whole robot runs on. Press `Ctrl+C` in each to stop.

---

## Part 6 — GUI apps (RViz, Gazebo)

Good news: Windows 11 + WSL2 supports Linux GUI apps out of the box (WSLg), no extra setup. Test it:

```bash
rviz2
```

An RViz window should open on your Windows desktop. Close it when satisfied. (If it errors about display, make sure Windows is updated — WSLg ships with recent Windows 11.)

---

## Storage tips (you have ~50 GB free)

- This setup uses ~10–15 GB. You're fine for now.
- The disk hog comes later: **AI model files** in Phase 5 (several GB each). Before then, either free up space (uninstalling one or two large games usually frees 30–100 GB) or add a cheap external USB SSD for models/datasets.
- Check WSL's disk use anytime from PowerShell: `wsl --system df -h` isn't standard; instead run `df -h` inside Ubuntu.

---

## Where your files live (Windows <-> Ubuntu)

- Your Windows files are visible inside Ubuntu under `/mnt/c/...`
  e.g. this project: `/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot`
- For ROS 2 work it's faster to keep your ROS workspace *inside* the Linux filesystem (e.g. `~/ros2_ws`) rather than under `/mnt/c`. We'll set that up when we build the first package.

---

## Next steps

1. Do the official **ROS 2 beginner tutorials** (nodes, topics, `tf`) — https://docs.ros.org/en/jazzy/Tutorials.html
2. Then we create your robot's first ROS 2 package + the URDF, and start simulating in Gazebo before any hardware.

> Update BUILD_LOG.md with how this install went — especially anything that broke and how you fixed it.
