"""
Uninformed search algorithms: BFS and Uniform Cost Search.
"""

from src.utils import PriorityQueue, reconstruct_path, get_neighbors

class BFSPlanner:
    """Breadth-First Search path planner."""
    
    def __init__(self, environment):
        self.env = environment
        self.nodes_expanded = 0
    
    def plan(self, start, goal):
        """Find path using BFS algorithm."""
        self.nodes_expanded = 0
        
        if start == goal:
            return [start]
        
        queue = [(start, [start])]  # (position, path)
        visited = set([start])
        
        while queue:
            current, path = queue.pop(0)
            self.nodes_expanded += 1
            
            if current == goal:
                return path
            
            for neighbor in get_neighbors(current, self.env.width, self.env.height):
                if (neighbor not in visited and 
                    not self.env.is_obstacle_at(neighbor[0], neighbor[1])):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None

class UniformCostPlanner:
    """Uniform Cost Search path planner."""
    
    def __init__(self, environment):
        self.env = environment
        self.nodes_expanded = 0
    
    def plan(self, start, goal):
        """Find path using Uniform Cost Search algorithm."""
        self.nodes_expanded = 0
        
        if start == goal:
            return [start]
        
        frontier = PriorityQueue()
        frontier.push(start, 0)
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while not frontier.is_empty():
            current = frontier.pop()
            self.nodes_expanded += 1
            
            if current == goal:
                path = reconstruct_path(came_from, goal)
                return path if path else None
            
            for neighbor in get_neighbors(current, self.env.width, self.env.height):
                if self.env.is_obstacle_at(neighbor[0], neighbor[1]):
                    continue
                
                # Calculate movement cost to neighbor
                move_cost = self.env.get_cell_cost(neighbor[0], neighbor[1])
                new_cost = cost_so_far[current] + move_cost
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost
                    frontier.push(neighbor, priority)
                    came_from[neighbor] = current
        
        return None