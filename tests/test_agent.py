import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.environment import GridEnvironment
from src.agent import DeliveryAgent

class TestDeliveryAgent(unittest.TestCase):
    
    def setUp(self):
        self.env = GridEnvironment(10, 10)
        self.start = (0, 0)
        self.goal = (9, 9)
        self.agent = DeliveryAgent(self.start, self.goal, self.env)
    
    def test_agent_initialization(self):
        self.assertEqual(self.agent.position, self.start)
        self.assertEqual(self.agent.goal, self.goal)
        self.assertEqual(self.agent.env, self.env)
        self.assertEqual(self.agent.fuel_used, 0)
        self.assertEqual(self.agent.time_elapsed, 0)
    
    def test_replan(self):
        path = self.agent.replan()
        
        self.assertIsNotNone(path)
        self.assertEqual(len(path) > 0, True)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.goal)
    
    def test_step_movement(self):
        initial_pos = self.agent.position
        self.agent.replan()
        
        # Take one step
        success = self.agent.step()
        
        self.assertTrue(success)
        self.assertNotEqual(self.agent.position, initial_pos)
        self.assertEqual(self.agent.time_elapsed, 1)
    
    def test_path_cost_calculation(self):
        path = [(0, 0), (0, 1), (0, 2)]
        
        # Set different terrain costs
        self.env.add_terrain_cost(0, 1, 3)
        self.env.add_terrain_cost(0, 2, 2)
        
        cost = self.agent.calculate_path_cost(path)
        expected_cost = 1 + 3 + 2  # cost of each step
        self.assertEqual(cost, expected_cost)

if __name__ == '__main__':
    unittest.main()