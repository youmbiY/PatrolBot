# PatrolBot — Robot Autonome de Livraison

Projet de simulation ROS2 d'un robot de livraison autonome avec navigation 
intelligente, gestion de missions et auto-récupération.

## Stack technique
- Ubuntu 22.04 LTS
- ROS2 Humble Hawksbill
- Gazebo Classic 11
- TurtleBot3 Waffle Pi
- Nav2 + SLAM Toolbox
- FastAPI (API REST/WebSocket)

## Architecture
8 packages ROS2 : perception, AI planner, delivery manager (FSM), 
API REST, self-recovery, monde Gazebo personnalisé, bringup.

## Installation
\`\`\`bash
sudo apt install ros-humble-desktop ros-humble-turtlebot3 \
  ros-humble-turtlebot3-simulations ros-humble-navigation2 \
  ros-humble-nav2-bringup ros-humble-slam-toolbox
cd ~/patrolbot_ws
colcon build --symlink-install
source install/setup.bash
\`\`\`

## Lancer le projet
\`\`\`bash
bash start_patrolbot.sh
\`\`\`

## Envoyer une mission
\`\`\`bash
curl -X POST http://localhost:5000/api/mission \
  -H "Content-Type: application/json" \
  -d '{"destination_x": 0.5, "destination_y": 0.3, "delivery_code": "1234"}'
\`\`\`

## Auteurs
- [Youmbi Nkouakep Youri]
- [N'faly Sangare]
- [Zakaria Nasr-allah]
