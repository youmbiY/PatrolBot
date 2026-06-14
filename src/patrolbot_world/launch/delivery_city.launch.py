import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    world_file = os.path.join(
        get_package_share_directory('patrolbot_world'),
        'worlds', 'delivery_city.world')

    return LaunchDescription([
        ExecuteProcess(
            cmd=['gazebo', '--verbose', world_file,
                 '-s', 'libgazebo_ros_factory.so',
                 '-s', 'libgazebo_ros_init.so',
                 '-s', 'libgazebo_map_creator.so'],
            output='screen'
        ),
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'waffle_pi',
                '-file', '/opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle_pi/model.sdf',
                '-x', '0', '-y', '0', '-z', '0.01'
            ],
            output='screen'
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': open('/opt/ros/humble/share/turtlebot3_gazebo/urdf/turtlebot3_waffle_pi.urdf').read()
            }],
            output='screen'
        ),
    ])
