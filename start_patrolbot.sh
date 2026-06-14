#!/bin/bash
source /opt/ros/humble/setup.bash
source ~/patrolbot_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi

echo "Lancement Gazebo"
gnome-terminal -- bash -c "source /opt/ros/humble/setup.bash && export TURTLEBOT3_MODEL=waffle_pi && ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py; bash"

sleep 8

echo "Lancement Navigation"
gnome-terminal -- bash -c "source /opt/ros/humble/setup.bash && source ~/patrolbot_ws/install/setup.bash && export TURTLEBOT3_MODEL=waffle_pi && ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$HOME/maps/patrolbot_map.yaml; bash"

sleep 15

echo "Lancement Nodes PatrolBot"
gnome-terminal -- bash -c "source /opt/ros/humble/setup.bash && source ~/patrolbot_ws/install/setup.bash && ros2 run patrolbot_perception obstacle_detector; bash"
gnome-terminal -- bash -c "source /opt/ros/humble/setup.bash && source ~/patrolbot_ws/install/setup.bash && ros2 run patrolbot_ai ai_planner; bash"
gnome-terminal -- bash -c "source /opt/ros/humble/setup.bash && source ~/patrolbot_ws/install/setup.bash && ros2 run patrolbot_recovery recovery_node; bash"
gnome-terminal -- bash -c "source /opt/ros/humble/setup.bash && source ~/patrolbot_ws/install/setup.bash && ros2 run patrolbot_delivery delivery_manager; bash"
gnome-terminal -- bash -c "source /opt/ros/humble/setup.bash && source ~/patrolbot_ws/install/setup.bash && ros2 run patrolbot_api api_server; bash"

echo "PatrolBot est prêt !"
