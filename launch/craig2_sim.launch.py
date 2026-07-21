"""
craig2 full sim bringup — the balancing SLAM stack in one launch.

Brings up, in one shot, everything we spent the week wiring by hand:
  Gazebo (sensor_world) · robot_state_publisher · joint_state_publisher ·
  ros_gz bridge (7 topics + the /tf and /odom remaps) · balance_controller ·
  scan_gate · slam_toolbox · RViz.  Nav2 is optional (nav2:=true).

KEY SEQUENCING: Gazebo starts running, but craig2 is spawned 7 s LATE, on a
timer. That is deliberate — the controller, bridge and gate come up first, so
the instant craig2 appears the controller is already catching him. Spawn him
at t=0 and he falls before anything is listening. This is the automated version
of the "controller before play" rule.

PREREQUISITES (one-time, see docs/run_balancer.md):
  ~/balancer.urdf      symlink -> urdf/balancer.urdf   (space-free path for gz)
  ~/sensor_world.sdf   symlink -> worlds/sensor_world.sdf
  ~/.rviz2/craig2.rviz the RViz config you saved (Map + LaserScan + RobotModel)

RUN IT (source the workspace first):
  cd "/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot"
  source install/setup.bash
  ros2 launch launch/craig2_sim.launch.py            # mapping stack
  ros2 launch launch/craig2_sim.launch.py nav2:=true # + Nav2

The six single-node scripts in scripts/ still exist — use those when something
breaks and you need one node's output in its own terminal. This file is for
when it already works and you just want it up.
"""
import os
from launch import LaunchDescription
from launch.actions import (ExecuteProcess, TimerAction, DeclareLaunchArgument,
                            IncludeLaunchDescription)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

HOME = os.path.expanduser('~')
WORLD = os.path.join(HOME, 'sensor_world.sdf')        # space-free symlink for gz
URDF = os.path.join(HOME, 'balancer.urdf')            # space-free symlink
RVIZ = os.path.join(HOME, '.rviz2', 'craig2.rviz')

REPO = '/mnt/c/Users/ultra/OneDrive/Documents/Engineering Projects/autonomous-robot'
SLAM_PARAMS = os.path.join(REPO, 'config', 'slam_params.yaml')
NAV2_PARAMS = os.path.join(REPO, 'config', 'nav2_params.yaml')


def generate_launch_description():
    use_sim = {'use_sim_time': True}

    with open(URDF, 'r') as f:
        robot_description = f.read()

    nav2_arg = DeclareLaunchArgument(
        'nav2', default_value='false',
        description='also bring up Nav2 (navigation_launch.py)')

    # Gazebo, running. craig2 is NOT in the world yet - he's spawned on a timer.
    gazebo = ExecuteProcess(cmd=['gz', 'sim', '-r', WORLD], output='screen')

    # base_link -> imu_link / lidar_link (static) and /robot_description for RViz.
    robot_state_publisher = Node(
        package='robot_state_publisher', executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}, use_sim],
        output='screen')

    # Zeros for the continuous wheel joints so their frames exist - kills the
    # red left_wheel/right_wheel "No transform" in RViz. Purely cosmetic.
    joint_state_publisher = Node(
        package='joint_state_publisher', executable='joint_state_publisher',
        parameters=[use_sim], output='screen')

    # 7 topics + the two remaps. tf -> /tf, odometry -> /odom.
    bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        arguments=[
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/model/craig2/joint/left_wheel_joint/cmd_force@std_msgs/msg/Float64]gz.msgs.Double',
            '/model/craig2/joint/right_wheel_joint/cmd_force@std_msgs/msg/Float64]gz.msgs.Double',
            '/model/craig2/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/model/craig2/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        remappings=[
            ('/model/craig2/tf', '/tf'),
            ('/model/craig2/odometry', '/odom'),
        ],
        output='screen')

    controller = Node(
        package='robot_intro', executable='balance_controller',
        parameters=[use_sim], output='screen')

    scan_gate = Node(
        package='robot_intro', executable='scan_gate',
        parameters=[use_sim], output='screen')

    # slam_toolbox is a LIFECYCLE node. Run it as a bare Node and it starts but
    # stays 'unconfigured' - it never subscribes to scans or publishes map->odom,
    # so no map frame ever appears (it still shows in `ros2 node list`, which is
    # what fooled us). Its own launch file performs the configure->activate
    # transitions, so include THAT instead of the raw node. This is exactly what
    # worked in the manual runs.
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('slam_toolbox'),
            'launch', 'online_async_launch.py')),
        launch_arguments={
            'slam_params_file': SLAM_PARAMS,
            'use_sim_time': 'true',
        }.items())

    rviz = Node(
        package='rviz2', executable='rviz2', arguments=['-d', RVIZ],
        parameters=[use_sim], output='screen')

    spawn = Node(
        package='ros_gz_sim', executable='create',
        arguments=['-file', URDF, '-name', 'craig2', '-z', '0.08'],
        output='screen')

    # The whole trick: everything that catches him is up before he exists.
    spawn_delayed = TimerAction(period=7.0, actions=[spawn])

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('nav2_bringup'),
            'launch', 'navigation_launch.py')),
        launch_arguments={
            'params_file': NAV2_PARAMS,
            'use_sim_time': 'true',
        }.items(),
        condition=IfCondition(LaunchConfiguration('nav2')))

    return LaunchDescription([
        nav2_arg,
        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        bridge,
        controller,
        scan_gate,
        slam,
        rviz,
        spawn_delayed,
        nav2,
    ])
