# PatrolBot — Autonomous Delivery Robot

[![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)](https://docs.ros.org/en/humble/)
[![Gazebo](https://img.shields.io/badge/Gazebo-Classic%2011-orange)](https://classic.gazebosim.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

PatrolBot is an autonomous delivery robot simulation built on **ROS2 Humble**, featuring an AI-powered multi-criteria planner, a finite state machine for delivery missions, a REST/WebSocket API, and self-recovery capabilities.

---

## Features

| Module | Description | Status |
|----------|----------|----------|
| AI Planner | Multi-criteria scoring (distance, obstacles, energy) | ✅ |
| Delivery Manager | 8-state FSM with timeout & code verification | ✅ |
| Navigation | Nav2 (A* + DWB) with obstacle avoidance | ✅ |
| API | REST endpoints + WebSocket for real-time tracking | ✅ |
| Self-Recovery | Automatic backup/spin when stuck | ✅ |
| Custom World | Urban environment (roads, houses, vehicles) | ✅ |

---

## Tech Stack

- **OS:** Ubuntu 22.04 LTS
- **ROS2:** Humble Hawksbill
- **Simulator:** Gazebo Classic 11
- **Robot:** TurtleBot3 Waffle Pi
- **Navigation:** Nav2 (SLAM Toolbox + AMCL)
- **API:** FastAPI + WebSocket

---

## Project Structure

```text
patrolbot_ws/
├── src/
│   ├── patrolbot_perception/   # LiDAR → obstacle density
│   ├── patrolbot_ai/           # Multi-criteria scoring
│   ├── patrolbot_delivery/     # FSM delivery manager
│   ├── patrolbot_api/          # FastAPI server
│   ├── patrolbot_recovery/     # Self-recovery
│   └── patrolbot_world/        # Custom Gazebo world
├── maps/                       # Occupancy grid maps
└── start_patrolbot.sh          # One-command launch
```

---

## Installation

```bash
sudo apt install ros-humble-desktop \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-simulations \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-slam-toolbox
```

```bash
cd ~/patrolbot_ws
colcon build --symlink-install
source install/setup.bash
```

---

## Launch

```bash
bash start_patrolbot.sh
```

---

## Send a Delivery Mission

```bash
curl -X POST http://localhost:5000/api/mission \
  -H "Content-Type: application/json" \
  -d '{"destination_x": 0.5, "destination_y": 0.3, "delivery_code": "1234"}'
```

---

## API Endpoints

| Method | Endpoint | Description |
|----------|----------|----------|
| GET | `/api/status` | Robot position & FSM state |
| POST | `/api/mission` | Send delivery mission |
| POST | `/api/code` | Submit verification code |
| WS | `/ws/tracking` | Real-time position stream |

---

## Performance Metrics

| Metric | Measured | Requirement |
|----------|----------|----------|
| Perception latency | 0.8 ms | < 100 ms |
| API latency | 15 ms | < 500 ms |
| WebSocket frequency | 2 Hz | > 1 Hz |
| Code verification | 8 ms | < 100 ms |
| Recovery (Backup) | 3.0 s | < 5 s |
| Recovery (Spin) | 2.0 s | < 5 s |

---

## Authors

- **Youmbi Youri Thibault**
- **N'faly Sangare**
- **Zakaria Nasr-Allah**

---

### Academic Information

**Master IAOC** 
Université Ibn Tofail, Kénitra

**Module:** Systèmes Temps Réel

**Academic Year:** 2025-2026
