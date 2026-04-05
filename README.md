# Autonomous Mobile Robot Navigation using Deep Reinforcement Learning (DRL)

## Problem Statement
Autonomous mobile robots need to navigate complex environments efficiently while avoiding obstacles.  
Traditional rule-based navigation systems are limited in dynamic and uncertain environments.  
Our project addresses the challenge of creating an intelligent navigation system that can learn from its environment and make real-time decisions.



## Tools and Software Used
- **Programming Language:** Python 3.x  
- **Simulation Environment:** Gazebo  
- **Robot Operating System:** ROS2  
- **Deep Reinforcement Learning Framework:** PyTorch  
- **Other Libraries:** NumPy, Gym, Matplotlib  



## Project Overview
This project develops an autonomous mobile robot capable of navigating a simulated environment using Deep Reinforcement Learning (DRL).  
The robot relies on LiDAR data to detect obstacles and make real-time navigation decisions.  
The project is structured into separate modules for LiDAR data processing, DRL training, trial environment testing, and a final merged code for full execution.



## Solution
We implemented a modular approach to solve the navigation problem:  

1. **LiDAR Data Processing:** `lidar_reder.py` reads and preprocesses LiDAR sensor data for obstacle detection.  
2. **DRL Agent Training:** `drl_training.py` trains a reinforcement learning agent in simulation to make navigation decisions.  
3. **Trial Environment Testing:** `drl_trial_env.py` evaluates the trained agent in a simulated environment to ensure safe navigation.  
4. **Final Merged Execution:** `final_code.py` combines all modules for complete autonomous navigation of the robot.  

This approach allows continuous learning and adaptation to dynamic environments, improving navigation performance over time.



## Project Modules
- **lidar_reder.py** → Reads LiDAR sensor data and processes it for navigation.  
- **drl_training.py** → Implements the DRL agent and trains it in a simulated environment.  
- **drl_trial_env.py** → Sets up a trial environment to test the trained DRL agent.  
- **final_code.py** → Merges all modules for final execution of the autonomous navigation system.



## How to Run
1. Install required Python packages:
   ```bash
  # pip install torch gym numpy matplotlib
  # python lidar_reder.py

##modules run in this order
python drl_training.py
python drl_trial_env.py
python final_code.py


##Future Work
1.Improve DRL training efficiency and stability
2.Add more complex simulated environments
3.Integrate the system with a real robot for practical testing
