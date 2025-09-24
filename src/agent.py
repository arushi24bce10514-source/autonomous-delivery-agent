"""
Delivery Agent implementation for autonomous package delivery.
"""

import time
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.planners.uninformed import BFSPlanner, UniformCostPlanner
from src.planners.informed import AStarPlanner
from src.planners.local_search import LocalSearchPlanner

class DeliveryAgent:
    """Autonomous delivery agent that navigates a grid environment."""
    
    def __init__(self, start_pos, goal_pos, environment, planner_type='astar'):
        self.position = start_pos
        self.goal = goal_pos
        self.env = environment
        self.planner_type = planner_type
        self.path = []
        self.current_path_index = 0
        self.fuel_used = 0
        self.time_elapsed = 0
        self.nodes_expanded = 0
        self.allow_diagonals = False
    
    def calculate_path_cost(self, path):
        """Calculate total cost of a path."""
        if not path:
            return float('inf')
        
        total_cost = 0
        for i in range(len(path) - 1):
            total_cost += self.env.get_cell_cost(path[i][0], path[i][1])
        return total_cost
    
    def replan(self):
        """Replan path from current position to goal."""
        # Choose planner based on type
        if self.planner_type == 'bfs':
            planner = BFSPlanner(self.env)
        elif self.planner_type == 'ucs':
            planner = UniformCostPlanner(self.env)
        elif self.planner_type == 'astar':
            planner = AStarPlanner(self.env)
        elif self.planner_type == 'local':
            planner = LocalSearchPlanner(self.env)
        else:
            raise ValueError(f"Unknown planner type: {self.planner_type}")
        
        # Plan path
        start_time = time.time()
        path = planner.plan(self.position, self.goal)
        planning_time = time.time() - start_time
        
        # Store metrics
        self.nodes_expanded = planner.nodes_expanded
        self.current_path_index = 0
        self.path = path
        
        return path, planning_time
    
    def step(self):
        """Move one step along the current path."""
        if not self.path or self.current_path_index >= len(self.path) - 1:
            return False
        
        self.current_path_index += 1
        next_pos = self.path[self.current_path_index]
        
        # Check if next position is blocked by dynamic obstacle
        if self.env.is_obstacle_at(next_pos[0], next_pos[1]):
            # Need to replan
            self.replan()
            return self.step()
        
        # Move to next position
        self.position = next_pos
        self.fuel_used += self.env.get_cell_cost(next_pos[0], next_pos[1])
        self.time_elapsed += 1
        
        return True
    
    def has_reached_goal(self):
        """Check if agent has reached the goal."""
        return self.position == self.goal
    
    def get_metrics(self):
        """Get performance metrics."""
        return {
            'fuel_used': self.fuel_used,
            'time_elapsed': self.time_elapsed,
            'nodes_expanded': self.nodes_expanded,
            'path_length': len(self.path) if self.path else 0,
            'path_cost': self.calculate_path_cost(self.path)
        }