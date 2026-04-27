"""
Reinforcement Learning for NobleLogic Trading System
Implements Deep Q-Learning and Policy Gradient methods using PyTorch
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import os
import json
from collections import deque
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class RLConfig:
    """Configuration for reinforcement learning agent"""
    state_size: int = 50  # Number of features in state representation
    action_size: int = 3  # Hold, Buy, Sell
    hidden_size: int = 128
    learning_rate: float = 0.001
    gamma: float = 0.99  # Discount factor
    epsilon_start: float = 1.0
    epsilon_end: float = 0.01
    epsilon_decay: float = 0.995
    batch_size: int = 64
    memory_size: int = 10000
    target_update_freq: int = 100
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'

class ReplayMemory:
    """Experience replay buffer for DQN"""

    def __init__(self, capacity: int):
        self.memory = deque(maxlen=capacity)

    def push(self, state: np.ndarray, action: int, reward: float,
             next_state: np.ndarray, done: bool):
        """Store a transition"""
        self.memory.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int) -> List[Tuple]:
        """Sample a batch of transitions"""
        return random.sample(self.memory, batch_size)

    def __len__(self) -> int:
        return len(self.memory)

class DQNetwork(nn.Module):
    """Deep Q-Network for trading decisions"""

    def __init__(self, state_size: int, action_size: int, hidden_size: int):
        super(DQNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, action_size)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class PolicyNetwork(nn.Module):
    """Policy network for policy gradient methods"""

    def __init__(self, state_size: int, action_size: int, hidden_size: int):
        super(PolicyNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, action_size),
            nn.Softmax(dim=-1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class ValueNetwork(nn.Module):
    """Value network for actor-critic methods"""

    def __init__(self, state_size: int, hidden_size: int):
        super(ValueNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class TradingRLAgent:
    """
    Reinforcement Learning Agent for Trading
    Supports DQN, Policy Gradient, and Actor-Critic methods
    """

    def __init__(self, config: RLConfig, method: str = 'dqn'):
        self.config = config
        self.method = method.lower()
        self.device = torch.device(config.device)

        # Initialize networks based on method
        if self.method == 'dqn':
            self.policy_net = DQNetwork(config.state_size, config.action_size, config.hidden_size).to(self.device)
            self.target_net = DQNetwork(config.state_size, config.action_size, config.hidden_size).to(self.device)
            self.target_net.load_state_dict(self.policy_net.state_dict())
            self.target_net.eval()
            self.memory = ReplayMemory(config.memory_size)
            self.optimizer = optim.Adam(self.policy_net.parameters(), lr=config.learning_rate)

        elif self.method == 'policy_gradient':
            self.policy_net = PolicyNetwork(config.state_size, config.action_size, config.hidden_size).to(self.device)
            self.optimizer = optim.Adam(self.policy_net.parameters(), lr=config.learning_rate)

        elif self.method == 'actor_critic':
            self.actor = PolicyNetwork(config.state_size, config.action_size, config.hidden_size).to(self.device)
            self.critic = ValueNetwork(config.state_size, config.hidden_size).to(self.device)
            self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=config.learning_rate)
            self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=config.learning_rate)

        # Training parameters
        self.epsilon = config.epsilon_start
        self.steps_done = 0

        # Create models directory
        self.base_path = os.path.join(os.path.dirname(__file__), 'models', 'rl')
        os.makedirs(self.base_path, exist_ok=True)

        logger.info(f"[RL] Initialized {method.upper()} agent on {self.device}")

    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """Select action using epsilon-greedy policy"""
        if training and random.random() < self.epsilon:
            return random.randint(0, self.config.action_size - 1)

        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

            if self.method == 'dqn':
                q_values = self.policy_net(state_tensor)
                return q_values.argmax().item()

            elif self.method == 'policy_gradient':
                probs = self.policy_net(state_tensor)
                dist = Categorical(probs)
                return dist.sample().item()

            elif self.method == 'actor_critic':
                probs = self.actor(state_tensor)
                dist = Categorical(probs)
                return dist.sample().item()

    def store_transition(self, state: np.ndarray, action: int, reward: float,
                        next_state: np.ndarray, done: bool):
        """Store transition in replay memory (for DQN)"""
        if self.method == 'dqn':
            self.memory.push(state, action, reward, next_state, done)

    def update_epsilon(self):
        """Decay epsilon for exploration"""
        self.epsilon = max(self.config.epsilon_end,
                          self.epsilon * self.config.epsilon_decay)

    def train_step(self) -> Optional[float]:
        """Perform one training step"""
        if self.method == 'dqn' and len(self.memory) < self.config.batch_size:
            return None

        if self.method == 'dqn':
            return self._train_dqn()
        elif self.method == 'policy_gradient':
            return self._train_policy_gradient()
        elif self.method == 'actor_critic':
            return self._train_actor_critic()

    def _train_dqn(self) -> float:
        """Train DQN using experience replay"""
        transitions = self.memory.sample(self.config.batch_size)
        batch = list(zip(*transitions))

        state_batch = torch.FloatTensor(np.array(batch[0])).to(self.device)
        action_batch = torch.LongTensor(batch[1]).to(self.device)
        reward_batch = torch.FloatTensor(batch[2]).to(self.device)
        next_state_batch = torch.FloatTensor(np.array(batch[3])).to(self.device)
        done_batch = torch.BoolTensor(batch[4]).to(self.device)

        # Compute Q values
        q_values = self.policy_net(state_batch).gather(1, action_batch.unsqueeze(1)).squeeze(1)

        # Compute target Q values
        with torch.no_grad():
            next_q_values = self.target_net(next_state_batch).max(1)[0]
            target_q_values = reward_batch + (self.config.gamma * next_q_values * (~done_batch))

        # Compute loss and update
        loss = nn.MSELoss()(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update target network
        self.steps_done += 1
        if self.steps_done % self.config.target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        return loss.item()

    def _train_policy_gradient(self) -> float:
        """Train using policy gradient (REINFORCE)"""
        # This would require storing trajectories
        # Simplified implementation - would need full trajectory storage
        return 0.0

    def _train_actor_critic(self) -> float:
        """Train using actor-critic method"""
        # Simplified implementation
        return 0.0

    def save_model(self, path: Optional[str] = None):
        """Save the trained model"""
        if path is None:
            path = os.path.join(self.base_path, f'rl_agent_{self.method}.pth')

        if self.method == 'dqn':
            torch.save({
                'policy_net': self.policy_net.state_dict(),
                'target_net': self.target_net.state_dict(),
                'optimizer': self.optimizer.state_dict(),
                'epsilon': self.epsilon,
                'steps_done': self.steps_done,
                'config': self.config
            }, path)
        elif self.method == 'policy_gradient':
            torch.save({
                'policy_net': self.policy_net.state_dict(),
                'optimizer': self.optimizer.state_dict(),
                'config': self.config
            }, path)
        elif self.method == 'actor_critic':
            torch.save({
                'actor': self.actor.state_dict(),
                'critic': self.critic.state_dict(),
                'actor_optimizer': self.actor_optimizer.state_dict(),
                'critic_optimizer': self.critic_optimizer.state_dict(),
                'config': self.config
            }, path)

        logger.info(f"[RL] Model saved to {path}")

    def load_model(self, path: Optional[str] = None):
        """Load a trained model"""
        if path is None:
            path = os.path.join(self.base_path, f'rl_agent_{self.method}.pth')

        if not os.path.exists(path):
            logger.warning(f"[RL] Model file not found: {path}")
            return

        checkpoint = torch.load(path, map_location=self.device)

        if self.method == 'dqn':
            self.policy_net.load_state_dict(checkpoint['policy_net'])
            self.target_net.load_state_dict(checkpoint['target_net'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])
            self.epsilon = checkpoint.get('epsilon', self.config.epsilon_start)
            self.steps_done = checkpoint.get('steps_done', 0)
        elif self.method == 'policy_gradient':
            self.policy_net.load_state_dict(checkpoint['policy_net'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])
        elif self.method == 'actor_critic':
            self.actor.load_state_dict(checkpoint['actor'])
            self.critic.load_state_dict(checkpoint['critic'])
            self.actor_optimizer.load_state_dict(checkpoint['actor_optimizer'])
            self.critic_optimizer.load_state_dict(checkpoint['critic_optimizer'])

        logger.info(f"[RL] Model loaded from {path}")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'method': self.method,
            'device': str(self.device),
            'epsilon': self.epsilon,
            'steps_done': self.steps_done,
            'config': {
                'state_size': self.config.state_size,
                'action_size': self.config.action_size,
                'hidden_size': self.config.hidden_size,
                'learning_rate': self.config.learning_rate,
                'gamma': self.config.gamma
            }
        }

class TradingEnvironment:
    """
    Reinforcement learning environment for trading
    Defines states, actions, and rewards for the trading agent
    """

    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.reset()

    def reset(self) -> np.ndarray:
        """Reset environment to initial state"""
        self.balance = self.initial_balance
        self.position = 0  # 0: no position, 1: long, -1: short
        self.entry_price = 0.0
        self.total_pnl = 0.0
        self.trades = []
        self.current_step = 0

        # Return initial state
        return self._get_state()

    def _get_state(self, market_data: Optional[Dict] = None) -> np.ndarray:
        """Get current state representation"""
        if market_data is None:
            # Default state when no market data
            return np.array([
                0.0,  # normalized price
                0.0,  # price change
                0.0,  # volume
                self.position,  # current position
                self.balance / self.initial_balance,  # normalized balance
                0.0,  # unrealized pnl
            ])

        # Extract features from market data
        price = market_data.get('price', 0.0)
        price_change = market_data.get('price_change', 0.0)
        volume = market_data.get('volume', 0.0)

        # Calculate unrealized P&L
        unrealized_pnl = 0.0
        if self.position != 0 and self.entry_price > 0:
            if self.position == 1:  # long position
                unrealized_pnl = (price - self.entry_price) / self.entry_price
            else:  # short position
                unrealized_pnl = (self.entry_price - price) / self.entry_price

        return np.array([
            price / 100000,  # normalized price (assuming crypto prices)
            price_change,  # price change percentage
            volume / 1000000,  # normalized volume
            self.position,  # current position
            self.balance / self.initial_balance,  # normalized balance
            unrealized_pnl,  # unrealized P&L
        ])

    def step(self, action: int, market_data: Dict) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute action and return next state, reward, done, info
        Actions: 0=hold, 1=buy, 2=sell
        """
        self.current_step += 1
        reward = 0.0
        done = False
        info = {}

        price = market_data.get('price', 0.0)
        timestamp = market_data.get('timestamp', datetime.now())

        # Execute action
        if action == 1:  # Buy
            if self.position == 0:  # No position - enter long
                self.position = 1
                self.entry_price = price
                reward = -0.001  # Small transaction cost
                info['action'] = 'BUY'
            elif self.position == -1:  # Short position - close and go long
                # Calculate P&L from closing short
                pnl = (self.entry_price - price) / self.entry_price * self.balance
                self.balance += pnl
                self.total_pnl += pnl
                self.trades.append({
                    'type': 'CLOSE_SHORT',
                    'entry_price': self.entry_price,
                    'exit_price': price,
                    'pnl': pnl,
                    'timestamp': timestamp
                })
                # Enter long position
                self.position = 1
                self.entry_price = price
                reward = pnl / self.initial_balance  # Normalized reward
                info['action'] = 'CLOSE_SHORT_BUY'
            # else: already long, do nothing

        elif action == 2:  # Sell
            if self.position == 0:  # No position - enter short
                self.position = -1
                self.entry_price = price
                reward = -0.001  # Small transaction cost
                info['action'] = 'SELL'
            elif self.position == 1:  # Long position - close and go short
                # Calculate P&L from closing long
                pnl = (price - self.entry_price) / self.entry_price * self.balance
                self.balance += pnl
                self.total_pnl += pnl
                self.trades.append({
                    'type': 'CLOSE_LONG',
                    'entry_price': self.entry_price,
                    'exit_price': price,
                    'pnl': pnl,
                    'timestamp': timestamp
                })
                # Enter short position
                self.position = -1
                self.entry_price = price
                reward = pnl / self.initial_balance  # Normalized reward
                info['action'] = 'CLOSE_LONG_SELL'
            # else: already short, do nothing

        else:  # Hold (action == 0)
            info['action'] = 'HOLD'
            # Small penalty for holding to encourage action
            reward = -0.0001

        # Check if episode should end (bankruptcy or max steps)
        if self.balance <= 0:
            done = True
            reward = -1.0  # Large penalty for bankruptcy
        elif self.current_step >= 1000:  # Max steps per episode
            done = True
            # Final reward based on total P&L
            reward = self.total_pnl / self.initial_balance

        next_state = self._get_state(market_data)
        return next_state, reward, done, info

    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        return {
            'balance': self.balance,
            'total_pnl': self.total_pnl,
            'total_return': self.total_pnl / self.initial_balance,
            'num_trades': len(self.trades),
            'current_position': self.position,
            'win_rate': sum(1 for t in self.trades if t['pnl'] > 0) / max(1, len(self.trades))
        }


class QLearningAgent:
    """
    Q-Learning agent for trading decisions
    Uses Q-table to learn optimal trading policy
    """

    def __init__(self, state_size: int = 6, action_size: int = 3,
                 learning_rate: float = 0.1, discount_factor: float = 0.95,
                 exploration_rate: float = 1.0, exploration_decay: float = 0.995):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = 0.01

        # Initialize Q-table
        self.q_table = {}

        # Discretization bins for continuous state variables
        self.price_bins = np.linspace(0, 0.01, 10)  # 0 to 100k normalized
        self.change_bins = np.linspace(-0.1, 0.1, 20)  # -10% to +10%
        self.volume_bins = np.linspace(0, 0.01, 10)  # normalized volume
        self.balance_bins = np.linspace(0.5, 1.5, 10)  # 50% to 150% of initial
        self.pnl_bins = np.linspace(-0.5, 0.5, 20)  # -50% to +50%

    def _discretize_state(self, state: np.ndarray) -> Tuple:
        """Discretize continuous state into discrete bins"""
        price_idx = np.digitize(state[0], self.price_bins) - 1
        change_idx = np.digitize(state[1], self.change_bins) - 1
        volume_idx = np.digitize(state[2], self.volume_bins) - 1
        position = int(state[3])  # -1, 0, 1
        balance_idx = np.digitize(state[4], self.balance_bins) - 1
        pnl_idx = np.digitize(state[5], self.pnl_bins) - 1

        return (price_idx, change_idx, volume_idx, position, balance_idx, pnl_idx)

    def _get_q_value(self, state: Tuple, action: int) -> float:
        """Get Q-value for state-action pair"""
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.action_size)
        return self.q_table[state][action]

    def _set_q_value(self, state: Tuple, action: int, value: float):
        """Set Q-value for state-action pair"""
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.action_size)
        self.q_table[state][action] = value

    def choose_action(self, state: np.ndarray) -> int:
        """Choose action using epsilon-greedy policy"""
        if random.random() < self.exploration_rate:
            return random.randint(0, self.action_size - 1)

        discrete_state = self._discretize_state(state)
        q_values = [self._get_q_value(discrete_state, a) for a in range(self.action_size)]
        return np.argmax(q_values)

    def learn(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray):
        """Update Q-table using Q-learning update rule"""
        discrete_state = self._discretize_state(state)
        discrete_next_state = self._discretize_state(next_state)

        # Q-learning update
        current_q = self._get_q_value(discrete_state, action)
        next_max_q = max(self._get_q_value(discrete_next_state, a) for a in range(self.action_size))

        new_q = current_q + self.learning_rate * (reward + self.discount_factor * next_max_q - current_q)
        self._set_q_value(discrete_state, action, new_q)

        # Decay exploration rate
        self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)

    def save_model(self, filepath: str):
        """Save Q-table to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump({str(k): v.tolist() for k, v in self.q_table.items()}, f)
        logger.info(f"Q-learning model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load Q-table from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.q_table = {eval(k): np.array(v) for k, v in data.items()}
            logger.info(f"Q-learning model loaded from {filepath}")
        else:
            logger.warning(f"Model file {filepath} not found")


class DeepQLearningAgent:
    """
    Deep Q-Learning agent using PyTorch for Q-value approximation
    """

    def __init__(self, state_size: int = 6, action_size: int = 3,
                 learning_rate: float = 0.001, discount_factor: float = 0.95,
                 exploration_rate: float = 1.0, exploration_decay: float = 0.995,
                 memory_size: int = 10000, batch_size: int = 64):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = 0.01
        self.memory_size = memory_size
        self.batch_size = batch_size

        # Experience replay memory
        self.memory = []
        self.memory_counter = 0

        # Build PyTorch neural network model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()

    def _build_model(self):
        """Build neural network for Q-value approximation"""
        model = nn.Sequential(
            nn.Linear(self.state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, self.action_size)
        )
        return model.to(self.device)

    def update_target_model(self):
        """Update target model weights"""
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()

    def remember(self, state: np.ndarray, action: int, reward: float,
                 next_state: np.ndarray, done: bool):
        """Store experience in replay memory"""
        experience = (state, action, reward, next_state, done)
        if len(self.memory) < self.memory_size:
            self.memory.append(experience)
        else:
            self.memory[self.memory_counter % self.memory_size] = experience
        self.memory_counter += 1

    def choose_action(self, state: np.ndarray) -> int:
        """Choose action using epsilon-greedy policy"""
        if random.random() < self.exploration_rate:
            return random.randint(0, self.action_size - 1)

        with torch.no_grad():
            state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.model(state)
            return torch.argmax(q_values).item()

    def replay(self):
        """Train model using experience replay"""
        if len(self.memory) < self.batch_size:
            return

        # Sample batch from memory
        batch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor(np.array([exp[0] for exp in batch])).to(self.device)
        actions = torch.LongTensor([exp[1] for exp in batch]).to(self.device)
        rewards = torch.FloatTensor([exp[2] for exp in batch]).to(self.device)
        next_states = torch.FloatTensor(np.array([exp[3] for exp in batch])).to(self.device)
        dones = torch.BoolTensor([exp[4] for exp in batch]).to(self.device)

        # Get current Q values
        current_q = self.model(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        # Get target Q values
        with torch.no_grad():
            next_q = self.target_model(next_states).max(1)[0]
            target_q = rewards + (self.discount_factor * next_q * (~dones))

        # Compute loss and update
        loss = nn.MSELoss()(current_q, target_q)
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # Decay exploration rate
        self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate * self.exploration_decay)

    def save_model(self, filepath: str):
        """Save model to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'exploration_rate': self.exploration_rate,
            'memory': self.memory,
            'memory_counter': self.memory_counter
        }, filepath)
        logger.info(f"Deep Q-Learning model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load model from file"""
        if os.path.exists(filepath):
            checkpoint = torch.load(filepath, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
            self.exploration_rate = checkpoint.get('exploration_rate', self.exploration_rate)
            self.memory = checkpoint.get('memory', [])
            self.memory_counter = checkpoint.get('memory_counter', 0)
            self.update_target_model()
            logger.info(f"Deep Q-Learning model loaded from {filepath}")
        else:
            logger.warning(f"Model file {filepath} not found")


class ReinforcementLearningTrader:
    """
    Main reinforcement learning trading system
    Integrates Q-learning and Deep Q-Learning agents
    """

    def __init__(self, agent_type: str = 'q_learning', model_path: str = None):
        self.agent_type = agent_type
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), 'models', 'rl')

        # Initialize environment
        self.environment = TradingEnvironment()

        # Initialize agent
        if agent_type == 'deep_q':
            self.agent = DeepQLearningAgent()
        else:
            self.agent = QLearningAgent()

        # Training metrics
        self.episode_rewards = []
        self.episode_pnls = []

        # Load existing model if available
        self.load_model()

    def train_episode(self, market_data: List[Dict]) -> Dict:
        """Train agent for one episode using market data"""
        state = self.environment.reset()
        total_reward = 0.0
        episode_steps = 0

        for market_step in market_data:
            # Choose action
            action = self.agent.choose_action(state)

            # Execute action in environment
            next_state, reward, done, info = self.environment.step(action, market_step)

            # Store experience (for deep Q-learning)
            if hasattr(self.agent, 'remember'):
                self.agent.remember(state, action, reward, next_state, done)

            # Learn from experience
            if self.agent_type == 'q_learning':
                self.agent.learn(state, action, reward, next_state)
            elif self.agent_type == 'deep_q' and episode_steps % 4 == 0:  # Train every 4 steps
                self.agent.replay()
                if episode_steps % 100 == 0:  # Update target network
                    self.agent.update_target_model()

            total_reward += reward
            state = next_state
            episode_steps += 1

            if done:
                break

        # Store episode metrics
        performance = self.environment.get_performance_metrics()
        self.episode_rewards.append(total_reward)
        self.episode_pnls.append(performance['total_pnl'])

        return {
            'total_reward': total_reward,
            'total_pnl': performance['total_pnl'],
            'num_trades': performance['num_trades'],
            'win_rate': performance['win_rate'],
            'final_balance': performance['balance'],
            'steps': episode_steps
        }

    def get_trading_decision(self, market_data: Dict) -> Dict:
        """Get trading decision from trained agent"""
        state = self.environment._get_state(market_data)
        action = self.agent.choose_action(state)

        # Convert action to trading decision
        action_map = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}
        decision = action_map[action]

        # Calculate confidence based on Q-values (if available)
        confidence = 0.5  # Default confidence
        if hasattr(self.agent, 'model') and self.agent.model:
            # For deep Q-learning, use max Q-value as confidence proxy
            state_reshaped = np.reshape(state, [1, len(state)])
            q_values = self.agent.model.predict(state_reshaped, verbose=0)[0]
            max_q = np.max(q_values)
            confidence = min(1.0, max(0.0, (max_q + 1.0) / 2.0))  # Normalize to 0-1
        elif hasattr(self.agent, 'q_table'):
            # For Q-learning, use max Q-value as confidence proxy
            discrete_state = self.agent._discretize_state(state)
            if discrete_state in self.agent.q_table:
                q_values = self.agent.q_table[discrete_state]
                max_q = np.max(q_values)
                confidence = min(1.0, max(0.0, (max_q + 1.0) / 2.0))

        return {
            'decision': decision,
            'confidence': confidence,
            'action': action,
            'agent_type': self.agent_type,
            'rl_active': True
        }

    def save_model(self):
        """Save the trained model"""
        filepath = os.path.join(self.model_path, f'{self.agent_type}_model')
        self.agent.save_model(filepath)

    def load_model(self):
        """Load a trained model"""
        filepath = os.path.join(self.model_path, f'{self.agent_type}_model')
        self.agent.load_model(filepath)

    def get_training_metrics(self) -> Dict:
        """Get training performance metrics"""
        return {
            'episodes_trained': len(self.episode_rewards),
            'avg_reward': np.mean(self.episode_rewards) if self.episode_rewards else 0.0,
            'avg_pnl': np.mean(self.episode_pnls) if self.episode_pnls else 0.0,
            'best_reward': max(self.episode_rewards) if self.episode_rewards else 0.0,
            'best_pnl': max(self.episode_pnls) if self.episode_pnls else 0.0,
            'agent_type': self.agent_type
        }


# Global RL trader instance
rl_trader = None

def get_rl_trader(agent_type: str = 'q_learning') -> ReinforcementLearningTrader:
    """Get or create RL trader instance"""
    global rl_trader
    if rl_trader is None or rl_trader.agent_type != agent_type:
        rl_trader = ReinforcementLearningTrader(agent_type=agent_type)
    return rl_trader

def train_rl_agent(market_data: List[Dict], agent_type: str = 'q_learning',
                   episodes: int = 100) -> Dict:
    """Train RL agent with market data"""
    trader = get_rl_trader(agent_type)

    print(f"[RL] Training {agent_type} agent for {episodes} episodes...")

    training_results = []
    for episode in range(episodes):
        result = trader.train_episode(market_data)
        training_results.append(result)

        if (episode + 1) % 10 == 0:
            print(f"[RL] Episode {episode + 1}/{episodes} - "
                  f"Reward: {result['total_reward']:.3f}, "
                  f"P&L: {result['total_pnl']:.2f}")

    # Save trained model
    trader.save_model()

    # Calculate final metrics
    final_metrics = trader.get_training_metrics()

    return {
        'training_results': training_results,
        'final_metrics': final_metrics,
        'agent_type': agent_type
    }