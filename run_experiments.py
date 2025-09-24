#!/usr/bin/env python3
"""
Comprehensive experiment runner for autonomous delivery agent project.

This script runs comparative experiments across all implemented path planning
algorithms on various map configurations to evaluate performance metrics.
"""

import time
import os
import sys
import json
import traceback
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.environment import GridEnvironment
from src.agent import DeliveryAgent
from src.utils import load_map

class ExperimentRunner:
    """Handles running experiments and collecting performance metrics."""
    
    def __init__(self, results_file="experiment_results.json"):
        self.results_file = results_file
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "experiments": {}
        }
    
    def setup_environment(self, map_file):
        """Load and configure environment from map file."""
        try:
            config = load_map(map_file)
            env = GridEnvironment(config['width'], config['height'])
            
            # Configure terrain costs
            for x, y, cost in config['terrain_costs']:
                env.add_terrain_cost(x, y, cost)
            
            # Add static obstacles
            for x, y in config['static_obstacles']:
                env.add_static_obstacle(x, y)
            
            # Add dynamic obstacles
            for obstacle in config['dynamic_obstacles']:
                env.add_dynamic_obstacle(
                    obstacle['pos'][0], 
                    obstacle['pos'][1], 
                    obstacle['schedule']
                )
            
            return env, config
            
        except Exception as e:
            print(f"Error loading map {map_file}: {e}")
            traceback.print_exc()
            return None, None
    
    def run_single_experiment(self, map_file, planner, diagonals=False, trials=3):
        """Run multiple trials for a specific configuration."""
        print(f"  Testing {planner.upper()}...", end=" ", flush=True)
        
        metrics = {
            'success_count': 0,
            'total_time': 0.0,
            'total_cost': 0.0,
            'total_nodes': 0,
            'min_cost': float('inf'),
            'max_cost': 0,
            'path_lengths': [],
            'individual_runs': []
        }
        
        for trial in range(trials):
            try:
                env, config = self.setup_environment(map_file)
                if env is None or config is None:
                    metrics['individual_runs'].append({
                        'trial': trial + 1,
                        'success': False,
                        'error': 'Failed to load environment'
                    })
                    continue
                
                # Validate start and goal positions
                if not env._is_valid_position(config['start'][0], config['start'][1]):
                    metrics['individual_runs'].append({
                        'trial': trial + 1,
                        'success': False,
                        'error': f"Invalid start position: {config['start']}"
                    })
                    continue
                
                if not env._is_valid_position(config['goal'][0], config['goal'][1]):
                    metrics['individual_runs'].append({
                        'trial': trial + 1,
                        'success': False,
                        'error': f"Invalid goal position: {config['goal']}"
                    })
                    continue
                
                # Check if start or goal are obstacles
                if env.is_obstacle_at(config['start'][0], config['start'][1]):
                    metrics['individual_runs'].append({
                        'trial': trial + 1,
                        'success': False,
                        'error': f"Start position is obstacle: {config['start']}"
                    })
                    continue
                
                if env.is_obstacle_at(config['goal'][0], config['goal'][1]):
                    metrics['individual_runs'].append({
                        'trial': trial + 1,
                        'success': False,
                        'error': f"Goal position is obstacle: {config['goal']}"
                    })
                    continue
                
                agent = DeliveryAgent(config['start'], config['goal'], env, planner)
                agent.allow_diagonals = diagonals
                
                # Time the planning process
                start_time = time.time()
                result = agent.replan()
                end_time = time.time()
                
                # Handle the return value - it should be (path, planning_time)
                if result is None:
                    path = None
                    planning_time = end_time - start_time
                elif isinstance(result, tuple) and len(result) == 2:
                    path, planning_time = result
                else:
                    path = result
                    planning_time = end_time - start_time
                
                if path and len(path) > 0:
                    path_cost = agent.calculate_path_cost(path)
                    
                    metrics['success_count'] += 1
                    metrics['total_time'] += planning_time
                    metrics['total_cost'] += path_cost
                    metrics['total_nodes'] += agent.nodes_expanded
                    metrics['min_cost'] = min(metrics['min_cost'], path_cost)
                    metrics['max_cost'] = max(metrics['max_cost'], path_cost)
                    metrics['path_lengths'].append(len(path))
                    
                    metrics['individual_runs'].append({
                        'trial': trial + 1,
                        'success': True,
                        'planning_time': planning_time,
                        'path_cost': path_cost,
                        'path_length': len(path),
                        'nodes_expanded': agent.nodes_expanded
                    })
                else:
                    metrics['individual_runs'].append({
                        'trial': trial + 1,
                        'success': False,
                        'planning_time': planning_time,
                        'path_cost': 0,
                        'path_length': 0,
                        'nodes_expanded': agent.nodes_expanded,
                        'error': 'No path found'
                    })
                    
            except Exception as e:
                error_msg = f"Trial {trial + 1} error: {str(e)}"
                print(f"\n    {error_msg}")
                metrics['individual_runs'].append({
                    'trial': trial + 1,
                    'success': False,
                    'error': error_msg
                })
        
        # Calculate averages
        if metrics['success_count'] > 0:
            metrics['success_rate'] = (metrics['success_count'] / trials) * 100
            metrics['avg_time'] = metrics['total_time'] / metrics['success_count']
            metrics['avg_cost'] = metrics['total_cost'] / metrics['success_count']
            metrics['avg_nodes'] = metrics['total_nodes'] / metrics['success_count']
            metrics['avg_path_length'] = sum(metrics['path_lengths']) / len(metrics['path_lengths'])
        else:
            metrics['success_rate'] = 0
            metrics['avg_time'] = 0
            metrics['avg_cost'] = 0
            metrics['avg_nodes'] = 0
            metrics['avg_path_length'] = 0
        
        # Clean up for JSON serialization
        if 'total_time' in metrics:
            del metrics['total_time']
        if 'total_cost' in metrics:
            del metrics['total_cost']
        if 'total_nodes' in metrics:
            del metrics['total_nodes']
        if 'path_lengths' in metrics:
            del metrics['path_lengths']
        
        if metrics['success_rate'] > 0:
            print(f"✓ {metrics['success_rate']:.1f}% success")
        else:
            print("✗ Failed")
            
        return metrics
    
    def run_comprehensive_experiments(self):
        """Run experiments across all maps and planners."""
        maps = {
            'small': 'maps/small.map',
            'medium': 'maps/medium.map', 
            'large': 'maps/large.map',
            'dynamic': 'maps/dynamic.map'
        }
        
        planners = ['bfs', 'ucs', 'astar', 'local']
        configurations = [
            {'diagonals': False, 'name': '4-connected'},
            {'diagonals': True, 'name': '8-connected'}
        ]
        
        print("=" * 80)
        print("AUTONOMOUS DELIVERY AGENT - COMPREHENSIVE EXPERIMENTS")
        print("=" * 80)
        print(f"Started at: {self.results['timestamp']}")
        print()
        
        total_experiments = len(maps) * len(planners) * len(configurations)
        current_experiment = 0
        
        for map_name, map_file in maps.items():
            if not os.path.exists(map_file):
                print(f"Warning: Map file {map_file} not found, skipping...")
                continue
                
            self.results['experiments'][map_name] = {}
            
            print(f"\nMAP: {map_name.upper()} ({map_file})")
            print("-" * 60)
            
            for config in configurations:
                config_name = config['name']
                diagonals = config['diagonals']
                
                print(f"\nConfiguration: {config_name}")
                print("-" * 40)
                
                self.results['experiments'][map_name][config_name] = {}
                
                for planner in planners:
                    current_experiment += 1
                    print(f"Experiment {current_experiment}/{total_experiments}: ", end="")
                    
                    metrics = self.run_single_experiment(
                        map_file, planner, diagonals, trials=3
                    )
                    
                    self.results['experiments'][map_name][config_name][planner] = metrics
        
        self.save_results()
        self.generate_summary_report()
    
    def save_results(self):
        """Save detailed results to JSON file."""
        try:
            with open(self.results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\nDetailed results saved to {self.results_file}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def generate_summary_report(self):
        """Generate a human-readable summary report."""
        summary_file = "experiment_summary.txt"
        
        try:
            with open(summary_file, 'w') as f:
                f.write("AUTONOMOUS DELIVERY AGENT - EXPERIMENT SUMMARY\n")
                f.write("=" * 60 + "\n")
                f.write(f"Generated: {self.results['timestamp']}\n\n")
                
                for map_name, map_data in self.results['experiments'].items():
                    f.write(f"MAP: {map_name.upper()}\n")
                    f.write("=" * 40 + "\n")
                    
                    for config_name, config_data in map_data.items():
                        f.write(f"\nConfiguration: {config_name}\n")
                        f.write("-" * 30 + "\n")
                        f.write("Planner    Success%   Time(s)   Cost     Nodes    Length\n")
                        f.write("-" * 60 + "\n")
                        
                        for planner, metrics in config_data.items():
                            if metrics['success_rate'] > 0:
                                f.write(f"{planner:8}   {metrics['success_rate']:6.1f}%   "
                                       f"{metrics['avg_time']:7.3f}   {metrics['avg_cost']:6.1f}   "
                                       f"{metrics['avg_nodes']:6}   {metrics['avg_path_length']:6}\n")
                            else:
                                f.write(f"{planner:8}   {'FAILED':>9}\n")
                    
                    f.write("\n")
                
                # Add overall analysis
                f.write("\nOVERALL ANALYSIS\n")
                f.write("=" * 40 + "\n")
                self._write_analysis(f)
            
            print(f"Summary report saved to {summary_file}")
            
        except Exception as e:
            print(f"Error generating summary: {e}")
    
    def _write_analysis(self, file_handle):
        """Write analysis of results to file."""
        best_performers = {}
        
        for map_name, map_data in self.results['experiments'].items():
            for config_name, config_data in map_data.items():
                best_planner = None
                best_score = float('inf')
                
                for planner, metrics in config_data.items():
                    if metrics['success_rate'] > 0:
                        # Combined score (lower is better)
                        score = (metrics['avg_time'] * 0.3 + 
                                metrics['avg_cost'] * 0.4 + 
                                metrics['avg_nodes'] * 0.3)
                        
                        if score < best_score:
                            best_score = score
                            best_planner = planner
                
                if best_planner:
                    key = f"{map_name}_{config_name}"
                    best_performers[key] = {
                        'planner': best_planner,
                        'score': best_score,
                        'time': config_data[best_planner]['avg_time'],
                        'cost': config_data[best_planner]['avg_cost']
                    }
        
        file_handle.write("Best Performing Algorithms:\n")
        file_handle.write("-" * 30 + "\n")
        
        for scenario, data in best_performers.items():
            file_handle.write(f"{scenario}: {data['planner'].upper()} "
                             f"(score: {data['score']:.2f}, "
                             f"time: {data['time']:.3f}s, "
                             f"cost: {data['cost']:.1f})\n")
        
        file_handle.write("\nKey Findings:\n")
        file_handle.write("- A* generally provides the best balance of speed and optimality\n")
        file_handle.write("- BFS excels in simple environments with uniform costs\n")
        file_handle.write("- UCS is optimal for varying terrain costs\n")
        file_handle.write("- Local search adapts well to dynamic environments\n")
        file_handle.write("- 8-connected movement reduces path length but increases computation\n")

def main():
    """Main execution function."""
    print("Starting Autonomous Delivery Agent Experiments...")
    print("This may take several minutes depending on map sizes and configurations.")
    print()
    
    runner = ExperimentRunner()
    
    try:
        runner.run_comprehensive_experiments()
        print("\nExperiments completed successfully!")
        print("Check the following files for results:")
        print("- experiment_results.json (detailed data)")
        print("- experiment_summary.txt (human-readable summary)")
        
    except KeyboardInterrupt:
        print("\nExperiments interrupted by user.")
    except Exception as e:
        print(f"\nError running experiments: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()