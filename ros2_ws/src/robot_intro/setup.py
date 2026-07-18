from setuptools import find_packages, setup

package_name = 'robot_intro'

setup(
    name=package_name,
    version='0.0.1',
    # find_packages locates our python code folder (robot_intro/)
    packages=find_packages(exclude=['test']),
    data_files=[
        # registers this package with ROS 2's index so `ros2 run` can find it
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        # installs package.xml alongside the package
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='viktor',
    maintainer_email='ultradshxpa@gmail.com',
    description='My first ROS 2 package: a node that drives the turtle (and one day, the real rover).',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        # This is the important part: it maps a COMMAND NAME you type after
        # `ros2 run robot_intro ...` to the python function that runs.
        #   'command_name = python_module.file:function'
        'console_scripts': [
            'turtle_driver = robot_intro.turtle_driver:main',
            'velocity_listener = robot_intro.velocity_listener:main',
            'my_first_node = robot_intro.my_first_node:main',
            'speed_ramp = robot_intro.speed_ramp:main',
            'wall_avoider = robot_intro.wall_avoider:main',
            'wall_avoider_proportional = robot_intro.wall_avoider_proportional:main',
            'go_to_goal = robot_intro.go_to_goal:main',
            'balance_controller = robot_intro.balance_controller:main',
        ],
    },
)
