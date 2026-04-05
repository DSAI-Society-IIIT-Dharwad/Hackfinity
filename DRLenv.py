import gymnasium as gym
from gymnasium import spaces
import numpy as np


class RobotEnv(gym.Env):
    def __init__(self):
        super(RobotEnv, self).__init__()

        # 30 LiDAR + goal angle
        self.observation_space = spaces.Box(low=0, high=1, shape=(31,), dtype=np.float32)
        self.action_space = spaces.Discrete(30)

        self.max_steps = 200
        self.step_count = 0

        # Robot state
        self.position = np.array([0.0, 0.0])
        self.goal = np.array([5.0, 0.0])  # fixed goal

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.step_count = 0
        self.position = np.array([0.0, 0.0])

        lidar = np.ones(30, dtype=np.float32)
        goal_angle = 0.0

        state = np.append(lidar, goal_angle)
        return state, {}

    def step(self, action):
        self.step_count += 1

        # 🔥 Convert action → angle
        angles = np.linspace(-1.0, 1.0, 30)
        turn = angles[action]

        # 🔥 Simulate movement
        dx = np.cos(turn) * 0.1
        dy = np.sin(turn) * 0.1

        old_distance = np.linalg.norm(self.goal - self.position)
        self.position += np.array([dx, dy])
        new_distance = np.linalg.norm(self.goal - self.position)

        # 🔥 Fake LiDAR (still simple for now)
        lidar = np.clip(np.random.rand(30), 0.1, 1.0)

        # 🔥 Goal direction
        goal_vector = self.goal - self.position
        goal_angle = np.arctan2(goal_vector[1], goal_vector[0])

        state = np.append(lidar, goal_angle)

        # 🔥 REWARD (THIS IS THE MOST IMPORTANT PART)
        reward = 0

        # Move toward goal
        if new_distance < old_distance:
            reward += 2
        else:
            reward -= 1

        # Collision penalty
        if np.min(lidar) < 0.2:
            reward -= 5

        # Goal reached
        if new_distance < 0.5:
            reward += 20

        # Termination
        terminated = new_distance < 0.5
        truncated = self.step_count >= self.max_steps

        return state, reward, terminated, truncated, {}
