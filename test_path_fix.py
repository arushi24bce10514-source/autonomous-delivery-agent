#!/usr/bin/env python3
"""
Test script to verify that paths no longer start with None.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.environment import GridEnvironment
from src.planners.uninformed import UniformCostPlanner
from src.planners.informed import AStarPlanner
from src.utils import reconstruct_path

def test_reconstruct_path():
    """Test the reconstruct_path function."""
    print("Testing reconstruct_path function...")
    
    # Test case 1: Normal path
    came_from = {(1, 0): (0, 0), (2, 0): (1, 0), (3, 0): (2, 0)}
    path = reconstruct_path(came_from, (3, 0))
    print(f"Path 1: {path}")
    assert path == [(0, 0), (1, 0), (2, 0), (3, 0)], f"Unexpected path: {path}"
    
    # Test case 2: Single node path
    came_from = {(0, 0): None}
    path = reconstruct_path(came_from, (0, 0))
    print(f"Path 2: {path}")
    assert path == [(0, 0)], f"Unexpected path: {path}"
    
    # Test case 3: No path
    came_from = {}
    path = reconstruct_path(came_from, (5, 5))
    print(f"Path 3: {path}")
    assert path is None, f"Unexpected path: {path}"
    
    print("✅ reconstruct_path tests passed!")

def test_planners_with_fix():
    """Test that planners now return proper paths without None."""
    print("\nTesting planners with fix...")
    
    # Create a simple environment
    env = GridEnvironment(5, 5)
    start = (0, 0)
    goal = (4, 4)
    
    # Test UCS
    ucs_planner = UniformCostPlanner(env)
    ucs_path = ucs_planner.plan(start, goal)
    print(f"UCS path: {ucs_path}")
    
    # Check that path doesn't start with None and is valid
    assert ucs_path is not None, "UCS returned None"
    assert len(ucs_path) > 0, "UCS returned empty path"
    assert ucs_path[0] == start, f"UCS path doesn't start at start: {ucs_path[0]}"
    assert ucs_path[-1] == goal, f"UCS path doesn't end at goal: {ucs_path[-1]}"
    assert None not in ucs_path, "UCS path contains None"
    
    # Test A*
    astar_planner = AStarPlanner(env)
    astar_path = astar_planner.plan(start, goal)
    print(f"A* path: {astar_path}")
    
    # Check that path doesn't start with None and is valid
    assert astar_path is not None, "A* returned None"
    assert len(astar_path) > 0, "A* returned empty path"
    assert astar_path[0] == start, f"A* path doesn't start at start: {astar_path[0]}"
    assert astar_path[-1] == goal, f"A* path doesn't end at goal: {astar_path[-1]}"
    assert None not in astar_path, "A* path contains None"
    
    print("✅ Planner path tests passed!")

def test_with_actual_map():
    """Test with the actual small.map file."""
    print("\nTesting with small.map...")
    
    from src.utils import load_map
    
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
    
    # Test UCS
    ucs_planner = UniformCostPlanner(env)
    ucs_path = ucs_planner.plan(start, goal)
    print(f"UCS path length: {len(ucs_path) if ucs_path else 'No path'}")
    
    if ucs_path:
        assert ucs_path[0] == start, f"UCS path doesn't start correctly: {ucs_path[0]}"
        assert ucs_path[-1] == goal, f"UCS path doesn't end correctly: {ucs_path[-1]}"
        assert None not in ucs_path, "UCS path contains None"
    
    # Test A*
    astar_planner = AStarPlanner(env)
    astar_path = astar_planner.plan(start, goal)
    print(f"A* path length: {len(astar_path) if astar_path else 'No path'}")
    
    if astar_path:
        assert astar_path[0] == start, f"A* path doesn't start correctly: {astar_path[0]}"
        assert astar_path[-1] == goal, f"A* path doesn't end correctly: {astar_path[-1]}"
        assert None not in astar_path, "A* path contains None"
    
    print("✅ Actual map tests passed!")

if __name__ == "__main__":
    print("Testing Path Reconstruction Fix")
    print("=" * 50)
    
    try:
        test_reconstruct_path()
        test_planners_with_fix()
        test_with_actual_map()
        print("\n🎉 All tests passed! Paths should no longer start with None.")
        print("\nYou can now run: python run_experiments.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()