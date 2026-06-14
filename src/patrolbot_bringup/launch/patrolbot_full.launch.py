from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os

def generate_launch_description():
    map_file = os.path.join(os.path.expanduser('~'), 'maps', 'patrolbot_map.yaml')

    return LaunchDescription([

        # 1. Gazebo
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                '/opt/ros/humble/share/turtlebot3_gazebo/launch/turtlebot3_world.launch.py'
            )
        ),

        # 2. Navigation Nav2 + RViz (délai 5s)
        TimerAction(period=5.0, actions=[
            ExecuteProcess(
                cmd=[
                    'ros2', 'launch', 'turtlebot3_navigation2',
                    'navigation2.launch.py',
                    f'map:={map_file}',
                    'use_sim_time:=True'
                ],
                output='screen'
            )
        ]),

        # 3. Nodes PatrolBot (délai 15s)
        TimerAction(period=15.0, actions=[
            Node(
                package='patrolbot_perception',
                executable='obstacle_detector',
                name='obstacle_detector',
                output='screen'
            ),
            Node(
                package='patrolbot_ai',
                executable='ai_planner',
                name='ai_planner',
                output='screen'
            ),
            Node(
                package='patrolbot_recovery',
                executable='recovery_node',
                name='recovery_node',
                output='screen'
            ),
            Node(
                package='patrolbot_delivery',
                executable='delivery_manager',
                name='delivery_manager',
                output='screen'
            ),
            Node(
                package='patrolbot_api',
                executable='api_server',
                name='api_server',
                output='screen'
            ),
        ]),
    ])
