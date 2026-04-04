import gymnasium as gym
from gymnasium import spaces
import numpy as np


class RobotEnv(gym.Env):
    def __init__(self):
        super(RobotEnv, self).__init__()

        # 30 LiDAR rays + goal angle
        self.observation_space = spaces.Box(low=-1, high=1, shape=(31,), dtype=np.float32)
        self.action_space = spaces.Discrete(30)  # 30 possible steering angles

        self.step_count = 0
        self.max_steps = 100

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0
        state = np.zeros(31, dtype=np.float32)
        return state, {}

    def step(self, action):
        self.step_count += 1

        # Simulate LiDAR
        lidar = np.random.rand(30).astype(np.float32)
        angles = np.linspace(-45, 45, 30)  # -45° to +45° field of view

        # Goal direction
        goal_angle = np.random.uniform(-45, 45)
        state = np.append(lidar, goal_angle)

        # Compute alignment for each ray
        alignment = 1 - np.abs(angles - goal_angle) / 45

        # Combine visibility and goal alignment
        score = lidar + alignment

        # Best angle
        best_index = np.argmax(score)
        best_angle = angles[best_index]

        # Reward
        if action == best_index:
            reward = 3
            reason = "Best angle chosen"
        else:
            reward = -1
            reason = "Not best angle"

        # Termination
        terminated = False
        truncated = self.step_count >= self.max_steps

        # Debug print every 20 steps
        if self.step_count % 20 == 0:
            print("\n==============================")
            print("Step:", self.step_count)
            print("LiDAR values:", np.round(lidar, 3))
            print("Angles (-45° to +45°):", np.round(angles, 1))
            print("Goal Angle:", round(goal_angle, 2))
            print("Alignment:", np.round(alignment, 3))
            print("Final Score:", np.round(score, 3))
            print("Best Angle:", round(best_angle, 2))
            print("Action Taken (angle):", round(angles[action], 2))
            print("Reward:", reward, "→", reason)
            print("==============================\n")

        return state, reward, terminated, truncated, {}
