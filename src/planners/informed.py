"""
Informed search algorithms: A* Search.
"""

from src.utils import PriorityQueue, reconstruct_path, get_neighbors, manhattan_distance

class AStarPlanner:
    """A* Search path planner with admissible heuristics."""
    
    def __init__(self, environment, heuristic='manhattan'):
        self.env = environment
        self.heuristic = heuristic
        self.nodes_expanded = 0
    
    def calculate_heuristic(self, pos, goal):
        """Calculate heuristic value for given position."""
        if self.heuristic == 'manhattan':
            return manhattan_distance(pos, goal)
        elif self.heuristic == 'euclidean':
            return ((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2) ** 0.5
        else:
            return 0
    
    def plan(self, start, goal):
        """Find path using A* algorithm."""
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
                    priority = new_cost + self.calculate_heuristic(neighbor, goal)
                    frontier.push(neighbor, priority)
                    came_from[neighbor] = current
        
        return None