"""
Script to load and analyze JSON files using the enhanced json_handler module.
"""
import os
import numpy as np
import json
from .json_handler import load_json_file, extract_json_structure_metadata, convert_json_to_tensor

def main():
    """
    Load and analyze JSON files using the enhanced json_handler module.
    """
    # List of files to process
    files = [
        'states.json',
        'countries.json'
    ]
    
    for file_name in files:
        file_path = os.path.join(os.path.dirname(__file__), file_name)
        print(f"\n{'='*80}")
        print(f"Processing file: {file_name}")
        print(f"{'='*80}")
        
        try:
            # Load the JSON file
            data, metadata = load_json_file(file_path)
            
            # Display basic information
            print(f"\nFile size: {metadata['file_size']} bytes")
            print(f"Encoding: {metadata['encoding']}")
            
            # Show JSON structure information
            print(f"\nStructure Information:")
            print(f"  - Maximum depth: {metadata['max_depth']}")
            print(f"  - Total nodes: {metadata['total_nodes']}")
            print(f"  - Type distribution: {metadata['type_distribution']}")
            
            # Display a sample of the data
            print("\nData Sample:")
            if isinstance(data, dict):
                # For dictionaries, show the keys and a sample of values
                print(f"  - Keys: {list(data.keys())[:10]}{' (truncated)' if len(data.keys()) > 10 else ''}")
                # Sample 2-3 key-value pairs
                sample_items = list(data.items())[:3]
                for k, v in sample_items:
                    print(f"  - {k}: {str(v)[:100]}{' (truncated)' if len(str(v)) > 100 else ''}")
            elif isinstance(data, list):
                # For lists, show the length and a few sample items
                print(f"  - List with {len(data)} items")
                for i, item in enumerate(data[:3]):
                    print(f"  - [{i}]: {str(item)[:100]}{' (truncated)' if len(str(item)) > 100 else ''}")
            else:
                # For other types, just show the data
                print(f"  - {str(data)[:200]}")
                
            # Convert to tensor representation
            tensor, tensor_metadata = convert_json_to_tensor(data)
            print(f"\nTensor Representation:")
            print(f"  - Shape: {tensor.shape}")
            print(f"  - Encoding method: {tensor_metadata['encoding_method']}")
            
            # Display some common patterns found
            if 'common_patterns' in metadata and metadata['common_patterns']:
                print("\nCommon Path Patterns:")
                for pattern, count in metadata['common_patterns'][:5]:
                    print(f"  - {pattern} ({count} occurrences)")
            
        except Exception as e:
            print(f"ERROR processing file {file_name}: {str(e)}")
            
    print("\nProcessing complete!")

if __name__ == "__main__":
    main()
