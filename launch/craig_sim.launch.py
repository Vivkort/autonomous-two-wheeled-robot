import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

# Use the space-free symlinks in your home folder
HOME = os.path.expanduser('~')
URDF = os.path.join(HOME, 'my_robot.urdf')
WORLD = os.path.join(HOME, 'sensor_world.sdf')
RVIZ_CONFIG = os.path.join(HOME, '.rviz2', 'craig.rviz')


def generate_launch_description():
    # Read the URDF so robot_state_publisher can broadcast the robot's frames
    with open(URDF, 'r') as f:
        robot_description = f.read()

    use_sim_time = {'use_sim_time': True}

    # 1. Start Gazebo with our sensor world (-r = start running, not paused)
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', WORLD],
        output='screen',
    )

    # 2. robot_state_publisher: publishes tf + the /robot_description topic
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}, use_sim_time],
    )

    # 2b. joint_state_publisher: supplies wheel joint angles so their tf frames exist
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen',
        parameters=[use_sim_time],
    )

    # 3. Spawn Craig into Gazebo from the robot_description topic
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'craig', '-z', '0.1'],
        output='screen',
    )

    # 4. Bridge topics between ROS and Gazebo (cmd_vel, scan, clock)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        ],
        output='screen',
    )

    # 5. RViz, auto-loading your saved config
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', RVIZ_CONFIG],
        parameters=[use_sim_time],
    )

    # Give Gazebo a few seconds to come up before spawning Craig
    spawn_after_gazebo = TimerAction(period=4.0, actions=[spawn])

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        spawn_after_gazebo,
        bridge,
        rviz,
    ])
