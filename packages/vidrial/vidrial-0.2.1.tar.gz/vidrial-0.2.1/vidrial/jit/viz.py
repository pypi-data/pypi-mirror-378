"""
Interactive visualization dashboard for CUDA kernel timing analysis.

This module provides functionality to:
- Load timing data from YAML files
- Generate interactive dashboards with filtering capabilities
- Support snapshot comparison for performance analysis
- Create publication-ready visualizations
"""

import yaml
import json
import os
from typing import Dict, List, Any, Set, Union
from pathlib import Path


def custom_yaml_constructor(loader, tag_suffix, node):
    """Handle custom YAML tags by converting them to string representations."""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    elif isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    else:
        return str(node)


def load_timing_data(yaml_path: str) -> Dict[str, List[Dict]]:
    """
    Load timing data from YAML file with custom object handling.
    
    Args:
        yaml_path: Path to the YAML timing cache file
        
    Returns:
        Dictionary mapping problem shapes to lists of timing configurations
    """
    # Create a custom YAML loader that handles unknown tags
    CustomLoader = yaml.SafeLoader
    CustomLoader.add_multi_constructor('', custom_yaml_constructor)
    
    with open(yaml_path, 'r') as f:
        data = yaml.load(f, Loader=CustomLoader)
    
    return data


def process_timing_data_for_dashboard(timings_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process timing data to match the dashboard.js data structure expectations.
    
    Args:
        timings_data: Raw timing data from YAML
        
    Returns:
        Dictionary with processed data for dashboard
    """
    # Flatten all timing records and add problem_shape field
    raw_data = []
    
    for problem_shape_hash, problem_list in timings_data.items():
        # Each problem shape maps to a list, usually with one item containing 'timings'
        for problem_data in problem_list:
            if 'timings' in problem_data:
                for timing_entry in problem_data['timings']:
                    # Each timing entry has 'config' and timing results
                    if 'config' in timing_entry:
                        record = timing_entry['config'].copy()
                        
                        # Convert complex values to strings for consistent filtering
                        for key, value in record.items():
                            if isinstance(value, (list, dict)):
                                record[key] = str(value)
                        
                        # Add timing results to the record
                        for key, value in timing_entry.items():
                            if key != 'config':
                                record[key] = value
                        
                        # Add problem shape identifier
                        record['problem_shape'] = problem_shape_hash
                        raw_data.append(record)
    
    # Extract configuration attributes from the 'config' sections
    config_attributes = {}
    timing_keys = {'time', 'n', 'std', 'gflops', 'memory_gb', 'tensor_utilization', 'problem_shape'}
    
    for record in raw_data:
        for key, value in record.items():
            if key not in timing_keys:
                if key not in config_attributes:
                    config_attributes[key] = {
                        'values': set(),
                        'type': type(value).__name__
                    }
                
                # Convert unhashable types to strings for set storage
                if isinstance(value, (list, dict)):
                    value_str = str(value)
                    # Also store the original type info for proper filtering
                    config_attributes[key]['has_complex_values'] = True
                else:
                    value_str = value
                    
                config_attributes[key]['values'].add(value_str)
    
    # Convert sets to sorted lists for JSON serialization
    for attr_data in config_attributes.values():
        attr_data['values'] = sorted(list(attr_data['values']))
    
    # Get unique problem shapes
    problem_shapes = sorted(list(timings_data.keys()))
    
    return {
        'rawData': raw_data,
        'configAttributes': config_attributes,
        'problemShapes': problem_shapes
    }


def get_dashboard_assets() -> Dict[str, str]:
    """
    Load dashboard HTML, CSS, and JavaScript assets from the viz directory.
    
    Returns:
        Dictionary containing 'html', 'css', and 'js' asset contents
    """
    viz_dir = Path(__file__).parent / 'viz'
    
    assets = {}
    
    # Load HTML template
    html_path = viz_dir / 'dashboard.html'
    if html_path.exists():
        with open(html_path, 'r') as f:
            assets['html'] = f.read()
    else:
        raise FileNotFoundError(f"HTML template not found at {html_path}")
    
    # Load CSS
    css_path = viz_dir / 'styles.css'
    if css_path.exists():
        with open(css_path, 'r') as f:
            assets['css'] = f.read()
    else:
        raise FileNotFoundError(f"CSS file not found at {css_path}")
    
    # Load JavaScript
    js_path = viz_dir / 'dashboard.js'
    if js_path.exists():
        with open(js_path, 'r') as f:
            assets['js'] = f.read()
    else:
        raise FileNotFoundError(f"JavaScript file not found at {js_path}")
    
    return assets


def generate_dashboard_html(timings_data: Dict[str, List[Dict]], output_path: str) -> None:
    """
    Generate complete HTML dashboard with embedded assets and data.
    
    Args:
        timings_data: Dictionary of problem shapes to timing configurations
        output_path: Path where the HTML file should be saved
    """
    # Process the data for the dashboard
    dashboard_data = process_timing_data_for_dashboard(timings_data)
    
    # Load dashboard assets
    assets = get_dashboard_assets()
    
    # Build the complete HTML
    html_template = assets['html']
    
    # Replace external CSS link with inline styles
    html_with_css = html_template.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<style>\n{assets["css"]}\n</style>'
    )
    
    # Replace the dashboard data placeholder
    html_with_data = html_with_css.replace(
        'window.DASHBOARD_DATA = {\n            rawData: [],\n            configAttributes: {},\n            problemShapes: []\n        };',
        f'window.DASHBOARD_DATA = {json.dumps(dashboard_data, indent=8)};'
    )
    
    # Replace external JS script with inline script
    final_html = html_with_data.replace(
        '<script src="dashboard.js"></script>',
        f'<script>\n{assets["js"]}\n</script>'
    )
    
    # Write the final HTML file
    with open(output_path, 'w') as f:
        f.write(final_html)
    
    print(f"Dashboard generated: {output_path}")
    print(f"Data summary: {len(dashboard_data['problemShapes'])} problem shapes, {len(dashboard_data['rawData'])} total configurations")


def main():
    """Main function for command-line usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python viz.py <yaml_file> [output_file]")
        return
    
    yaml_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "kernel_dashboard.html"
    
    try:
        data = load_timing_data(yaml_file)
        generate_dashboard_html(data, output_file)
        print(f"Dashboard successfully generated: {output_file}")
    except Exception as e:
        print(f"Error generating dashboard: {e}")


if __name__ == "__main__":
    main()