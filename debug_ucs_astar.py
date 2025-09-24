#!/usr/bin/env python3
"""
Debug script to specifically test UCS and A* planners.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.environment import GridEnvironment
from src.utils import load_map
from src.planners.uninformed import UniformCostPlanner
from src.planners.informed import AStarPlanner

def debug_planner(planner_name, env, start, goal):
    """Debug a specific planner with detailed output."""
    print(f"\n=== Debugging {planner_name.upper()} ===")
    print(f"Start: {start}, Goal: {goal}")
    print(f"Grid size: {env.width}x{env.height}")
    
    if planner_name == 'ucs':
        planner = UniformCostPlanner(env)
    elif planner_name == 'astar':
        planner = AStarPlanner(env)
    else:
        print(f"Unknown planner: {planner_name}")
        return
    
    try:
        print("Calling planner.plan()...")
        path = planner.plan(start, goal)
        print(f"Planner returned: {path}")
        
        if path is None:
            print("❌ Planner returned None")
        elif path == []:
            print("❌ Planner returned empty list")
        else:
            print(f"✅ Path found! Length: {len(path)}")
            print(f"Nodes expanded: {planner.nodes_expanded}")
            print(f"First few steps: {path[:5]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_with_simple_map():
    """Test with a very simple 3x3 map."""
    print("Testing with simple 3x3 map...")
    
    # Create a minimal environment
    env = GridEnvironment(3, 3)
    start = (0, 0)
    goal = (2, 2)
    
    # Test both planners
    debug_planner('ucs', env, start, goal)
    debug_planner('astar', env, start, goal)

def test_with_obstacles():
    """Test with obstacles."""
    print("\n" + "="*50)
    print("Testing with obstacles...")
    
    env = GridEnvironment(5, 5)
    start = (0, 0)
    goal = (4, 4)
    
    # Add some obstacles
    env.add_static_obstacle(2, 2)
    env.add_static_obstacle(2, 3)
    env.add_static_obstacle(3, 2)
    
    debug_planner('ucs', env, start, goal)
    debug_planner('astar', env, start, goal)

def test_with_actual_map():
    """Test with one of our actual map files."""
    print("\n" + "="*50)
    print("Testing with small.map...")
    
    try:
        config = load_map('maps/small.map')
        env = GridEnvironment(config['width'], config['height'])
        
        # Configure terrain costs
        for x, y, cost in config['terrain_costs']:
            env.add_terrain_cost(x, y, cost)
        
        # Add static obstacles
        for x, y in config['static_obstacles']:
            env.add_static_obstacle(x, y)
        
        start = config['start']
        goal = config['goal']
        
        print(f"Map loaded: {config['width']}x{config['height']}")
        print(f"Start: {start}, Goal: {goal}")
        print(f"Terrain costs: {config['terrain_costs']}")
        print(f"Obstacles: {config['static_obstacles']}")
        
        debug_planner('ucs', env, start, goal)
        debug_planner('astar', env, start, goal)
        
    except Exception as e:
        print(f"Error loading map: {e}")

if __name__ == "__main__":
    print("Debugging UCS and A* Planners")
    print("=" * 50)
    
    test_with_simple_map()
    test_with_obstacles()
    test_with_actual_map()