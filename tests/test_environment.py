import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.environment import GridEnvironment

class TestGridEnvironment(unittest.TestCase):
    
    def setUp(self):
        self.env = GridEnvironment(10, 10)
    
    def test_initialization(self):
        self.assertEqual(self.env.width, 10)
        self.assertEqual(self.env.height, 10)
        
        # Test that all cells are initialized properly
        for y in range(10):
            for x in range(10):
                cell = self.env.grid[y][x]
                self.assertEqual(cell.terrain_cost, 1)
                self.assertFalse(cell.is_obstacle)
    
    def test_terrain_cost(self):
        self.env.add_terrain_cost(2, 3, 5)
        self.assertEqual(self.env.grid[3][2].terrain_cost, 5)
    
    def test_static_obstacle(self):
        self.env.add_static_obstacle(4, 5)
        self.assertTrue(self.env.grid[5][4].is_obstacle)
    
    def test_dynamic_obstacle(self):
        schedule = [(1, 0), (1, 0), (0, 1)]
        self.env.add_dynamic_obstacle(1, 1, schedule)
        
        self.assertEqual(len(self.env.dynamic_obstacles), 1)
        obstacle = self.env.dynamic_obstacles[0]
        self.assertEqual(obstacle['position'], (1, 1))
        self.assertEqual(obstacle['schedule'], schedule)
    
    def test_is_obstacle_at(self):
        self.env.add_static_obstacle(3, 3)
        self.assertTrue(self.env.is_obstacle_at(3, 3))
        self.assertFalse(self.env.is_obstacle_at(0, 0))
    
    def test_get_cell_cost(self):
        self.env.add_terrain_cost(2, 2, 3)
        self.assertEqual(self.env.get_cell_cost(2, 2), 3)
        self.assertEqual(self.env.get_cell_cost(0, 0), 1)

if __name__ == '__main__':
    unittest.main()