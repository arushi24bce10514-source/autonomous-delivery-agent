"""
Grid environment implementation for autonomous delivery agent.
"""

class GridCell:
    def __init__(self, terrain_cost=1, is_obstacle=False, dynamic_obstacle=False):
        self.terrain_cost = terrain_cost
        self.is_obstacle = is_obstacle
        self.dynamic_obstacle = dynamic_obstacle
        self.obstacle_schedule = []  # For predictable dynamic obstacles

class GridEnvironment:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[GridCell() for _ in range(width)] for _ in range(height)]
        self.dynamic_obstacles = []
        self.time_step = 0
    
    def add_terrain_cost(self, x, y, cost):
        """Add terrain cost to a specific cell."""
        if self._is_valid_position(x, y):
            self.grid[y][x].terrain_cost = cost
    
    def add_static_obstacle(self, x, y):
        """Add a static obstacle to a specific cell."""
        if self._is_valid_position(x, y):
            self.grid[y][x].is_obstacle = True
    
    def add_dynamic_obstacle(self, x, y, schedule):
        """Add a dynamic obstacle with a movement schedule."""
        if self._is_valid_position(x, y):
            self.dynamic_obstacles.append({
                'position': (x, y),
                'schedule': schedule,
                'current_step': 0
            })
            self.grid[y][x].dynamic_obstacle = True
    
    def _is_valid_position(self, x, y):
        """Check if position is within grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_obstacle_at(self, x, y):
        """Check if there's an obstacle at the given position."""
        if not self._is_valid_position(x, y):
            return True  # Consider out-of-bounds as obstacles
        return self.grid[y][x].is_obstacle
    
    def get_cell_cost(self, x, y):
        """Get the movement cost for a cell."""
        if not self._is_valid_position(x, y):
            return float('inf')  # Infinite cost for out-of-bounds
        return self.grid[y][x].terrain_cost
    
    def update_dynamic_obstacles(self):
        """Update positions of dynamic obstacles based on their schedule."""
        self.time_step += 1
        for obstacle in self.dynamic_obstacles:
            # Clear current position
            current_x, current_y = obstacle['position']
            self.grid[current_y][current_x].dynamic_obstacle = False
            
            # Get next movement from schedule
            schedule = obstacle['schedule']
            if schedule:
                step = obstacle['current_step'] % len(schedule)
                dx, dy = schedule[step]
                new_x, new_y = current_x + dx, current_y + dy
                
                # Move if new position is valid
                if self._is_valid_position(new_x, new_y) and not self.is_obstacle_at(new_x, new_y):
                    obstacle['position'] = (new_x, new_y)
                    self.grid[new_y][new_x].dynamic_obstacle = True
                
                obstacle['current_step'] += 1
    
    def get_dynamic_obstacle_positions(self):
        """Get current positions of all dynamic obstacles."""
        return [obs['position'] for obs in self.dynamic_obstacles]