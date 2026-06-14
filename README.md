# PatrolBot — Autonomous Delivery Robot

[![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)](https://docs.ros.org/en/humble/)
[![Gazebo](https://img.shields.io/badge/Gazebo-Classic%2011-orange)](https://classic.gazebosim.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)

PatrolBot is an autonomous delivery robot simulation built on **ROS2 Humble**, featuring an AI-powered multi-criteria planner, a finite state machine for delivery missions, a REST/WebSocket API, and self-recovery capabilities.

---

## Preview

| Gazebo Simulation | RViz Navigation |
|:-----------------:|:----------------:|
| *Robot in custom urban environment* | *Path planning & localization* |

> **Screenshots to add**: Capture Gazebo with your city and RViz with the planned path.

---

## Features

| Module | Description | Status |
|--------|-------------|--------|
| **AI Planner** | Multi-criteria scoring (distance, obstacles, energy, risk) | ✅ |
| **Delivery Manager** | 8-state FSM with timeout (30-120s) & SHA-256 code verification | ✅ |
| **Navigation** | Nav2 (A* + DWB controller) with obstacle avoidance | ✅ |
| **API** | REST endpoints + WebSocket for real-time tracking (2 Hz) | ✅ |
| **Self-Recovery** | Automatic backup (0.3m) + spin (180°) when stuck | ✅ |
| **Custom World** | Urban environment (42m x 42m with roads, houses, vehicles) | ✅ |
| **SLAM** | Real-time mapping with SLAM Toolbox | ✅ |
| **Localization** | AMCL particle filter for pose estimation | ✅ |

---

## Tech Stack

| Component | Version |
|-----------|---------|
| **OS** | Ubuntu 22.04 LTS |
| **ROS2** | Humble Hawksbill |
| **Simulator** | Gazebo Classic 11 |
| **Robot** | TurtleBot3 Waffle Pi |
| **Navigation** | Nav2 (Navigation2) |
| **SLAM** | SLAM Toolbox |
| **Localization** | AMCL |
| **API** | FastAPI + WebSocket |

---

## Project Structure
patrolbot_ws/
├── src/
│ ├── patrolbot/ # Main orchestration node
│ ├── patrolbot_perception/ # LiDAR → obstacle density (36 sectors)
│ ├── patrolbot_ai/ # Multi-criteria scoring
│ ├── patrolbot_delivery/ # 8-state FSM delivery manager
│ ├── patrolbot_api/ # FastAPI server (port 5000)
│ ├── patrolbot_recovery/ # Self-recovery (backup + spin)
│ ├── patrolbot_world/ # Custom Gazebo world (delivery_city.world)
│ └── patrolbot_bringup/ # Launch files integration
├── maps/
│ ├── patrolbot_map.pgm # Occupancy grid map
│ └── patrolbot_map.yaml # Map metadata
├── nav2_params.yaml # Nav2 configuration
└── start_patrolbot.sh # One-command startup script

---

## Installation

```bash
# Install dependencies
sudo apt install ros-humble-desktop ros-humble-turtlebot3 \
  ros-humble-turtlebot3-simulations ros-humble-navigation2 \
  ros-humble-nav2-bringup ros-humble-slam-toolbox

# Build the workspace
cd ~/patrolbot_ws
colcon build --symlink-install
source install/setup.bash

---

##Launch
bash start_patrolbot.sh

---

##Send a Delivery Mission
curl -X POST http://localhost:5000/api/mission \
  -H "Content-Type: application/json" \
  -d '{"destination_x": 0.5, "destination_y": 0.3, "delivery_code": "1234"}'

---

##Authors

    Youmbi Youri Thibault

    N'faly Sangare

    Zakaria Nasr-Allah

Master IAOC — Université Ibn Tofail, Kénitra
Module: Systèmes Temps Réel
Academic Year: 2025-2026

