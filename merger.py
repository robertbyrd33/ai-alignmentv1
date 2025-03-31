#!/usr/bin/env python3
"""
Merger Script

This script merges the content of all component group, component, subcomponent, 
and literature JSON files into a single file called "merged_files.json".

Usage:
    python merger.py
"""

import os
import json
import glob

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def find_all_json_files():
    """Find all relevant JSON files to merge."""
    # Base directory (current directory)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Directories to search
    directories = {
        'component_group': ['.'],  # Root directory for component group
        'component': ['components'],
        'subcomponent': ['subcomponents'],
        'literature': ['literature']
    }
    
    # Store all found JSON files
    all_files = {}
    
    # Search for JSON files in each directory
    for category, dirs in directories.items():
        all_files[category] = []
        for directory in dirs:
            dir_path = os.path.join(base_dir, directory)
            if os.path.exists(dir_path):
                # Find all JSON files in this directory
                json_files = glob.glob(os.path.join(dir_path, '*.json'))
                all_files[category].extend(json_files)
    
    return all_files

def merge_files():
    """Merge all relevant JSON files into a single structure."""
    # Find all JSON files
    all_files = find_all_json_files()
    
    # Create the merged data structure
    merged_data = {
        "component_groups": [],
        "components": [],
        "subcomponents": [],
        "literature": []
    }
    
    # Process each category
    for category, file_paths in all_files.items():
        for file_path in file_paths:
            # Load the JSON data
            data = load_json_file(file_path)
            if data:
                # Only include JSON files, skip others
                if isinstance(data, dict):
                    # Add the file path as metadata
                    data['_file_path'] = file_path
                    
                    # Special case for component group (likely just one file)
                    if category == 'component_group':
                        merged_data['component_groups'].append(data)
                    elif category == 'component':
                        merged_data['components'].append(data)
                    elif category == 'subcomponent':
                        merged_data['subcomponents'].append(data)
                    elif category == 'literature':
                        merged_data['literature'].append(data)
    
    return merged_data

def save_merged_data(merged_data, output_file='merged_files.json'):
    """Save the merged data to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(merged_data, file, indent=2, ensure_ascii=False)
        print(f"Successfully merged files into {output_file}")
        
        # Print stats about what was merged
        print("\nMerged file statistics:")
        for category, items in merged_data.items():
            print(f"  {category}: {len(items)} files")
    except Exception as e:
        print(f"Error saving merged data: {e}")

def main():
    print("Starting to merge files...")
    merged_data = merge_files()
    save_merged_data(merged_data)
    print("Merge completed.")

if __name__ == "__main__":
    main() 