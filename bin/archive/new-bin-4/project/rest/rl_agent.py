import numpy as np
import json
import os

class SimpleRLEnv:
    def reset(self):
        return {"question": ""}

    def step(self, action):
        reward = self._get_reward(action)
        next_state = {"question": ""}
        return next_state, reward, {}

class RLAgent:
    def __init__(self, env):
        self.env = env
        self.q_table_path = 'q_table.json'
        self.q_table = self.load_q_table()

    def load_q_table(self):
        if not os.path.exists(self.q_table_path):
            print(f"Q-table file {self.q_table_path} does not exist. Initializing new Q-table.")
            return {}

        try:
            with open(self.q_table_path, 'r') as f:
                q_table = json.load(f)
                #print(f"Loaded Q-table from {self.q_table_path}: {q_table}")
                return q_table
        except Exception as e:
            print(f"Failed to load Q-table: {e}")
            return {}

    def save_q_table(self):
        print(f"Saving Q-table: {self.q_table}")
        with open('q_table.json', 'w') as f:
            json.dump(self.q_table, f, indent=4)

    def train(self, question, reward, response):
            if question not in self.q_table:
                self.q_table[question] = {}

            self.q_table[question]['last_reward'] = reward
            self.q_table[question]['last_response'] = response
            self.save_q_table()
