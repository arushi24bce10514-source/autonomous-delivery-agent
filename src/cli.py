"""
Command Line Interface for the autonomous delivery agent.
"""

import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.environment import GridEnvironment
from src.agent import DeliveryAgent
from src.utils import load_map, timer

def main():
    parser = argparse.ArgumentParser(description='Autonomous Delivery Agent')
    
    parser.add_argument('map_file', help='Path to the map file')
    parser.add_argument('--planner', choices=['bfs', 'ucs', 'astar', 'local'], 
                       default='astar', help='Path planning algorithm to use')
    parser.add_argument('--diagonals', action='store_true', 
                       help='Allow diagonal movements (8-connected)')
    parser.add_argument('--max-time', type=int, default=60,
                       help='Maximum planning time in seconds')
    parser.add_argument('--visualize', action='store_true',
                       help='Visualize the path (if matplotlib is available)')
    parser.add_argument('--output', help='Output file for results')
    
    args = parser.parse_args()
    
    # Load map configuration
    try:
        config = load_map(args.map_file)
    except FileNotFoundError:
        print(f"Error: Map file '{args.map_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading map: {e}")
        sys.exit(1)
    
    # Create environment
    env = GridEnvironment(config['width'], config['height'])
    
    # Set up terrain costs
    for x, y, cost in config['terrain_costs']:
        env.add_terrain_cost(x, y, cost)
    
    # Add static obstacles
    for x, y in config['static_obstacles']:
        env.add_static_obstacle(x, y)
    
    # Add dynamic obstacles
    for obstacle in config['dynamic_obstacles']:
        env.add_dynamic_obstacle(obstacle['pos'][0], obstacle['pos'][1], obstacle['schedule'])
    
    # Create agent
    agent = DeliveryAgent(config['start'], config['goal'], env, args.planner)
    agent.allow_diagonals = args.diagonals
    
    print(f"=== Autonomous Delivery Agent ===")
    print(f"Map: {args.map_file}")
    print(f"Size: {config['width']}x{config['height']}")
    print(f"Start: {config['start']}, Goal: {config['goal']}")
    print(f"Planner: {args.planner.upper()}")
    print(f"Diagonals allowed: {args.diagonals}")
    print("-" * 40)
    
    # Plan path
    try:
        path, planning_time = agent.replan()
        
        if path:
            print(f"Path found! Length: {len(path)}")
            print(f"Planning time: {planning_time:.4f} seconds")
            print(f"Path cost: {agent.calculate_path_cost(path)}")
            print(f"Nodes expanded: {agent.nodes_expanded}")
            
            if args.visualize:
                try:
                    agent.visualize_path(path)
                except ImportError:
                    print("Visualization requires matplotlib. Install with: pip install matplotlib")
            
            # Save results if output file specified
            if args.output:
                results = {
                    'map_file': args.map_file,
                    'planner': args.planner,
                    'path_length': len(path),
                    'planning_time': planning_time,
                    'path_cost': agent.calculate_path_cost(path),
                    'nodes_expanded': agent.nodes_expanded,
                    'success': True
                }
                save_results(args.output, results)
                print(f"Results saved to {args.output}")
        else:
            print("No path found!")
            
    except Exception as e:
        print(f"Error during planning: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()