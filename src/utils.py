"""
Utility functions for the autonomous delivery agent project.
"""

import time
import heapq
from typing import List, Tuple, Dict, Any

def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """Calculate Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def euclidean_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Calculate Euclidean distance between two positions."""
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

def is_valid_position(x: int, y: int, width: int, height: int) -> bool:
    """Check if position is within grid bounds."""
    return 0 <= x < width and 0 <= y < height

def get_neighbors(pos, width, height, diagonals=False):
    """Get valid neighboring positions (4-connected or 8-connected)."""
    x, y = pos
    neighbors = []
    
    # 4-connected movements
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    if diagonals:
        # Add diagonal directions
        directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if is_valid_position(nx, ny, width, height):
            neighbors.append((nx, ny))
    
    return neighbors

def reconstruct_path(came_from: dict, current: tuple) -> list:
    """Reconstruct path from start to goal using came_from dictionary."""
    if current not in came_from:
        return None
    
    path = []
    while current is not None:
        path.append(current)
        current = came_from.get(current)  # Use get() to avoid KeyError
    
    path.reverse()
    return path if path else None

class PriorityQueue:
    """A proper priority queue implementation for pathfinding algorithms."""
    
    def __init__(self):
        self.elements = []
        self.entry_count = 0  # Counter for tie-breaking
    
    def push(self, item, priority):
        """Add a new item to the queue."""
        heapq.heappush(self.elements, (priority, self.entry_count, item))
        self.entry_count += 1
    
    def pop(self):
        """Remove and return the lowest priority item."""
        if self.elements:
            priority, count, item = heapq.heappop(self.elements)
            return item
        raise IndexError('pop from an empty priority queue')
    
    def is_empty(self):
        """Check if the queue is empty."""
        return len(self.elements) == 0
    
    def __bool__(self):
        """Boolean check for emptiness."""
        return not self.is_empty()

def load_map(filename: str) -> Dict[str, Any]:
    """
    Load map from file and return environment configuration.
    
    File format:
    width height
    S start_x start_y
    G goal_x goal_y
    T terrain_x terrain_y cost
    O obstacle_x obstacle_y
    D dynamic_x dynamic_y schedule
    """
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    
    config = {
        'width': 0, 'height': 0,
        'start': None, 'goal': None,
        'terrain_costs': [],
        'static_obstacles': [],
        'dynamic_obstacles': []
    }
    
    for line in lines:
        parts = line.split()
        if not parts:
            continue
            
        if parts[0] == 'S':
            config['start'] = (int(parts[1]), int(parts[2]))
        elif parts[0] == 'G':
            config['goal'] = (int(parts[1]), int(parts[2]))
        elif parts[0] == 'T':
            config['terrain_costs'].append((int(parts[1]), int(parts[2]), int(parts[3])))
        elif parts[0] == 'O':
            config['static_obstacles'].append((int(parts[1]), int(parts[2])))
        elif parts[0] == 'D':
            schedule = []
            if len(parts) > 3:
                for move in parts[3].split(','):
                    dx, dy = map(int, move.split(':'))
                    schedule.append((dx, dy))
            config['dynamic_obstacles'].append({
                'pos': (int(parts[1]), int(parts[2])),
                'schedule': schedule
            })
        else:
            # First line should be width and height
            config['width'] = int(parts[0])
            config['height'] = int(parts[1])
    
    return config

def save_results(filename: str, results: Dict[str, Any]):
    """Save experimental results to a file."""
    with open(filename, 'w') as f:
        for key, value in results.items():
            f.write(f"{key}: {value}\n")

def timer(func):
    """Decorator to measure execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    return wrapper