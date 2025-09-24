"""
Local search algorithms for dynamic replanning.
"""

import random
from src.utils import get_neighbors, manhattan_distance

class LocalSearchPlanner:
    """Local search planner with random restarts for dynamic environments."""
    
    def __init__(self, environment, max_restarts=10):
        self.env = environment
        self.max_restarts = max_restarts
        self.nodes_expanded = 0
    
    def get_random_valid_position(self):
        """Get a random valid position that's not an obstacle."""
        while True:
            x = random.randint(0, self.env.width - 1)
            y = random.randint(0, self.env.height - 1)
            if not self.env.is_obstacle_at(x, y):
                return (x, y)
    
    def hill_climb(self, start, goal, max_steps=1000):
        """Perform hill climbing from start to goal."""
        current = start
        path = [current]
        self.nodes_expanded = 0
        
        for step in range(max_steps):
            self.nodes_expanded += 1
            
            if current == goal:
                return path
            
            # Get all valid neighbors
            neighbors = []
            for neighbor in get_neighbors(current, self.env.width, self.env.height):
                if not self.env.is_obstacle_at(neighbor[0], neighbor[1]):
                    # Use negative distance to goal as fitness (we want to minimize distance)
                    fitness = -manhattan_distance(neighbor, goal)
                    neighbors.append((neighbor, fitness))
            
            if not neighbors:
                break
            
            # Find best neighbor
            neighbors.sort(key=lambda x: x[1], reverse=True)
            best_neighbor, best_fitness = neighbors[0]
            
            # If no improvement, stop
            current_fitness = -manhattan_distance(current, goal)
            if best_fitness <= current_fitness:
                break
            
            current = best_neighbor
            path.append(current)
        
        return path if current == goal else None
    
    def plan(self, start, goal):
        """Find path using hill climbing with random restarts."""
        best_path = None
        best_cost = float('inf')
        
        # Try direct hill climbing first
        path = self.hill_climb(start, goal)
        if path:
            path_cost = sum(self.env.get_cell_cost(pos[0], pos[1]) for pos in path)
            best_path = path
            best_cost = path_cost
        
        # Random restarts
        for restart in range(self.max_restarts):
            # Generate a random intermediate point
            intermediate = self.get_random_valid_position()
            
            # Path from start to intermediate
            path1 = self.hill_climb(start, intermediate)
            if not path1:
                continue
            
            # Path from intermediate to goal
            path2 = self.hill_climb(intermediate, goal)
            if not path2:
                continue
            
            # Combine paths (avoid duplicate intermediate point)
            combined_path = path1 + path2[1:]
            path_cost = sum(self.env.get_cell_cost(pos[0], pos[1]) for pos in combined_path)
            
            if path_cost < best_cost:
                best_path = combined_path
                best_cost = path_cost
        
        return best_path