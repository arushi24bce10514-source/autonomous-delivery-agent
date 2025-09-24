import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.environment import GridEnvironment
from src.planners.uninformed import BFSPlanner, UniformCostPlanner
from src.planners.informed import AStarPlanner

class TestPlanners(unittest.TestCase):
    
    def setUp(self):
        self.env = GridEnvironment(5, 5)
        self.start = (0, 0)
        self.goal = (4, 4)
    
    def test_bfs_find_path(self):
        planner = BFSPlanner(self.env)
        path = planner.plan(self.start, self.goal)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.goal)
    
    def test_ucs_find_path(self):
        planner = UniformCostPlanner(self.env)
        path = planner.plan(self.start, self.goal)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.goal)
    
    def test_astar_find_path(self):
        planner = AStarPlanner(self.env)
        path = planner.plan(self.start, self.goal)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.goal)
    
    def test_obstacle_avoidance(self):
        # Add obstacles to block direct path
        self.env.add_static_obstacle(1, 0)
        self.env.add_static_obstacle(0, 1)
        self.env.add_static_obstacle(1, 1)
        
        planner = AStarPlanner(self.env)
        path = planner.plan(self.start, self.goal)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.goal)
        # Path should not go through obstacles
        for pos in path:
            self.assertFalse(self.env.is_obstacle_at(pos[0], pos[1]))

if __name__ == '__main__':
    unittest.main()