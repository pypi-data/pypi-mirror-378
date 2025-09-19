#!/usr/bin/env python3
"""
TensorPack: Streamlined CLI tool for tensor-matrix conversions

A focused command-line interface for tensor_to_matrix and matrix_to_tensor functionality 
from MatrixTransformer, providing essential conversion capabilities.

Features:
- Direct tensor to matrix conversions with metadata
- Matrix to tensor reconstruction with original shape preservation
- Support for multiple file formats
- Error estimation and verification
"""

import os
import sys
import json
import re
import argparse
import traceback
import numpy as np
import logging
import time
import re
import datetime
from pathlib import Path
import traceback
from typing import Dict, Any, Optional, Tuple, List, Union, Callable, TypeVar, Type
import sys

import pandas as pd

# Early suppression of ML library outputs (before any ML imports happen)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'

# Suppress tqdm progress bars globally
try:
    # Simple approach: just set environment variable to disable tqdm
    os.environ['TQDM_DISABLE'] = '1'
    
    # Import and configure tqdm to be silent
    import tqdm
    
    # Patch tqdm constructor to always be disabled
    _original_tqdm_init = tqdm.tqdm.__init__
    def _silent_tqdm_init(self, *args, **kwargs):
        kwargs['disable'] = True
        kwargs['leave'] = False
        return _original_tqdm_init(self, *args, **kwargs)
    
    tqdm.tqdm.__init__ = _silent_tqdm_init
    
    # Configure pandas tqdm integration
    try:
        tqdm.pandas(disable=True)
    except:
        pass
        
except ImportError:
    pass

import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

def suppress_ml_outputs():
    """Aggressively suppress all ML library outputs and progress bars."""
    import os
    import warnings
    import logging
    
    # Environment variables for various libraries
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
    os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
    os.environ['WANDB_SILENT'] = 'true'
    os.environ['DATASETS_VERBOSITY'] = 'error'
    
    # Suppress all warnings
    warnings.filterwarnings('ignore')
    
    # Set all ML library loggers to ERROR level
    ml_loggers = [
        'tensorflow', 'tf_keras', 'absl', 'transformers', 'sentence_transformers',
        'datasets', 'huggingface_hub', 'torch', 'torchvision', 'sklearn',
        'matplotlib', 'PIL', 'urllib3', 'requests', 'numpy', 'pandas'
    ]
    
    for logger_name in ml_loggers:
        logging.getLogger(logger_name).setLevel(logging.ERROR)
        logging.getLogger(logger_name).propagate = False
    
    # Additional tqdm suppression (if not already done above)
    try:
        import tqdm
        # Only patch if not already patched
        if not hasattr(tqdm.tqdm.__init__, '_tensorpack_patched'):
            original_init = tqdm.tqdm.__init__
            def safe_silent_init(self, *args, **kwargs):
                kwargs['disable'] = True
                kwargs['leave'] = False
                try:
                    return original_init(self, *args, **kwargs)
                except Exception:
                    # Fallback to basic initialization if patching fails
                    pass
            safe_silent_init._tensorpack_patched = True
            tqdm.tqdm.__init__ = safe_silent_init
    except ImportError:
        pass

# Call the suppression function immediately
suppress_ml_outputs()

# Quantum Virtual Memory integration removed; keep a minimal compatibility config
_QVM_INSTANCE = None
_QVM_CONFIG = {
    'large_file_threshold': 100 * 1024 * 1024  # 100MB threshold (kept for compatibility)
}

# OCR configuration for image processing
_OCR_CONFIG = {
    'extract_ocr_on_load': False,  # Whether to extract text automatically when loading images
    'confidence_threshold': 0.5,   # Confidence threshold for OCR results
    'default_lang': 'en',          # Default language for OCR
    'use_gpu': False,              # Whether to use GPU for OCR (if available)
    'store_results_in_metadata': True,  # Save OCR results in metadata
    'include_in_entity_search': True,   # Include OCR text in entity search results
    'video_processing_enabled': False,  # Enable video frame extraction and OCR
}

# Registries for OCR data
_OCR_INDEX_REGISTRY = {}  # Maps array IDs to OCR indices
_OCR_DATA_REGISTRY = {}   # Maps array IDs to raw OCR data

def get_quantum_vm_instance():
    """QVM removed: callers should use standard memory.

    Kept for backward compatibility; always returns None.
    """
    return None


def configure_qvm(*args, **kwargs):
    """Compatibility no-op for older callers.

    Accepts the same parameters but does nothing beyond updating the
    compatibility config for large_file_threshold when provided.
    """
    global _QVM_CONFIG
    large_file_threshold = kwargs.get('large_file_threshold') if kwargs else None
    if large_file_threshold is not None:
        _QVM_CONFIG['large_file_threshold'] = large_file_threshold
        logging.info(f"QVM compatibility threshold updated: {_QVM_CONFIG['large_file_threshold']}")

def configure_ocr(extract_on_load=None, confidence_threshold=None, 
                 default_lang=None, use_gpu=None, store_in_metadata=None, 
                 include_in_search=None, video_processing=None):
    """
    Configure OCR settings for image and video text extraction.
    
    Args:
        extract_on_load: Whether to extract text automatically when loading images
        confidence_threshold: Minimum confidence score for OCR results (0.0-1.0)
        default_lang: Default language for OCR (e.g., 'en', 'fr', 'ja', etc.)
        use_gpu: Whether to use GPU for OCR processing if available
        store_in_metadata: Store OCR results in image metadata
        include_in_search: Include OCR text in entity search results
        video_processing: Enable video frame extraction and OCR
    """
    global _OCR_CONFIG
    
    # Update settings that are provided
    if extract_on_load is not None:
        _OCR_CONFIG['extract_ocr_on_load'] = extract_on_load
    if confidence_threshold is not None:
        _OCR_CONFIG['confidence_threshold'] = confidence_threshold
    if default_lang is not None:
        _OCR_CONFIG['default_lang'] = default_lang
    if use_gpu is not None:
        _OCR_CONFIG['use_gpu'] = use_gpu
    if store_in_metadata is not None:
        _OCR_CONFIG['store_results_in_metadata'] = store_in_metadata
    if include_in_search is not None:
        _OCR_CONFIG['include_in_entity_search'] = include_in_search
    if video_processing is not None:
        _OCR_CONFIG['video_processing_enabled'] = video_processing
    
    # Update OCR integration configuration if module is available
    try:
        from .ocr_integration import configure_ocr as configure_ocr_integration
        configure_ocr_integration(
            lang=_OCR_CONFIG['default_lang'],
            confidence_threshold=_OCR_CONFIG['confidence_threshold'],
            video_frame_interval=_OCR_CONFIG.get('video_frame_interval', 10),
            max_frames=_OCR_CONFIG.get('max_frames', 300)
        )
    except ImportError:
        logging.warning("OCR integration module not available for configuration")
    except Exception as e:
        logging.error(f"Error configuring OCR integration: {e}")
        
    logging.info(f"OCR configuration updated: {_OCR_CONFIG}")

def create_silent_sentence_transformer(model_name='all-MiniLM-L6-v2'):
    """Create a SentenceTransformer with all outputs suppressed."""
    import logging
    import warnings
    
    # Temporarily set even stricter logging
    old_level = logging.getLogger().level
    old_transformers_level = logging.getLogger('transformers').level
    old_sentence_level = logging.getLogger('sentence_transformers').level
    
    try:
        # Set ultra-quiet mode
        logging.getLogger().setLevel(logging.CRITICAL)
        logging.getLogger('transformers').setLevel(logging.CRITICAL)
        logging.getLogger('sentence_transformers').setLevel(logging.CRITICAL)
        logging.getLogger('tensorflow').setLevel(logging.CRITICAL)
        logging.getLogger('torch').setLevel(logging.CRITICAL)
        
        # Suppress warnings during import and creation
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(model_name, device='cpu')
            
        return model
        
    finally:
        # Restore original logging levels
        logging.getLogger().setLevel(old_level)
        logging.getLogger('transformers').setLevel(old_transformers_level)
        logging.getLogger('sentence_transformers').setLevel(old_sentence_level)

# Import helper functions for entity extraction and pathway analysis
try:
    from .entity_extraction import _extract_key_entities_from_dataset
except ImportError:
    # Fallback implementation
    def _extract_key_entities_from_dataset(dataset, metadata):
        """Extract key entities from dataset metadata (fallback implementation)"""
        key_entities = []
        if metadata and metadata.get('is_tabular') and 'columns' in metadata:
            key_entities.extend(metadata['columns'][:5])
        return key_entities

# === Global helper metric functions (exposed for unit tests) ===
def frac_zero(a: np.ndarray) -> float:
    if not isinstance(a, np.ndarray) or a.size == 0:
        return 0.0
    return float(np.count_nonzero(a == 0) / a.size)

def frac_nan(a: np.ndarray) -> float:
    if not isinstance(a, np.ndarray) or not np.issubdtype(a.dtype, np.number):
        return 0.0
    return float(np.count_nonzero(np.isnan(a)) / a.size)

def is_integer_like(a: np.ndarray) -> bool:
    if not isinstance(a, np.ndarray) or not np.issubdtype(a.dtype, np.number):
        return False
    sample = a.ravel()
    if sample.size > 50_000:
        sample = sample[:50_000]
    return np.mean(np.abs(sample - np.round(sample))) < 1e-6

def is_nonnegative(a: np.ndarray) -> bool:
    try:
        return isinstance(a, np.ndarray) and np.all(a >= 0)
    except Exception:
        return False

def estimate_rank(a: np.ndarray, energy_ratio: float = 0.95):
    if not isinstance(a, np.ndarray) or a.ndim != 2:
        return None
    try:
        M, N = a.shape
        if M * N > 40_000:
            sub = a[:min(M, 200), :min(N, 200)]
        else:
            sub = a
        u, s, vh = np.linalg.svd(sub, full_matrices=False)
        total = np.sum(s**2)
        if total == 0:
            return None
        cum = np.cumsum(s**2)
        r = np.searchsorted(cum, energy_ratio * total) + 1
        return r, len(s)
    except Exception:
        return None

def symmetry_score(a: np.ndarray) -> float:
    if not isinstance(a, np.ndarray) or a.ndim != 2 or a.shape[0] != a.shape[1]:
        return 0.0
    n = a.shape[0]
    if n > 800:
        sub = a[:400, :400]
    else:
        sub = a
    denom = np.linalg.norm(sub) + 1e-12
    return 1.0 - (np.linalg.norm(sub - sub.T) / denom)

def diagonal_dominance(a: np.ndarray) -> float:
    if not isinstance(a, np.ndarray) or a.ndim != 2 or a.shape[0] != a.shape[1]:
        return 0.0
    diag = np.abs(np.diag(a))
    if diag.size == 0:
        return 0.0
    off = np.abs(a) - np.diag(diag)
    mean_off = (np.sum(off) / max(off.size, 1))
    mean_diag = np.mean(diag)
    if mean_off == 0:
        return 1.0
    return float(mean_diag / (mean_off + 1e-12))


            
    

# Try to import torch, but make it optional
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Import MatrixTransformer - adjust path as needed
try:
    from .matrixtransformer import MatrixTransformer
    from .license_manager import LicenseManager
except ImportError as e:
    print(f"Error: Required module not found - {e}. Please ensure it's installed correctly.")
    sys.exit(1)







def setup_logging(verbose: bool = False, log_file: str = None) -> None:
    """Configure logging level based on verbose flag and optional log file."""
    import os
    import warnings
    
    # Suppress TensorFlow and ML library outputs
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow INFO, WARNING, and ERROR messages
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations to reduce messages
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Suppress tokenizer warnings
    
    # Suppress warnings from various ML libraries
    warnings.filterwarnings('ignore', category=UserWarning, module='torch')
    warnings.filterwarnings('ignore', category=UserWarning, module='transformers')
    warnings.filterwarnings('ignore', category=FutureWarning, module='transformers')
    warnings.filterwarnings('ignore', category=DeprecationWarning, module='tensorflow')
    warnings.filterwarnings('ignore', category=UserWarning, module='tensorflow')
    warnings.filterwarnings('ignore', category=FutureWarning, module='tensorflow')
    
    level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Suppress specific library loggers unless in verbose mode
    if not verbose:
        # TensorFlow loggers
        logging.getLogger('tensorflow').setLevel(logging.ERROR)
        logging.getLogger('tf_keras').setLevel(logging.ERROR)
        logging.getLogger('absl').setLevel(logging.ERROR)
        
        # Transformers and ML library loggers
        logging.getLogger('transformers').setLevel(logging.ERROR)
        logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
        logging.getLogger('datasets').setLevel(logging.ERROR)
        logging.getLogger('huggingface_hub').setLevel(logging.ERROR)
        
        # PyTorch loggers
        logging.getLogger('torch').setLevel(logging.ERROR)
        logging.getLogger('torchvision').setLevel(logging.ERROR)
        
        # Other common ML libraries
        logging.getLogger('sklearn').setLevel(logging.ERROR)
        logging.getLogger('matplotlib').setLevel(logging.ERROR)
        logging.getLogger('PIL').setLevel(logging.ERROR)
        logging.getLogger('urllib3').setLevel(logging.ERROR)
    
    # Add file handler if log file is specified
    if log_file:
        # Create directory for log file if it doesn't exist
        log_dir = os.path.dirname(os.path.abspath(log_file))
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # Add the file handler to the root logger
        logging.getLogger().addHandler(file_handler)
        
        logging.info(f"Logging to file: {log_file}")


# Global registry to store original data metadata for entity search
# Global metadata storage for matrices
_GENERAL_METADATA = {}

# Entity registry for bidirectional entity-to-matrix mapping
_ENTITY_REGISTRY = {}

def _store_general_metadata(file_path: str, original_data, array, data_type: str, extra_info: dict = None):
    """Store original data metadata for later entity search across all file types."""
    global _GENERAL_METADATA
    array_id = id(array)
    
    # Get array shape
    shape = array.shape
    
    metadata = {
        'original_data': original_data,
        'file_path': file_path,
        'data_type': data_type,
        'shape': shape,
        'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
        'entity_map': {},  # Maps matrix coordinates to entity information
        'entity_ids': [],  # List of entity IDs in this matrix
        'domain_context': {},  # Domain-specific context information
        'semantic_index': {},    # NEW: For enhanced JSON searchability
        'entity_locations': {},  # NEW: Fast entity lookup
        'search_cache': {}       # NEW: Pre-computed search patterns
    }
    
    # Add extra information if provided
    if extra_info:
        metadata.update(extra_info)
        
        # Special handling for JSON semantic index
        if 'hierarchical_metadata' in extra_info and 'semantic_index' in extra_info.get('hierarchical_metadata', {}):
            semantic_data = extra_info['hierarchical_metadata']['semantic_index']
            metadata['semantic_index'] = semantic_data
            metadata['entity_locations'] = semantic_data.get('entity_locations', {})
            metadata['search_cache'] = semantic_data.get('search_cache', {})
    
    # For DataFrame-like data, extract useful structure info
    if hasattr(original_data, 'columns') and hasattr(original_data, 'iloc'):
        metadata.update({
            'columns': original_data.columns.tolist(),
            'dataframe': original_data,
            'is_tabular': True
        })
                    
    elif isinstance(original_data, (list, tuple)):
        metadata.update({
            'length': len(original_data),
            'is_sequence': True
        })
    elif isinstance(original_data, str):
        metadata.update({
            'text_length': len(original_data),
            'text_preview': original_data,  # Store complete text content - no limits
            'is_text': True
        })
    
    _GENERAL_METADATA[array_id] = metadata

def _store_dataframe_metadata(file_path: str, dataframe, array: np.ndarray):
    """Legacy function - now uses general metadata storage."""
    _store_general_metadata(file_path, dataframe, array, 'tabular', {
        'columns': dataframe.columns.tolist(),
        'dataframe': dataframe
    })

def _get_dataframe_metadata(array: np.ndarray):
    """Retrieve original dataframe metadata for an array (legacy compatibility)."""
    metadata = _get_general_metadata(array)
    if metadata and metadata.get('is_tabular'):
        return metadata
    return None

def _get_general_metadata(array: np.ndarray):
    """Retrieve original data metadata for an array."""
    global _GENERAL_METADATA
    array_id = id(array)
    return _GENERAL_METADATA.get(array_id, None)

def _clear_dataframe_metadata():
    """Clear the metadata registry."""
    global _GENERAL_METADATA, _ENTITY_REGISTRY
    _GENERAL_METADATA.clear()
    if '_ENTITY_REGISTRY' in globals():
        _ENTITY_REGISTRY.clear()


def _register_entity(entity_id: str, entity_info: dict, matrix: np.ndarray = None, coordinates: tuple = None):
    """
    Register or update an entity in the global entity registry and link to matrix coordinates.
    
    Args:
        entity_id: Unique identifier for the entity
        entity_info: Dictionary containing entity information
        matrix: Matrix containing the entity (optional)
        coordinates: Tuple of ((row_start, row_end), (col_start, col_end)) for entity location (optional)
    
    Returns:
        bool: Success status
    """
    global _ENTITY_REGISTRY, _GENERAL_METADATA
    
    # Create or update entity in registry
    if entity_id not in _ENTITY_REGISTRY:
        _ENTITY_REGISTRY[entity_id] = {
            'info': entity_info,
            'matrix_locations': [],
            'relationships': [],
            'semantic_context': {}
        }
    else:
        # Update existing entity
        _ENTITY_REGISTRY[entity_id]['info'].update(entity_info)
    
    # If matrix and coordinates are provided, link entity to matrix location
    if matrix is not None:
        array_id = id(matrix)
        logging.debug(f"Registering entity {entity_id} for matrix {array_id}")
        
        # Add basic location even without coordinates
        location = {
            'array_id': array_id,
            'coordinates': coordinates if coordinates else (0, 0)
        }
        
        # Avoid duplicate locations
        if not any(loc['array_id'] == array_id and loc['coordinates'] == location['coordinates'] 
                for loc in _ENTITY_REGISTRY[entity_id]['matrix_locations']):
            _ENTITY_REGISTRY[entity_id]['matrix_locations'].append(location)
            logging.debug(f"Added matrix location for entity {entity_id}")
        
        # Update matrix metadata to link to this entity
        metadata = _GENERAL_METADATA.get(array_id)
        if metadata is None:
            logging.warning(f"No metadata found for array {array_id}, creating empty metadata")
            metadata = _GENERAL_METADATA[array_id] = {}
        
        # Create coordinate key for entity map (simplified format for consistency)
        if coordinates:
            # Use center point of the region as the key
            center_row = (coordinates[0][0] + coordinates[0][1]) // 2
            center_col = (coordinates[1][0] + coordinates[1][1]) // 2
            coord_key = f"{center_row},{center_col}"
        else:
            # No coordinates provided, just use entity_id as key
            coord_key = f"entity_{entity_id}"
        
        # Add entity to matrix's entity map
        if 'entity_map' not in metadata:
            metadata['entity_map'] = {}
        metadata['entity_map'][coord_key] = entity_id
        
        # Update entity_ids list if needed
        if 'entity_ids' not in metadata:
            metadata['entity_ids'] = []
        if entity_id not in metadata['entity_ids']:
            metadata['entity_ids'].append(entity_id)
        
        logging.debug(f"Registered entity '{entity_id}' at array_id {array_id} with coord_key '{coord_key}'")
    
    return True


def _get_entities_in_matrix(matrix: np.ndarray):
    """
    Retrieve all entities mapped to locations in the specified matrix.
    
    Args:
        matrix: The matrix to search for entities
    
    Returns:
        dict: Dictionary mapping coordinate keys to entity information
    """
    global _GENERAL_METADATA, _ENTITY_REGISTRY
    
    array_id = id(matrix)
    metadata = _GENERAL_METADATA.get(array_id)
    
    logging.debug(f"_get_entities_in_matrix: array_id={array_id}, matrix_shape={matrix.shape}")
    logging.debug(f"Available metadata keys: {list(_GENERAL_METADATA.keys())}")
    
    if not metadata:
        logging.debug(f"No metadata found for array_id {array_id}")
        return {}
    
    if not metadata.get('entity_map'):
        logging.debug(f"No entity_map in metadata for array_id {array_id}")
        return {}
    
    result = {}
    entity_map = metadata['entity_map']
    logging.debug(f"Found entity_map with {len(entity_map)} entries")
    
    for coord_key, entity_id in entity_map.items():
        if entity_id in _ENTITY_REGISTRY:
            result[coord_key] = {
                'entity_id': entity_id,
                'info': _ENTITY_REGISTRY[entity_id]['info']
            }
            logging.debug(f"Added entity {entity_id} at {coord_key}")
        else:
            logging.warning(f"Entity {entity_id} not found in registry")
    
    logging.debug(f"Returning {len(result)} entities")
    return result


def _find_entity_by_id(entity_id: str):
    """
    Find entity by its ID and return all its information including matrix locations.
    
    Args:
        entity_id: The entity ID to search for
        
    Returns:
        dict: Entity information or None if not found
    """
    global _ENTITY_REGISTRY
    return _ENTITY_REGISTRY.get(entity_id)


def _map_entities_to_matrix_regions(matrix: np.ndarray, entity_map: dict):
    """
    Map multiple entities to regions in a matrix.
    
    Args:
        matrix: The matrix to map entities to
        entity_map: Dictionary mapping entity IDs to coordinate tuples:
                    {entity_id: ((row_start, row_end), (col_start, col_end)), ...}
    
    Returns:
        bool: Success status
    """
    array_id = id(matrix)
    logging.debug(f"_map_entities_to_matrix_regions: array_id={array_id}, mapping {len(entity_map)} entities")
    
    for entity_id, coordinates in entity_map.items():
        if entity_id not in _ENTITY_REGISTRY:
            # Create a basic entity if it doesn't exist
            logging.debug(f"Creating new entity '{entity_id}' in registry")
            _register_entity(entity_id, {'name': entity_id})
        
        # Map this entity to the matrix region - preserve existing entity info
        existing_info = _ENTITY_REGISTRY.get(entity_id, {}).get('info', {})
        logging.debug(f"Mapping entity '{entity_id}' to coordinates {coordinates} with info: {existing_info}")
        _register_entity(entity_id, existing_info, matrix, coordinates)
    
    # Verify the mapping worked
    entities_in_matrix = _get_entities_in_matrix(matrix)
    logging.debug(f"After mapping, matrix contains {len(entities_in_matrix)} entities")
    
    return True


def _search_semantic_index(dataset: np.ndarray, search_entity: str, dataset_info: dict) -> List[dict]:
    """
    Search for entities using the semantic index for JSON datasets.
    
    Args:
        dataset: The dataset array
        search_entity: Entity to search for
        dataset_info: Dataset metadata
        
    Returns:
        List of semantic matches with enhanced context
    """
    matches = []
    
    # Get metadata for this dataset
    metadata = _get_general_metadata(dataset)
    if not metadata:
        return matches
    
    # Check if this dataset has semantic index data
    semantic_index = metadata.get('semantic_index', {})
    if not semantic_index:
        # No semantic index available — attempt a safe NDJSON fallback for
        # top-level JSON arrays (many JSON array files can be converted to
        # NDJSON or processed line-by-line). This keeps behavior conservative
        # while allowing simple entity searches without full indexing.
        try:
            data_type = dataset_info.get('data_type', '').lower() if dataset_info else ''
            file_path = dataset_info.get('file_path') if dataset_info else None
            if data_type in ('json_array', 'json') and file_path and os.path.exists(file_path):
                import json as _json
                with open(file_path, 'r', encoding='utf-8') as fh:
                    # Stream lines and treat each line as one JSON record (NDJSON-style)
                    for i, raw in enumerate(fh):
                        line = raw.strip()
                        if not line:
                            continue
                        # Fast substring check (case-insensitive) — conservative
                        if search_entity.lower() in line.lower():
                            # Try to extract a small context snippet
                            start = line.lower().find(search_entity.lower())
                            end = start + len(search_entity) if start >= 0 else 0
                            # Try to parse the entire line as JSON so callers can get the
                            # full NDJSON record; fall back to raw line when parsing fails.
                            try:
                                parsed_record = _json.loads(line)
                            except Exception:
                                parsed_record = None

                            matches.append({
                                'type': 'ndjson_fallback_match',
                                'value': search_entity,
                                'json_path': f'line[{i}]',
                                'tensor_coordinates': (0, start if start >= 0 else 0),
                                'character_range': (start, end) if start >= 0 else (0, 0),
                                'confidence': 0.6,
                                # keep a short human-readable context string, but include
                                # the full parsed record for downstream consumers
                                'context': f"fallback: NDJSON line match",
                                'full_record': parsed_record if parsed_record is not None else line,
                                'match_type': 'fallback',
                                'matcher_type': 'ndjson_fallback',
                                'dataset_name': dataset_info.get('file_path', 'unknown'),
                                'dataset_type': dataset_info.get('data_type', 'unknown')
                            })
                # If we found any matches via NDJSON fallback, return them
                if matches:
                    return matches
        except Exception:
            # If fallback fails, continue to return empty matches
            pass
        return matches
    
    # Search in entity locations
    entity_locations = semantic_index.get('entity_locations', {})
    string_entities = semantic_index.get('string_entities', {})
    value_mappings = semantic_index.get('value_mappings', {})
    
    # Exact match search
    if search_entity in entity_locations:
        for path, char_start, char_end in entity_locations[search_entity]:
            # Convert character position to tensor coordinates (approximation)
            tensor_row = char_start // dataset.shape[1] if dataset.shape[1] > 0 else 0
            tensor_col = char_start % dataset.shape[1] if dataset.shape[1] > 0 else 0
            
            matches.append({
                'type': 'semantic_exact_match',
                'value': search_entity,
                'json_path': path,
                'tensor_coordinates': (tensor_row, tensor_col),
                'character_range': (char_start, char_end),
                'confidence': 1.0,
                'context': f"Exact match at JSON path: {path}",
                'match_type': 'semantic',
                'matcher_type': 'semantic_index'
            })
    
    # Partial match search in string entities
    partial_matches = []
    search_lower = search_entity.lower()
    
    for entity_value, paths in string_entities.items():
        entity_lower = entity_value.lower()
        if search_lower in entity_lower or entity_lower in search_lower:
            similarity = len(search_lower) / max(len(entity_lower), len(search_lower))
            if similarity > 0.3:  # Threshold for partial matches
                for path in paths:
                    # Get character positions if available
                    char_positions = entity_locations.get(entity_value, [(path, 0, 0)])[0]
                    char_start, char_end = char_positions[1], char_positions[2]
                    
                    # Convert to tensor coordinates
                    tensor_row = char_start // dataset.shape[1] if dataset.shape[1] > 0 else 0
                    tensor_col = char_start % dataset.shape[1] if dataset.shape[1] > 0 else 0
                    
                    partial_matches.append({
                        'type': 'semantic_partial_match',
                        'value': entity_value,
                        'search_term': search_entity,
                        'json_path': path,
                        'tensor_coordinates': (tensor_row, tensor_col),
                        'character_range': (char_start, char_end),
                        'confidence': similarity,
                        'context': f"Partial match '{entity_value}' at JSON path: {path}",
                        'match_type': 'semantic_partial',
                        'matcher_type': 'semantic_index'
                    })
    
    # Sort partial matches by confidence and add top ones
    partial_matches.sort(key=lambda x: x['confidence'], reverse=True)
    matches.extend(partial_matches[:5])  # Top 5 partial matches
    
    # Add context information
    for match in matches:
        if 'json_path' in match:
            json_path = match['json_path']
            original_value = value_mappings.get(json_path)
            if original_value is not None:
                match['original_value'] = original_value
                
        # Add dataset context
        match['dataset_name'] = dataset_info.get('file_path', 'unknown')
        match['dataset_type'] = dataset_info.get('data_type', 'unknown')
    
    return matches


def _propagate_entities_through_transformation(source_matrix: np.ndarray, target_matrix: np.ndarray, 
                                              transformation_info: dict):
    """
    Propagate entity mappings through a matrix transformation.
    
    Args:
        source_matrix: Original matrix with entity mappings
        target_matrix: Transformed matrix 
        transformation_info: Information about the transformation that guides entity mapping
                            (should include 'type' and transformation-specific parameters)
    
    Returns:
        dict: Mapping of target matrix regions to entity IDs
    """
    source_entities = _get_entities_in_matrix(source_matrix)
    if not source_entities:
        return {}
    
    target_entity_map = {}
    transformation_type = transformation_info.get('type', 'unknown')
    
    # Handle different transformation types
    if transformation_type == 'linear':
        # For linear transformations, we can directly map coordinates using the transformation matrix
        for coord_key, entity_data in source_entities.items():
            # Parse source coordinates (simplified format: "row,col")
            try:
                src_coords = coord_key.split(',')
                if len(src_coords) == 2:
                    # Simple point coordinates
                    src_row = int(src_coords[0])
                    src_col = int(src_coords[1])
                    
                    # Apply linear transformation to point
                    transform_matrix = transformation_info.get('matrix', np.eye(2))
                    target_row = int(transform_matrix[0][0] * src_row + transform_matrix[0][1] * src_col)
                    target_col = int(transform_matrix[1][0] * src_row + transform_matrix[1][1] * src_col)
                    
                    # Ensure coordinates are within bounds
                    target_shape = target_matrix.shape
                    target_row = max(0, min(target_row, target_shape[0]-1))
                    target_col = max(0, min(target_col, target_shape[1]-1))
                    
                    # Create new coordinate key and register entity
                    target_coord_key = f"{target_row},{target_col}"
                    target_entity_map[target_coord_key] = entity_data['entity_id']
                    
                    # Update entity registry with new location
                    _register_entity(
                        entity_data['entity_id'], 
                        {'transformed_by': transformation_type},
                        target_matrix, 
                        ((target_row, target_row+1), (target_col, target_col+1))
                    )
                    
                else:
                    # Legacy format with ranges (like "0:3,0:3") - convert to center point
                    src_row_range = [int(x) for x in src_coords[0].split(':')]
                    src_col_range = [int(x) for x in src_coords[1].split(':')]
                    
                    # Use center point for transformation
                    src_row = (src_row_range[0] + src_row_range[1]) // 2
                    src_col = (src_col_range[0] + src_col_range[1]) // 2
                    
                    # Apply linear transformation
                    transform_matrix = transformation_info.get('matrix', np.eye(2))
                    target_row = int(transform_matrix[0][0] * src_row + transform_matrix[0][1] * src_col)
                    target_col = int(transform_matrix[1][0] * src_row + transform_matrix[1][1] * src_col)
                    
                    # Ensure coordinates are within bounds
                    target_shape = target_matrix.shape
                    target_row = max(0, min(target_row, target_shape[0]-1))
                    target_col = max(0, min(target_col, target_shape[1]-1))
                    
                    # Create new coordinate key and register entity
                    target_coord_key = f"{target_row},{target_col}"
                    target_entity_map[target_coord_key] = entity_data['entity_id']
                    
                    # Update entity registry
                    _register_entity(
                        entity_data['entity_id'], 
                        {'transformed_by': transformation_type},
                        target_matrix, 
                        ((target_row, target_row+1), (target_col, target_col+1))
                    )
            except (ValueError, IndexError) as e:
                logging.warning(f"Failed to parse coordinates '{coord_key}': {e}")
                continue
    
    elif transformation_type in ('blend', 'weighted_average'):
        # For blending, handle weighted propagation of entities
        weights = transformation_info.get('weights', [1.0])
        source_indices = transformation_info.get('source_indices', [0])
        
        # Only propagate entities from source matrices with significant weight
        threshold = 0.2  # Minimum weight to propagate entities
        
        for src_idx, weight in zip(source_indices, weights):
            if weight >= threshold and src_idx == 0:  # Only process the first source for now
                # Simple propagation based on weight - can be enhanced later
                for coord_key, entity_data in source_entities.items():
                    target_entity_map[coord_key] = entity_data['entity_id']
                    
                    # Parse source coordinates
                    src_coords = coord_key.split(',')
                    src_row_range = [int(x) for x in src_coords[0].split(':')]
                    src_col_range = [int(x) for x in src_coords[1].split(':')]
                    
                    # Register with weight information
                    _register_entity(
                        entity_data['entity_id'],
                        {'transformed_by': transformation_type, 'weight': weight},
                        target_matrix,
                        ((src_row_range[0], src_row_range[1]), (src_col_range[0], src_col_range[1]))
                    )
    
    else:
        # For unknown transformations, use a simple 1:1 mapping if dimensions match
        if source_matrix.shape == target_matrix.shape:
            for coord_key, entity_data in source_entities.items():
                target_entity_map[coord_key] = entity_data['entity_id']
                
                # Parse source coordinates
                src_coords = coord_key.split(',')
                src_row_range = [int(x) for x in src_coords[0].split(':')]
                src_col_range = [int(x) for x in src_coords[1].split(':')]
                
                # Register with transformation type
                _register_entity(
                    entity_data['entity_id'],
                    {'transformed_by': transformation_type},
                    target_matrix,
                    ((src_row_range[0], src_row_range[1]), (src_col_range[0], src_col_range[1]))
                )
    
    return target_entity_map


def load_tensor_from_file(file_path: str, max_retries: int = 3, use_virtual_memory: bool = None) -> np.ndarray:
    """
    Load tensor data from file based on extension with robust error handling.
    Automatically uses QuantumVirtualMemory for large files to optimize memory usage.
    
    Args:
        file_path: Path to the file to load
        max_retries: Maximum number of loading attempts with different approaches
        use_virtual_memory: Override automatic detection to force QVM usage
            - None: Auto-detect based on file size (default)
            - True: Force QVM usage regardless of file size
            - False: Force direct loading regardless of file size
        
    Returns:
        Numpy array containing the loaded data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is empty or invalid
        Exception: For other loading errors
    """
    # Import dependencies at the top of function
    import os
    import time
    import json
    import logging
    import numpy as np
    import pickle
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    # Check if file is empty
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"File is empty: {file_path}")
    
    # Get file size for memory optimization decisions
    file_size = os.path.getsize(file_path)
    # QVM removed: define local flags for compatibility
    should_use_virtual_memory = False
    qvm = None
    
    # Check file size and log if large; QVM removed, we'll load into memory
    if file_size > _QVM_CONFIG.get('large_file_threshold', 100 * 1024 * 1024):
        logging.info(f"Large file detected ({file_size/1024/1024:.2f} MB): {file_path}; loading into memory")
    
    # Log loading attempt
    logging.info(f"Loading tensor data from: {file_path}")
    start_time = time.time()
    
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Auto-detect data type based on extension
        data_type = _detect_data_type(file_path)

        # Fast-path: NumPy binary formats (.npy/.npz)
        if file_ext in ['.npy', '.npz']:
            try:
                if file_ext == '.npy':
                    arr = np.load(file_path, allow_pickle=False)
                else:
                    z = np.load(file_path)
                    # prefer common keys
                    arr = None
                    for key in ('arr_0', 'data', 'array'):
                        if key in z:
                            arr = z[key]
                            break
                    if arr is None:
                        first = next(iter(z.files))
                        arr = z[first]

                # Store metadata for binary numpy loads
                try:
                    _store_general_metadata(file_path, file_path, arr, 'npy', {
                        'file_format': file_ext.lstrip('.'),
                        'dtype': str(arr.dtype),
                        'shape': arr.shape
                    })
                except Exception:
                    logging.debug('Failed to register metadata for numpy binary')

                return arr
            except Exception as e:
                logging.warning(f"Failed to load numpy binary {file_path}: {e}")
        
        # Helper function placeholder: QVM removed, use direct memory operations
        def load_with_qvm(data_array, qvm_name_prefix, init_pattern="zeros"):
            """Compatibility wrapper that returns the input array unchanged."""
            return data_array
            
            # Retrieve data from QVM in chunks (some QVM backends enforce a per-call chunk limit)
            total = int(data_array.size)
            chunk = int(_QVM_CONFIG.get('chunk_size', 1_000_000))
            try:
                if total <= chunk:
                    flat = qvm.get(qvm_name, end_idx=total)
                    flat = np.asarray(flat)
                else:
                    parts = []
                    for s in range(0, total, chunk):
                        e = min(s + chunk, total)
                        part = qvm.get(qvm_name, start_idx=s, end_idx=e)
                        parts.append(np.asarray(part))
                    flat = np.concatenate(parts, axis=0) if parts else np.array([], dtype=flattened_data.dtype)

                # Validate size before reshape
                if flat.size != total:
                    logging.warning(f"QVM returned {flat.size} elements but expected {total}; falling back to direct memory for {file_path}")
                    return data_array

                result = flat.reshape(data_array.shape)
                return result
            except Exception as e:
                logging.warning(f"QVM retrieval failed: {e}; falling back to direct memory for {file_path}")
                return data_array
        
        # Allow automatic handling based on detected data type
        if data_type == 'image' and file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']:
            # Load the image and extract OCR data if enabled
            extract_ocr = _OCR_CONFIG.get('extract_ocr_on_load', False)
            
            if extract_ocr:
                # Load with OCR extraction
                image_result = _load_image_file(file_path, extract_ocr=True)
                
                if isinstance(image_result, tuple) and len(image_result) == 2:
                    # Unpack image array and OCR metadata
                    image_array, ocr_metadata = image_result
                else:
                    # Fallback if OCR extraction failed
                    image_array = image_result
                    ocr_metadata = {
                        'ocr_index': {},
                        'raw_text': '',
                        'text_count': 0,
                        'has_text': False,
                        'language': 'en',
                        'ocr_df': []
                    }
            else:
                # Standard image loading without OCR
                image_array = _load_image_file(file_path, extract_ocr=False)
                ocr_metadata = None
        elif data_type == 'video' and file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']:
            # Load the video and extract OCR data if enabled
            extract_ocr = _OCR_CONFIG.get('extract_ocr_on_load', False) and _OCR_CONFIG.get('video_processing_enabled', False)
            
            if extract_ocr:
                # Load with OCR extraction
                video_result = _load_video_file(file_path, extract_ocr=True)
                
                if isinstance(video_result, tuple) and len(video_result) == 2:
                    # Unpack video frame array and OCR metadata
                    image_array, ocr_metadata = video_result
                else:
                    # Fallback if OCR extraction failed
                    image_array = video_result
                    ocr_metadata = {
                        'ocr_index': {},
                        'raw_text': '',
                        'text_count': 0,
                        'has_text': False,
                        'language': 'en',
                        'ocr_df': [],
                        'video_properties': {'processed_frames': 0}
                    }
            else:
                # Standard video loading without OCR (returns a keyframe)
                image_array = _load_video_file(file_path, extract_ocr=False)
                ocr_metadata = None
            
            # Use QVM for large images if configured
            result_array = image_array
            if should_use_virtual_memory and qvm and image_array.size > 1000000:  # Only for larger images (1M+ pixels)
                try:
                    result_array = load_with_qvm(image_array, f"img_{file_ext[1:]}")
                except Exception as e:
                    # Fallback to regular memory if QVM fails
                    logging.warning(f"Failed to use QVM for image data: {e}. Falling back to direct memory.")
                    result_array = image_array
            
            # Prepare metadata for storage
            image_metadata = {
                'file_format': 'image',
                'image_format': file_ext[1:],  # Remove the dot
                'image_shape': result_array.shape,
                'uses_qvm': should_use_virtual_memory and qvm is not None
            }
            
            # Add OCR metadata if available
            if ocr_metadata:
                image_metadata.update({
                    'ocr_processed': True,
                    'has_text': ocr_metadata.get('has_text', False),
                    'text_count': ocr_metadata.get('text_count', 0),
                    'ocr_raw_text': ocr_metadata.get('raw_text', ''),
                    'ocr_language': ocr_metadata.get('language', 'en')
                })
                
                # Store OCR index in global registry for searching
                global _OCR_INDEX_REGISTRY
                if not hasattr(sys.modules[__name__], '_OCR_INDEX_REGISTRY'):
                    _OCR_INDEX_REGISTRY = {}
                    
                array_id = id(result_array)
                if 'ocr_index' in ocr_metadata:
                    _OCR_INDEX_REGISTRY[array_id] = ocr_metadata['ocr_index']
                    image_metadata['ocr_indexed'] = True
                
                # Store raw OCR data records
                if 'ocr_df' in ocr_metadata:
                    global _OCR_DATA_REGISTRY
                    if not hasattr(sys.modules[__name__], '_OCR_DATA_REGISTRY'):
                        _OCR_DATA_REGISTRY = {}
                    _OCR_DATA_REGISTRY[array_id] = ocr_metadata['ocr_df']
                    image_metadata['ocr_data_stored'] = True
            
            # Store image metadata
            _store_general_metadata(file_path, file_path, result_array, 'image', image_metadata)
            
            return result_array
        
        if data_type == 'text' and file_ext in ['.txt', '.md', '.html', '.xml']:
            # Load text and store metadata
            result_array = _load_text_file(file_path)
            
            # Read original text for metadata storage
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    original_text = f.read()
            except Exception:
                try:
                    with open(file_path, 'r', encoding='latin1') as f:
                        original_text = f.read()
                except Exception:
                    original_text = "Could not read original text"
            
            _store_general_metadata(file_path, original_text, result_array, 'text', {
                'file_format': 'text',
                'text_encoding': 'utf-8',
                'file_extension': file_ext
            })
            
            return result_array
        
        # Handle JSON files
        if file_ext == '.json':
            logging.debug(f"Loading JSON data from {file_path}")
            try:
                # Quick pre-check: if this JSON is already in our tensor format
                # (either a dict with 'shape' and 'data' or a top-level nested list),
                # load it directly and return the N-D array -- this preserves
                # exact dimensionality for formats like sample_6d_tensor.json.
                try:
                    with open(file_path, 'r', encoding='utf-8') as jf:
                        raw_json = json.load(jf)
                    # Direct tensor format: {'shape': [...], 'data': [...]}
                    if isinstance(raw_json, dict) and 'data' in raw_json and 'shape' in raw_json:
                        try:
                            arr = np.array(raw_json['data'])
                            if 'dtype' in raw_json:
                                arr = arr.astype(raw_json['dtype'])
                            _store_general_metadata(file_path, raw_json, arr, 'json_tensor', {
                                'file_format': 'json',
                                'json_tensor': True,
                                'provided_shape': raw_json.get('shape'),
                                'provided_dtype': raw_json.get('dtype')
                            })
                            return arr
                        except Exception:
                            logging.debug('Failed to convert direct tensor JSON to array; will try enhanced handling')
                    # Plain nested list -> treat as tensor directly
                    if isinstance(raw_json, list):
                        try:
                            arr = np.array(raw_json)
                            _store_general_metadata(file_path, raw_json, arr, 'json_array', {
                                'file_format': 'json',
                                'json_array': True,
                                'inferred_shape': arr.shape
                            })
                            return arr
                        except Exception:
                            logging.debug('Failed to convert JSON list to array; will try enhanced handling')
                except Exception:
                    # If quick parsing fails, fall back to enhanced handling below
                    pass

                # Use enhanced JSON handling
                try:
                    from json_handler import load_json_file, convert_json_to_tensor

                    # Load with enhanced path-based parsing
                    data, json_metadata = load_json_file(file_path)
                    
                    # CRITICAL: Save a direct copy of the JSON data for connection discovery
                    global _GENERAL_METADATA
                    temp_data_key = f"temp_json_data_{hash(file_path)}"
                    _GENERAL_METADATA[temp_data_key] = data
                    
                    # Convert to tensor with structure preservation
                    result_array, structure_metadata = convert_json_to_tensor(data)
                    
                    # Combine metadata
                    json_summary = {
                        "enhanced_parsing": True,
                        "structure_preserved": True
                    }
                    json_summary.update(structure_metadata)
                    
                    # Store the comprehensive metadata - ensure data is passed as original_data
                    array_id = id(result_array)
                    logging.debug(f"Storing original JSON data in metadata, type: {type(data).__name__}, array_id: {array_id}")
                    
                    # Store the reference instead of the full data which might be getting lost
                    _store_general_metadata(file_path, _GENERAL_METADATA[temp_data_key], result_array, 'json', {
                        'file_format': 'json',
                        'json_type': type(data).__name__,
                        'encoding': json_metadata.get('encoding', 'utf-8'),
                        'json_summary': json_summary,
                        'hierarchical_metadata': structure_metadata,
                        'contains_original_data': True,  # Flag to verify data is stored
                        'json_data_preserved': True      # Additional verification
                    })
                    return result_array
                    
                except (ImportError, Exception) as e:
                    # Fallback to original method if enhanced handling fails
                    logging.warning(f"Enhanced JSON handling failed, falling back to basic: {str(e)}")
                    
                    # Try multiple approaches for robust JSON loading
                    data = None
                    encodings_to_try = ['utf-8', 'utf-16', 'latin1', 'cp1252']
                    
                    for encoding in encodings_to_try:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read()
                                
                            # Try different JSON parsing strategies
                            try:
                                # Strategy 1: Direct parsing
                                data = json.loads(content)
                                logging.debug(f"Successfully loaded JSON with encoding {encoding}")
                                break
                            except json.JSONDecodeError as json_err:
                                # Strategy 2: Try to fix common JSON issues
                                logging.debug(f"JSON decode error with {encoding}: {str(json_err)}")
                                
                                # Try to truncate at the error position if it's near the end
                                error_pos = getattr(json_err, 'pos', None)
                                if error_pos and error_pos > len(content) * 0.9:  # Error near end
                                    logging.warning(f"JSON error near end of file at position {error_pos}, attempting truncation")
                                    try:
                                        # Find the last complete JSON object/array
                                        truncated_content = content[:error_pos].rstrip()
                                        # Try to fix incomplete arrays/objects
                                        if truncated_content.endswith(','):
                                            truncated_content = truncated_content[:-1]
                                        if truncated_content.count('[') > truncated_content.count(']'):
                                            truncated_content += ']'
                                        elif truncated_content.count('{') > truncated_content.count('}'):
                                            truncated_content += '}'
                                        
                                        data = json.loads(truncated_content)
                                        logging.warning(f"Successfully parsed truncated JSON (removed {len(content) - len(truncated_content)} chars)")
                                        break
                                    except json.JSONDecodeError:
                                        logging.debug("Truncation strategy failed")
                                        pass
                                
                                # Strategy 3: Try line-by-line parsing for JSONL format
                                if not data:
                                    try:
                                        lines = content.strip().split('\n')
                                        if len(lines) > 1:
                                            json_objects = []
                                            successful_lines = 0
                                            for i, line in enumerate(lines):
                                                line = line.strip()
                                                if line:
                                                    try:
                                                        obj = json.loads(line)
                                                        json_objects.append(obj)
                                                        successful_lines += 1
                                                    except json.JSONDecodeError:
                                                        if i < 10:  # Only log first few errors
                                                            logging.debug(f"Skipping malformed line {i+1}: {line[:100]}...")
                                                        if i > len(lines) * 0.9:  # Stop if too many errors near end
                                                            break
                                            
                                            if json_objects:
                                                data = json_objects
                                                logging.warning(f"Parsed as JSONL format: {successful_lines} valid objects from {len(lines)} lines")
                                                break
                                    except Exception:
                                        logging.debug("JSONL parsing strategy failed")
                                        pass
                        
                        except Exception as enc_err:
                            logging.debug(f"Failed to read file with encoding {encoding}: {str(enc_err)}")
                            continue
                    
                    if data is None:
                        raise ValueError(f"Could not parse JSON file {file_path} with any encoding or strategy")

                    # If the JSON file already encodes a tensor as a dict with
                    # 'shape' and 'data' keys (our sample format), load the data
                    # directly as a numpy array and preserve its shape/dtype.
                    if isinstance(data, dict) and 'data' in data and 'shape' in data:
                        try:
                            result_array = np.array(data['data'])
                            # Store rich metadata referencing the original JSON
                            _store_general_metadata(file_path, data, result_array, 'json_tensor', {
                                'file_format': 'json',
                                'json_tensor': True,
                                'provided_shape': data.get('shape'),
                                'provided_dtype': data.get('dtype')
                            })
                            return result_array
                        except Exception:
                            # If direct conversion fails, fall back to the generic path below
                            logging.debug('Direct tensor-like JSON conversion failed; falling back to generic JSON handling')

                    # Store a summary of the JSON instead of the full object
                    if isinstance(data, dict):
                        json_summary = {
                            "type": "dict",
                            "keys": list(data.keys()),  # Store all keys - no limits
                            "total_keys": len(data)
                        }
                    elif isinstance(data, list):
                        json_summary = {
                            "type": "list",
                            "length": len(data),
                            "sample": str(data[:5]) if data else ""  # Store complete sample - no char limits
                        }
                    else:
                        json_summary = {
                            "type": str(type(data).__name__)
                        }
                    
                # Convert to numpy array safely with better handling for complex JSON
                try:
                    # First try direct conversion
                    temp_array = np.array(data)
                    
                    # Check if it's a valid numeric array
                    if temp_array.dtype == 'object' or temp_array.dtype.kind in ['U', 'S']:
                        # Contains mixed types or strings, convert to numeric representation
                        raise ValueError("Mixed data types detected, converting to numeric")
                    
                    # Check if the array can handle mathematical operations
                    try:
                        # Test with a small operation
                        _ = np.isfinite(temp_array.flat[:min(10, temp_array.size)])
                        result_array = temp_array
                    except (TypeError, ValueError):
                        # Can't handle mathematical operations, convert to character representation
                        raise ValueError("Array doesn't support mathematical operations")
                        
                except (ValueError, TypeError):
                    # Handle complex nested structures by creating a numeric representation
                    json_str = json.dumps(data, default=str)  # Convert any non-serializable objects to strings
                    
                    # Create a numeric representation based on character codes
                    char_codes = [ord(c) for c in json_str[:10000]]  # Limit to 10k characters
                    
                    # Ensure we have a meaningful array size
                    if len(char_codes) == 0:
                        char_codes = [0]  # Fallback for empty JSON
                    
                    # Create a proper numeric array
                    result_array = np.array(char_codes, dtype=np.float32)
                    
                    # Reshape to a more meaningful 2D array if possible
                    if len(char_codes) > 1:
                        # Try to create a roughly square matrix
                        size = len(char_codes)
                        sqrt_size = int(np.sqrt(size))
                        if sqrt_size > 1:
                            # Pad to make it rectangular
                            target_size = sqrt_size * sqrt_size
                            if size < target_size:
                                char_codes.extend([0] * (target_size - size))
                            result_array = np.array(char_codes[:target_size], dtype=np.float32).reshape(sqrt_size, sqrt_size)
                        else:
                            result_array = np.array(char_codes, dtype=np.float32).reshape(-1, 1)
                
                _store_general_metadata(file_path, data, result_array, 'json', {
                    'file_format': 'json',
                    'json_type': type(data).__name__,
                    'encoding': 'utf-8',
                    'json_summary': json_summary  # Keep the summary as additional info
                })
                
                return result_array
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin1') as f:
                    data = json.load(f)

                # Same direct-tensor detection for latin1-decoded JSON
                if isinstance(data, dict) and 'data' in data and 'shape' in data:
                    try:
                        result_array = np.array(data['data'])
                        _store_general_metadata(file_path, data, result_array, 'json_tensor', {
                            'file_format': 'json',
                            'json_tensor': True,
                            'provided_shape': data.get('shape'),
                            'provided_dtype': data.get('dtype')
                        })
                        return result_array
                    except Exception:
                        logging.debug('Direct tensor-like JSON (latin1) conversion failed; continuing generic handling')
                
                # Store a summary of the JSON instead of the full object
                if isinstance(data, dict):
                    json_summary = {
                        "type": "dict",
                        "keys": list(data.keys()),  # Store all keys - no limits
                        "total_keys": len(data)
                    }
                elif isinstance(data, list):
                    json_summary = {
                        "type": "list",
                        "length": len(data),
                        "sample": str(data[:5]) if data else ""  # Store complete sample - no char limits
                    }
                else:
                    json_summary = {
                        "type": str(type(data).__name__)
                    }
                
                # Convert to numpy array safely with better handling for complex JSON
                try:
                    # First try direct conversion
                    temp_array = np.array(data)
                    
                    # Check if it's a valid numeric array
                    if temp_array.dtype == 'object' or temp_array.dtype.kind in ['U', 'S']:
                        # Contains mixed types or strings, convert to numeric representation
                        raise ValueError("Mixed data types detected, converting to numeric")
                    
                    # Check if the array can handle mathematical operations
                    try:
                        # Test with a small operation
                        _ = np.isfinite(temp_array.flat[:min(10, temp_array.size)])
                        result_array = temp_array
                    except (TypeError, ValueError):
                        # Can't handle mathematical operations, convert to character representation
                        raise ValueError("Array doesn't support mathematical operations")
                        
                except (ValueError, TypeError):
                    # Handle complex nested structures by creating a numeric representation
                    json_str = json.dumps(data, default=str)  # Convert any non-serializable objects to strings
                    
                    # Create a numeric representation based on character codes
                    char_codes = [ord(c) for c in json_str[:10000]]  # Limit to 10k characters
                    
                    # Ensure we have a meaningful array size
                    if len(char_codes) == 0:
                        char_codes = [0]  # Fallback for empty JSON
                    
                    # Create a proper numeric array
                    result_array = np.array(char_codes, dtype=np.float32)
                    
                    # Reshape to a more meaningful 2D array if possible
                    if len(char_codes) > 1:
                        # Try to create a roughly square matrix
                        size = len(char_codes)
                        sqrt_size = int(np.sqrt(size))
                        if sqrt_size > 1:
                            # Pad to make it rectangular
                            target_size = sqrt_size * sqrt_size
                            if size < target_size:
                                char_codes.extend([0] * (target_size - size))
                            result_array = np.array(char_codes[:target_size], dtype=np.float32).reshape(sqrt_size, sqrt_size)
                        else:
                            result_array = np.array(char_codes, dtype=np.float32).reshape(-1, 1)
                
                _store_general_metadata(file_path, data, result_array, 'json', {
                    'file_format': 'json',
                    'json_type': type(data).__name__,
                    'encoding': 'latin1',
                    'json_summary': json_summary
                })
                
                return result_array

        elif file_ext in ['.xlsx', '.xls']:
            logging.debug(f"Loading Excel data from {file_path}")
            try:
                import pandas as pd
                # Read the first sheet by default
                df = pd.read_excel(file_path)
                original_df = df.copy()  # Keep a copy of original data for entity extraction
                
                # Store the original DataFrame in a special key for easier retrieval
                excel_data_key = f"excel_data_{hash(file_path)}"
                _GENERAL_METADATA[excel_data_key] = original_df
                
                # Store original DataFrame before conversion
                _store_general_metadata(file_path, df, df.values, 'excel', {
                    'file_format': 'excel',
                    'sheet_name': 'default',
                    'excel_data_key': excel_data_key  # Reference to where we stored the full dataframe
                })
                
                # Convert columns to numeric where possible
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Fill NaN values with 0
                df = df.fillna(0)
                
                # Select only numeric columns for matrix operations
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) == 0:
                    logging.warning(f"No numeric data found in {file_path}")
                    result_array = np.arange(len(df)).reshape(-1, 1)
                else:
                    result_array = df[numeric_cols].values
                
                # Update metadata with the final processed array
                _store_general_metadata(file_path, original_df, result_array, 'excel', {
                    'file_format': 'excel',
                    'sheet_name': 'default',
                    'columns': df.columns.tolist(),
                    'dataframe': original_df,  # Store the original dataframe in metadata
                    'excel_data_key': excel_data_key  # Reference to original data
                })
                
                return result_array
            except ImportError:
                raise ImportError("pandas and openpyxl are required to load Excel files")
        elif file_ext in ['.csv', '.tsv']:
            delimiter = ',' if file_ext == '.csv' else '\t'
            logging.debug(f"Loading tabular data from {file_path}")
            
            # Try using pandas for robust tabular data loading
            try:
                import pandas as pd
                import numpy as np  # Ensure numpy is available in this scope
                
                try:
                    # Try standard loading first. Use header=None to avoid treating
                    # the first data row as a header (numpy.savetxt writes no header).
                    df = pd.read_csv(file_path, delimiter=delimiter, header=None)
                except (UnicodeDecodeError, pd.errors.ParserError) as e:
                    # Handle both encoding and parsing errors
                    logging.warning(f"Standard CSV parsing failed: {e}. Trying with error handling...")
                    
                    # Try different encodings with error handling
                    encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
                    for encoding in encodings:
                        try:
                            # Try with error handling for malformed lines
                            try:
                                # For newer pandas versions - skip bad lines. Use header=None
                                df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding,
                                               on_bad_lines='skip', engine='python', header=None)
                                break
                            except TypeError:
                                # For older pandas versions - use header=None
                                df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding,
                                               error_bad_lines=False, warn_bad_lines=True, header=None)
                                break
                        except Exception as e:
                            if encoding == encodings[-1]:  # Last encoding attempt
                                logging.warning(f"All CSV parsing attempts failed: {e}")
                                # Final fallback: read as text and create basic structure
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                                        lines = f.readlines()
                                    if lines:
                                        # Create a simple DataFrame with line numbers
                                        df = pd.DataFrame({'line_content': [line.strip() for line in lines]})
                                    else:
                                        df = pd.DataFrame({'empty': [0]})
                                except Exception:
                                    # Absolute fallback
                                    df = pd.DataFrame({'error': [1]})
                
                # Store the original DataFrame BEFORE conversion to preserve text content
                original_df = df.copy()
                
                # Convert columns to numeric where possible for numerical operations
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Fill NaN values with 0
                df = df.fillna(0)
                
                # Select numeric columns for matrix operations
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) == 0:
                    logging.warning(f"No numeric data found in {file_path}")
                    # Create a simple index-based numeric representation
                    result_array = np.arange(len(df)).reshape(-1, 1)
                else:
                    numpy_array = df[numeric_cols].values
                    
                            # Load directly into memory
                    result_array = numpy_array
                
                # Store ORIGINAL dataframe (with text content) in registry
                _store_general_metadata(file_path, original_df, result_array, 'tabular', {
                    'file_format': 'csv' if file_ext == '.csv' else 'tsv',
                    'delimiter': delimiter,
                    'uses_qvm': False
                })
                
                return result_array
            
            except ImportError:
                logging.warning("Pandas not available, falling back to NumPy")
                try:
                    # Try with NumPy's genfromtxt
                    return np.genfromtxt(file_path, delimiter=delimiter, filling_values=0)
                except Exception as e:
                    # Last resort: binary read with error handling
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                    text_data = raw_data.decode('utf-8', errors='replace')
                    from io import StringIO
                    return np.genfromtxt(StringIO(text_data), delimiter=delimiter, 
                                        filling_values=0, invalid_raise=False)

        else:
            # Unknown file type - try to guess format
            # If the extension is a common image type, prefer a quiet debug message and treat it as image
            image_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.gif']
            if file_ext in image_exts:
                logging.debug(f"File extension {file_ext} appears to be an image; attempting image load without noisy warning.")
            else:
                logging.warning(f"Unknown file extension: {file_ext}. Attempting to guess format.")
            
            # Try to detect file type
            data_type = _detect_data_type(file_path)
            logging.info(f"Detected data type: {data_type}")
            
            if data_type == 'image':
                result_array = _load_image_file(file_path)
                _store_general_metadata(file_path, file_path, result_array, 'image_unknown', {
                    'file_format': 'image_unknown',
                    'detected_as': 'image',
                    'original_extension': file_ext
                })
                return result_array
            elif data_type == 'video':
                result_array = _load_video_file(file_path)
                _store_general_metadata(file_path, file_path, result_array, 'video_unknown', {
                    'file_format': 'video_unknown',
                    'detected_as': 'video',
                    'original_extension': file_ext
                })
                return result_array
            elif data_type == 'text':
                result_array = _load_text_file(file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        original_text = f.read()
                except Exception:
                    original_text = "Could not read original text"
                
                _store_general_metadata(file_path, original_text, result_array, 'text_unknown', {
                    'file_format': 'text_unknown',
                    'detected_as': 'text',
                    'original_extension': file_ext
                })
                return result_array
            elif data_type == 'json':
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        data = json.load(f)
                    result_array = np.array(data)
                    _store_general_metadata(file_path, data, result_array, 'json_unknown', {
                        'file_format': 'json_unknown',
                        'detected_as': 'json',
                        'original_extension': file_ext
                    })
                    return result_array
                except Exception:
                    pass
            elif data_type == 'tabular':
                # Try as CSV first, then TSV
                for delimiter in [',', '\t']:
                    try:
                        import pandas as pd
                        df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8', errors='replace', header=None)
                        original_df = df.copy()
                        
                        # Convert to numeric where possible
                        for col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        df = df.fillna(0)
                        result_array = df.select_dtypes(include=[np.number]).values
                        
                        _store_general_metadata(file_path, original_df, result_array, 'tabular_unknown', {
                            'file_format': 'tabular_unknown',
                            'detected_as': 'tabular',
                            'delimiter': delimiter,
                            'original_extension': file_ext
                        })
                        return result_array
                    except Exception:
                        pass
            
            # If we get here, we couldn't handle the file type
            raise ValueError(f"Could not determine how to load file: {file_path}")
                
    finally:
        end_time = time.time()
        loading_time = end_time - start_time
    logging.debug(f"Tensor loading completed in {loading_time:.4f} seconds using direct memory")





def _detect_data_type(file_path: str) -> str:
    """
    Automatically detect the data type based on file extension and content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        A string indicating the detected data type:
        - 'tabular': CSV, TSV data
        - 'excel': Excel files
        - 'image': Image files
        - 'video': Video files
        - 'text': Text files
        - 'json': JSON data
        - 'unknown': Could not determine
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Quick check based on extension for common file types
    if file_ext in ['.csv', '.tsv']:
        return 'tabular'
    elif file_ext in ['.xlsx', '.xls']:
        return 'excel'
    elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']:
        return 'image'
    elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']:
        return 'video'
    elif file_ext in ['.txt', '.md', '.html', '.xml']:
        return 'text'
    elif file_ext in ['.json']:
        return 'json'
    
    # For ambiguous extensions, examine file content
    try:
        # Open in binary mode to check for magic bytes
        with open(file_path, 'rb') as f:
            header = f.read(64)  # Read more bytes for better detection
            
            # Image format detection
            if header.startswith(b'\x89PNG'):  # PNG
                return 'image'
            elif header.startswith(b'\xff\xd8\xff'):  # JPEG
                return 'image'
            elif header.startswith(b'GIF8'):  # GIF
                return 'image'
            elif header.startswith(b'BM'):  # BMP
                return 'image'
            elif header.startswith(b'II*\x00') or header.startswith(b'MM\x00*'):  # TIFF
                return 'image'
            
            # Document format detection
            elif header.startswith(b'%PDF'):  # PDF
                return 'binary'
            elif header.startswith(b'PK\x03\x04'):  # ZIP-based formats (Office docs)
                return 'binary'
            elif header[:8] in [b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1',  # OLE Compound Document (older Office)
                               b'\x50\x4b\x03\x04\x14\x00\x06\x00']:  # DOCX/XLSX/etc
                return 'binary'
                
            # Database formats
            elif header.startswith(b'SQLite format'):  # SQLite
                return 'binary'
            
            # Enhanced JSON detection
            json_start_patterns = [b'{', b'[', b' {', b' [', b'\n{', b'\n[', b'\r\n{', b'\r\n[']
            json_content = False
            
            # Check if content looks like JSON with a more robust approach
            for pattern in json_start_patterns:
                if header.lstrip().startswith(pattern):
                    json_content = True
                    break
                    
            if json_content:
                try:
                    # Attempt to read a small portion to validate JSON structure
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as text_f:
                        # Read first 1000 characters for pattern checking
                        sample = text_f.read(1000)
                        
                        # Check for JSON structural patterns
                        brace_count = sample.count('{') - sample.count('}')
                        bracket_count = sample.count('[') - sample.count(']')
                        has_colons = ':' in sample
                        has_quotes = '"' in sample or "'" in sample
                        
                        # Weighted scoring for JSON likelihood
                        json_score = 0
                        if sample.lstrip().startswith('{') or sample.lstrip().startswith('['): 
                            json_score += 5
                        if has_colons: 
                            json_score += 3
                        if has_quotes: 
                            json_score += 2
                        if brace_count > 0 or bracket_count > 0: 
                            json_score += 1
                            
                        # Determine if this is likely JSON
                        if json_score >= 6:
                            try:
                                # Try to import enhanced JSON handling for better detection
                                from json_handler import load_json_file
                                # Just check if it's valid without loading fully
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    # Read just enough to check if it's valid JSON
                                    test_content = f.read(10000)  # 10KB test sample
                                    try:
                                        json.loads(test_content[:test_content.rfind('}')+1] if '}' in test_content else test_content)
                                        return 'json'
                                    except:
                                        # More aggressive check for JSONL
                                        lines = test_content.split('\n')
                                        if any(line.strip().startswith('{') for line in lines[:10]):
                                            return 'json'
                            except ImportError:
                                # Fall back to simple check if enhanced handling isn't available
                                if sample.lstrip().startswith('{') or sample.lstrip().startswith('['):
                                    return 'json'
                except Exception:
                    # If JSON detection fails, try a simpler approach
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as text_f:
                            first_char = text_f.read(1).strip()
                            if first_char in ['{', '[']:
                                return 'json'
                    except:
                        pass
            
            # Check if it might be a CSV/TSV
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as text_f:
                    first_line = text_f.readline()
                    if ',' in first_line and len(first_line.split(',')) > 1:
                        return 'tabular'
                    if '\t' in first_line and len(first_line.split('\t')) > 1:
                        return 'tabular'
            except:
                pass
                
            # Check if it looks like a text file (high ratio of printable ASCII chars)
            try:
                with open(file_path, 'rb') as f:
                    sample = f.read(4096)  # Read a larger sample
                    if sample:
                        printable = 0
                        for byte in sample:
                            if 32 <= byte <= 126 or byte in (9, 10, 13):  # ASCII printable + whitespace
                                printable += 1
                        if printable / len(sample) > 0.8:  # If >80% is printable, probably text
                            return 'text'
                        else:
                            return 'binary'  # Otherwise, assume binary
            except:
                pass
                
    except Exception as e:
        logging.debug(f"Error detecting file type: {e}")
    
    # Use file extension as a fallback for ambiguous files
    if file_ext and len(file_ext) > 1:
        # Map file extension to data type if we have no other information
        ext_map = {
            # Source code files
            '.py': 'text', '.js': 'text', '.java': 'text', '.c': 'text', '.cpp': 'text', '.h': 'text',
            '.rb': 'text', '.go': 'text', '.rs': 'text', '.php': 'text', '.ts': 'text',
            # Data files
            '.csv': 'tabular', '.tsv': 'tabular', '.json': 'json', '.xml': 'text',
            # Binary formats
        '.bin': 'binary', '.dAqat': 'binary', '.exe': 'binary', '.dll': 'binary',
            '.pdf': 'binary', '.docx': 'binary', '.xlsx': 'binary',
            # Images
            '.jpg': 'image', '.png': 'image', '.gif': 'image', '.svg': 'text',
        }
        if file_ext in ext_map:
            return ext_map[file_ext]
    
    # Fallback
    return 'unknown'

def _load_image_file(file_path: str, extract_ocr: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, Dict]]:
    """
    Load an image file into a numpy array.
    
    Args:
        file_path: Path to the image file
        extract_ocr: Whether to extract text using OCR
        
    Returns:
        If extract_ocr is False: NumPy array representation of the image
        If extract_ocr is True: Tuple of (NumPy array, OCR metadata dict)
    """
    logging.debug(f"Loading image from {file_path}")
    try:
        # Try PIL first, most commonly available
        try:
            from PIL import Image
            img = Image.open(file_path)
            # Convert to RGB to ensure consistent 3-channel arrays for downstream processing
            try:
                img = img.convert('RGB')
            except Exception:
                pass
            img_array = np.array(img)
        except ImportError:
            logging.warning("PIL not available, trying OpenCV")
            
            # Try OpenCV
            try:
                import cv2
                img_array = cv2.imread(file_path)
                if img_array is None:
                    raise ValueError(f"Failed to load image with OpenCV: {file_path}")
                # Convert BGR to RGB
                if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
            except ImportError:
                logging.error("Neither PIL nor OpenCV available for image loading")
                raise ImportError("Image loading requires either PIL or OpenCV")
        
        # Extract OCR data if requested
        if extract_ocr:
            try:
                from .ocr_integration import extract_text_from_image, create_ocr_index
                
                # Extract text from image
                raw_results, ocr_df = extract_text_from_image(img_array)
                
                # Create searchable index
                if not ocr_df.empty:
                    ocr_metadata = {
                        'ocr_index': create_ocr_index(ocr_df),
                        'raw_text': ' '.join(row['text'] for _, row in ocr_df.iterrows()),
                        'text_count': len(ocr_df),
                        'has_text': len(ocr_df) > 0,
                        'language': 'en',  # Default, can be expanded later
                        'ocr_df': ocr_df.to_dict('records')  # Store for later use
                    }
                else:
                    ocr_metadata = {
                        'ocr_index': {},
                        'raw_text': '',
                        'text_count': 0,
                        'has_text': False,
                        'language': 'en',
                        'ocr_df': []
                    }
                    
                return img_array, ocr_metadata
            except ImportError:
                logging.warning("OCR integration not available, skipping text extraction")
                return img_array
            except Exception as e:
                logging.error(f"Error in OCR processing: {e}")
                return img_array
                
        return img_array
    except Exception as e:
        logging.error(f"Error loading image {file_path}: {str(e)}")
        raise

def _load_video_file(file_path: str, extract_ocr: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, Dict]]:
    """
    Load a video file and process its frames.
    
    Args:
        file_path: Path to the video file
        extract_ocr: Whether to extract text using OCR
        
    Returns:
        If extract_ocr is False: A keyframe from the video as NumPy array
        If extract_ocr is True: Tuple of (keyframe array, OCR metadata dict)
    """
    logging.debug(f"Loading video from {file_path}")
    try:
        # Check if OpenCV is available
        try:
            import cv2
        except ImportError:
            logging.error("OpenCV (cv2) is required for video processing")
            raise ImportError("Video processing requires OpenCV (cv2)")
        
        # Get a representative frame as thumbnail
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            logging.error(f"Could not open video file: {file_path}")
            raise ValueError(f"Failed to open video: {file_path}")
            
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        
        # Get a representative frame (around 20% into the video)
        target_frame = min(int(total_frames * 0.2), total_frames - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        
        if not ret:
            logging.warning(f"Failed to read frame from video {file_path}, trying first frame")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                raise ValueError(f"Failed to read any frames from video: {file_path}")
                
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Extract OCR data if requested
        if extract_ocr:
            try:
                from .ocr_integration import process_video_frames, create_ocr_index
                
                # Process video frames if video processing is enabled
                if _OCR_CONFIG.get('video_processing_enabled', False):
                    # This will extract text from multiple frames
                    ocr_df = process_video_frames(file_path)
                    
                    # Create searchable index
                    if not ocr_df.empty:
                        ocr_metadata = {
                            'ocr_index': create_ocr_index(ocr_df),
                            'raw_text': ' '.join(row['text'] for _, row in ocr_df.iterrows()),
                            'text_count': len(ocr_df),
                            'has_text': len(ocr_df) > 0,
                            'language': 'en',  # Default, can be expanded later
                            'ocr_df': ocr_df.to_dict('records'),  # Store for later use
                            'video_properties': {
                                'fps': fps,
                                'total_frames': total_frames,
                                'width': width,
                                'height': height,
                                'duration_seconds': duration,
                                'processed_frames': len(ocr_df['frame_number'].unique()) if not ocr_df.empty else 0
                            }
                        }
                    else:
                        ocr_metadata = {
                            'ocr_index': {},
                            'raw_text': '',
                            'text_count': 0,
                            'has_text': False,
                            'language': 'en',
                            'ocr_df': [],
                            'video_properties': {
                                'fps': fps,
                                'total_frames': total_frames,
                                'width': width,
                                'height': height,
                                'duration_seconds': duration,
                                'processed_frames': 0
                            }
                        }
                        
                    return frame_rgb, ocr_metadata
                else:
                    # If video processing is disabled, just extract text from the keyframe
                    from .ocr_integration import extract_text_from_image, create_ocr_index
                    raw_results, ocr_df = extract_text_from_image(frame_rgb)
                    
                    # Create searchable index
                    if not ocr_df.empty:
                        ocr_metadata = {
                            'ocr_index': create_ocr_index(ocr_df),
                            'raw_text': ' '.join(row['text'] for _, row in ocr_df.iterrows()),
                            'text_count': len(ocr_df),
                            'has_text': len(ocr_df) > 0,
                            'language': 'en',
                            'ocr_df': ocr_df.to_dict('records'),
                            'video_properties': {
                                'fps': fps,
                                'total_frames': total_frames,
                                'width': width,
                                'height': height,
                                'duration_seconds': duration,
                                'processed_frames': 1  # Only the keyframe
                            }
                        }
                    else:
                        ocr_metadata = {
                            'ocr_index': {},
                            'raw_text': '',
                            'text_count': 0,
                            'has_text': False,
                            'language': 'en',
                            'ocr_df': [],
                            'video_properties': {
                                'fps': fps,
                                'total_frames': total_frames,
                                'width': width,
                                'height': height,
                                'duration_seconds': duration,
                                'processed_frames': 0
                            }
                        }
                    
                    return frame_rgb, ocr_metadata
            except ImportError:
                logging.warning("OCR integration not available, skipping text extraction")
                return frame_rgb
            except Exception as e:
                logging.error(f"Error in video OCR processing: {e}")
                return frame_rgb
                
        # Return representative frame if not extracting OCR
        cap.release()
        return frame_rgb
    except Exception as e:
        logging.error(f"Error processing video {file_path}: {str(e)}")
        raise

def _load_text_file(file_path: str) -> np.ndarray:
        """Load text file and produce a richer numeric representation.

        Backward compatible: first column replicates the original simple
        normalized character-level encoding (so existing downstream code
        expecting a column vector will still work by selecting [:,0]).

        Added semantic features per character position:
        - Column 0: normalized character index (original behavior)
        - Column 1: normalized frequency of the word containing the character
        - Columns 2..(2+EMB_DIM-1): deterministic hashed word embedding
        - Optional TF-IDF global relevance score (final column) if feasible

        For large files (> ~1MB) or on failure, gracefully falls back to the
        simple (n_chars,1) representation.
        """
        import re, math, hashlib
        from collections import Counter
        EMB_DIM = 16
        MAX_FILE_SIZE = 1_000_000  # bytes
        try:
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE:
                raise RuntimeError("File too large for semantic expansion; using fallback")
        except OSError:
            pass

        # Multi-encoding read
        encodings = ['utf-8', 'latin1', 'cp1252']
        text = None
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    text = f.read()
                break
            except UnicodeDecodeError:
                continue
        if text is None:  # last resort
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()

        if len(text) == 0:
            return np.zeros((0, 1), dtype=np.float32)

        # Character-level base encoding
        chars_sorted = sorted(set(text))
        char_to_idx = {c: i+1 for i, c in enumerate(chars_sorted)}  # 1-based
        base_seq = np.fromiter((char_to_idx.get(c, 0) for c in text), dtype=np.int32)
        norm_base = (base_seq / (len(char_to_idx) + 1)).astype(np.float32)

        # Tokenization (simple word tokens) and mapping char positions to tokens
        # Keep original text positions; fallback if tokenization empty.
        token_pattern = re.compile(r"\b\w+\b", re.UNICODE)
        tokens = []
        for m in token_pattern.finditer(text.lower()):
            tokens.append((m.group(0), m.start(), m.end()))

        # Deterministic hashing to embedding for each unique token
        unique_tokens = list({t[0] for t in tokens})
        token_to_emb = {}
        for tok in unique_tokens:
            h = hashlib.sha256(tok.encode('utf-8')).digest()
            # Use first EMB_DIM 32-bit chunks, pad if necessary
            emb_raw = np.frombuffer(h, dtype=np.uint32)
            if len(emb_raw) >= EMB_DIM:
                emb_raw = emb_raw[:EMB_DIM]
            else:
                # Pad with repeated values if hash is too short
                emb_raw = np.tile(emb_raw, (EMB_DIM // len(emb_raw)) + 1)[:EMB_DIM]
            
            emb = emb_raw.astype(np.float32)
            emb /= (np.linalg.norm(emb) + 1e-12)
            token_to_emb[tok] = emb

        # Assemble embedding matrix per character position
        n = len(text)
        emb_matrix = np.zeros((n, EMB_DIM), dtype=np.float32)
        for tok, s, e in tokens:
            emb = token_to_emb[tok]
            if len(emb) == EMB_DIM:
                emb_matrix[s:e, :] = emb
        # Word frequency feature per character
        if tokens:
            token_counts = Counter(t[0] for t in tokens)
            word_freq_vec = np.zeros(n, dtype=np.float32)
            for tok, s, e in tokens:
                word_freq_vec[s:e] = token_counts[tok] / len(tokens)
        else:
            word_freq_vec = np.zeros(n, dtype=np.float32)
        feature_cols = [norm_base, word_freq_vec, emb_matrix]

        # Optional TF-IDF global relevance per token (lines as documents)
        tfidf_col = None
        try:
            # Treat lines as docs if multiple lines exist
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            if len(lines) > 1:
                from sklearn.feature_extraction.text import TfidfVectorizer
                vec = TfidfVectorizer(max_features=512, token_pattern=r"\b\w+\b")
                tfidf = vec.fit_transform(lines)
                # Map each token to its average TF-IDF across documents where it appears
                vocab = vec.vocabulary_
                inv_vocab = {v: k for k, v in vocab.items()}
                token_tfidf = {}
                tfidf_csr = tfidf.tocoo()
                accum = {}
                counts = {}
                for r, c, v in zip(tfidf_csr.row, tfidf_csr.col, tfidf_csr.data):
                    w = inv_vocab.get(c)
                    if w is None:
                        continue
                    accum[w] = accum.get(w, 0.0) + v
                    counts[w] = counts.get(w, 0) + 1
                for w, total in accum.items():
                    token_tfidf[w] = total / counts[w]
                # Build per-character tfidf vector
                tfidf_col = np.zeros(n, dtype=np.float32)
                for tok, s, e in tokens:
                    tfidf_col[s:e] = token_tfidf.get(tok, 0.0)
        except Exception:
            tfidf_col = None

        # Concatenate features: char_norm, word_freq_norm, word_emb(EMB_DIM), [tfidf_mean]
        combined = np.concatenate([
            norm_base.reshape(-1, 1),
            word_freq_vec.reshape(-1, 1),
            emb_matrix
        ], axis=1)
        if tfidf_col is not None:
            tfidf_mean = float(np.mean(tfidf_col)) if len(tfidf_col) > 0 else 0.0
            combined = np.concatenate([combined, np.full((n,1), tfidf_mean, dtype=np.float32)], axis=1)
        return combined.astype(np.float32)


def _load_video_file(file_path: str, extract_ocr: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, Dict]]:
    """
    Load a video file and extract OCR data from frames if requested.
    Uses the process_video_frames function from ocr_integration.
    
    Args:
        file_path: Path to the video file
        extract_ocr: Whether to extract text from video frames using OCR
        
    Returns:
        If extract_ocr is False: First frame as NumPy array
        If extract_ocr is True: Tuple of (First frame as NumPy array, OCR metadata dict)
    """
    logging.debug(f"Loading video from {file_path}")
    
    try:
        # Try OpenCV
        import cv2
        
        # Open the video file
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            raise ValueError(f"Failed to open video file: {file_path}")
            
        # Read the first frame
        ret, first_frame = cap.read()
        if not ret:
            raise ValueError(f"Failed to read the first frame from video: {file_path}")
            
        # Convert BGR to RGB
        if len(first_frame.shape) == 3 and first_frame.shape[2] == 3:
            first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB)
            
        # Release the video capture object
        cap.release()
        
        # Extract OCR data if requested
        if extract_ocr:
            try:
                # Use process_video_frames from ocr_integration
                from .ocr_integration import process_video_frames, create_ocr_index
                
                # Process video frames to extract text
                ocr_df = process_video_frames(file_path)
                
                # Create searchable index
                if not ocr_df.empty:
                    ocr_metadata = {
                        'ocr_index': create_ocr_index(ocr_df),
                        'raw_text': ' '.join(row['text'] for _, row in ocr_df.iterrows()),
                        'text_count': len(ocr_df),
                        'has_text': len(ocr_df) > 0,
                        'language': 'en',  # Default, can be expanded later
                        'ocr_df': ocr_df.to_dict('records'),  # Store for later use
                        'is_video': True,
                        'frame_count': int(ocr_df['frame_number'].max()) + 1 if 'frame_number' in ocr_df.columns else 0,
                        'duration': ocr_df['time_sec'].max() if 'time_sec' in ocr_df.columns else 0
                    }
                else:
                    # Get basic video info if OCR didn't work
                    try:
                        cap = cv2.VideoCapture(file_path)
                        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        duration = frame_count / fps if fps > 0 else 0
                        cap.release()
                    except:
                        frame_count = 0
                        duration = 0
                    
                    ocr_metadata = {
                        'ocr_index': {},
                        'raw_text': '',
                        'text_count': 0,
                        'has_text': False,
                        'language': 'en',
                        'ocr_df': [],
                        'is_video': True,
                        'frame_count': frame_count,
                        'duration': duration
                    }
                
                return first_frame, ocr_metadata
                
            except ImportError:
                logging.warning("OCR integration not available, skipping text extraction from video")
                return first_frame
            except Exception as e:
                logging.error(f"Error in video OCR processing: {e}")
                return first_frame
        
        return first_frame
        
    except ImportError:
        logging.error("OpenCV (cv2) is required for video processing")
        raise ImportError("Video loading requires OpenCV (cv2)")
    except Exception as e:
        logging.error(f"Error loading video {file_path}: {str(e)}")
        raise


def save_to_file(data: Union[np.ndarray, Dict], file_path: str, file_format: str = None) -> None:
    """
    Save matrix or metadata to file.
    
    Args:
        data: The data to save (numpy array, PyTorch tensor, or dictionary)
        file_path: The path to save to
        file_format: Optional format override (e.g., 'npy', 'csv', 'h5')
    """
    import os
    import json
    import logging
    import numpy as np
    import pickle
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Convert PyTorch tensors to NumPy arrays if needed
    if hasattr(data, 'detach'):  # PyTorch tensor
        data = data.detach().cpu().numpy()
    
    # Determine format from file_format parameter or file extension
    if file_format:
        fmt = file_format.lower().lstrip('.')
    else:
        fmt = os.path.splitext(file_path)[1].lower().lstrip('.')

    # License gating for export formats and writes
    try:
        lm = LicenseManager()
        # Check whether writes/exports are allowed for this format
        allowed, msg = lm.check_feature_access('export_writes')
        if not allowed:
            # Permit saving JSON metadata for basic flows but block other formats
            if fmt not in ['json']:
                raise PermissionError(f"Export Error: {msg} - format '{fmt}' not permitted by current license")
        else:
            # If export_writes is allowed, also check format-specific allowances
            formats_allowed = lm.get_allowed_export_formats() if hasattr(lm, 'get_allowed_export_formats') else None
            if formats_allowed and fmt and fmt not in formats_allowed and 'all' not in formats_allowed:
                raise PermissionError(f"Export Error: format '{fmt}' not allowed by license. Allowed: {formats_allowed}")
    except Exception as e:
        # If LicenseManager isn't available or check fails, fall back to permissive but logged behavior
        logging.debug(f"License export gating: {e}")
    
    # Handle dictionaries (metadata)
    if isinstance(data, dict):
        if fmt == 'json':
            logging.debug(f"Saving dictionary as JSON to {file_path}")
            # Use enhanced JSON handling if available
            try:
                from json_handler import save_json_file
                json_metadata = save_json_file(data, file_path, prettify=True)
                logging.debug(f"Enhanced JSON saving complete: {json_metadata.get('file_size', 0)} bytes written")
            except ImportError:
                # Fall back to basic method
                with open(file_path, 'w') as f:
                    json.dump(convert_numpy_types(data), f, indent=2)
        elif fmt in ['pkl', 'pickle']:
            logging.debug(f"Saving dictionary as pickle to {file_path}")
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
        elif fmt in ['xlsx', 'xls']:
            logging.debug(f"Saving dictionary as Excel to {file_path}")
            try:
                import pandas as pd
                # Convert dict to DataFrame if possible
                df = pd.DataFrame([data])
                if fmt == 'xlsx':
                    df.to_excel(file_path, index=False)
                else:
                    df.to_excel(file_path, index=False, engine='xlwt')
            except ImportError:
                logging.warning("pandas and openpyxl/xlwt required for Excel format; defaulting to JSON")
                with open(file_path.replace(f'.{fmt}', '.json'), 'w') as f:
                    json.dump(convert_numpy_types(data), f, indent=2)
        else:
            logging.warning(f"Dictionary data can only be saved as JSON, pickle, or Excel; defaulting to JSON")
            with open(file_path if file_path.endswith('.json') else f"{file_path}.json", 'w') as f:
                json.dump(convert_numpy_types(data), f, indent=2)
        return
        
    # Handle numpy arrays and tensors
    if fmt == 'npy':
        logging.debug(f"Saving NumPy array to {file_path}")
        np.save(file_path, data)
        # Register metadata for saved numpy array (keep provenance consistent)
        try:
            _store_general_metadata(file_path, data, data, 'npy', {
                'file_format': 'npy',
                'dtype': str(data.dtype),
                'shape': data.shape
            })
        except Exception:
            logging.debug('Failed to store metadata for saved .npy file')
    
    elif fmt == 'npz':
        logging.debug(f"Saving NumPy compressed array to {file_path}")
        np.savez_compressed(file_path, data=data)
    
    elif fmt in ['pt', 'pth']:
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch not available. Cannot save as .pt format.")
        logging.debug(f"Saving PyTorch tensor to {file_path}")
        import torch
        if isinstance(data, np.ndarray):
            torch_tensor = torch.from_numpy(data)
        else:
            torch_tensor = data  # Already a tensor
        torch.save(torch_tensor, file_path)
    
    elif fmt in ['csv', 'tsv']:
        delimiter = ',' if fmt == 'csv' else '\t'
        logging.debug(f"Saving tabular data to {file_path}")
        # Check dimensionality - CSV/TSV is primarily for 2D data
        if data.ndim > 2:
            logging.warning(f"Converting {data.ndim}D data to 2D for {fmt.upper()} export")
            data_2d = data.reshape(data.shape[0], -1)
            np.savetxt(file_path, data_2d, delimiter=delimiter)
        else:
            np.savetxt(file_path, data, delimiter=delimiter)
    
    elif fmt in ['xlsx', 'xls']:
        logging.debug(f"Saving Excel data to {file_path}")
        try:
            import pandas as pd
            # Convert to DataFrame
            if data.ndim == 1:
                df = pd.DataFrame(data, columns=['value'])
            elif data.ndim == 2:
                df = pd.DataFrame(data)
            else:
                # Flatten higher dimensional data
                logging.warning(f"Converting {data.ndim}D data to 2D for Excel export")
                data_2d = data.reshape(data.shape[0], -1)
                df = pd.DataFrame(data_2d)
            
            if fmt == 'xlsx':
                df.to_excel(file_path, index=False)
            else:
                df.to_excel(file_path, index=False, engine='xlwt')
        except ImportError:
            raise ImportError("pandas and openpyxl (for .xlsx) or xlwt (for .xls) are required to save Excel files")
    
    elif fmt == 'json':
        logging.debug(f"Saving array as JSON to {file_path}")
        # Use enhanced JSON handling if available
        try:
            from json_handler import save_json_file
            # Convert to list first for better serialization
            data_list = data.tolist() if hasattr(data, 'tolist') else data
            json_metadata = save_json_file(data_list, file_path, prettify=True)
            logging.debug(f"Enhanced JSON array saving complete: {json_metadata.get('file_size', 0)} bytes written")
        except ImportError:
            # Fall back to basic method
            with open(file_path, 'w') as f:
                json.dump(data.tolist(), f)
    
    elif fmt in ['pkl', 'pickle']:
        logging.debug(f"Saving pickle to {file_path}")
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    
    elif fmt in ['h5', 'hdf5']:
        logging.debug(f"Saving HDF5 to {file_path}")
        try:
            import h5py
            with h5py.File(file_path, 'w') as f:
                f.create_dataset('data', data=data, compression='gzip')
        except ImportError:
            raise ImportError("h5py package required to save HDF5 files")
    
    elif fmt == 'mat':
        logging.debug(f"Saving MATLAB file to {file_path}")
        try:
            import scipy.io
            scipy.io.savemat(file_path, {'data': data})
        except ImportError:
            raise ImportError("scipy package required to save MATLAB files")
    
    elif fmt in ['nc', 'cdf']:
        logging.debug(f"Saving NetCDF to {file_path}")
        try:
            import netCDF4
            # Create dimensions based on the shape
            with netCDF4.Dataset(file_path, 'w') as nc:
                for i, dim_size in enumerate(data.shape):
                    nc.createDimension(f'dim{i}', dim_size)
                
                # Create the variable using the dimensions
                dims = tuple(f'dim{i}' for i in range(data.ndim))
                var = nc.createVariable('data', data.dtype, dims, zlib=True)
                var[:] = data
        except ImportError:
            raise ImportError("netCDF4 package required to save NetCDF files")
    
    elif fmt in ['tiff', 'tif']:
        logging.debug(f"Saving TIFF to {file_path}")
        try:
            import tifffile
            tifffile.imwrite(file_path, data)
        except ImportError:
            raise ImportError("tifffile package required to save TIFF files")
    
    elif fmt in ['nii', 'nii.gz']:
        logging.debug(f"Saving NIfTI to {file_path}")
        try:
            import nibabel as nib
            img = nib.Nifti1Image(data, np.eye(4))
            nib.save(img, file_path)
        except ImportError:
            raise ImportError("nibabel package required to save NIfTI files")
    
    elif fmt == 'zarr':
        logging.debug(f"Saving Zarr to {file_path}")
        try:
            import zarr # pyright: ignore[reportMissingImports]
            z = zarr.open(file_path, mode='w', shape=data.shape, dtype=data.dtype)
            z[:] = data
        except ImportError:
            raise ImportError("zarr package required to save Zarr files")
    
    # Image formats (for array data that represents images)
    elif fmt in ['jpg', 'jpeg', 'png', 'bmp']:
        logging.debug(f"Saving image to {file_path}")
        try:
            from PIL import Image
            # Ensure data is in the right format for PIL
            if data.dtype != np.uint8:
                # Normalize to 0-255 range if needed
                if data.max() <= 1.0:
                    data = (data * 255).astype(np.uint8)
                else:
                    data = np.clip(data, 0, 255).astype(np.uint8)
            
            # Handle different array shapes
            if data.ndim == 2:
                # Grayscale
                img = Image.fromarray(data, mode='L')
            elif data.ndim == 3 and data.shape[2] == 3:
                # RGB
                img = Image.fromarray(data, mode='RGB')
            elif data.ndim == 3 and data.shape[2] == 4:
                # RGBA
                img = Image.fromarray(data, mode='RGBA')
            else:
                # Flatten to 2D grayscale
                logging.warning(f"Converting {data.shape} array to grayscale for image export")
                if data.ndim > 2:
                    data = np.mean(data, axis=tuple(range(2, data.ndim)))
                img = Image.fromarray(data.astype(np.uint8), mode='L')
            
            img.save(file_path)
        except ImportError:
            raise ImportError("PIL (Pillow) package required to save image files")
    
    # Text format (for simple array data)
    elif fmt in ['txt', 'md']:
        logging.debug(f"Saving text to {file_path}")
        with open(file_path, 'w') as f:
            if data.ndim == 1:
                # Save as simple list
                for item in data:
                    f.write(f"{item}\n")
            elif data.ndim == 2:
                # Save as space-separated values
                for row in data:
                    f.write(" ".join(map(str, row)) + "\n")
            else:
                # Flatten and save
                f.write(" ".join(map(str, data.flatten())))
    
    # HTML format (for simple data visualization)
    elif fmt in ['html', 'htm']:
        logging.debug(f"Saving HTML to {file_path}")
        with open(file_path, 'w') as f:
            f.write("<html><head><title>Array Data</title></head><body>\n")
            f.write(f"<h1>Array Data (Shape: {data.shape})</h1>\n")
            if data.ndim <= 2:
                f.write("<table border='1'>\n")
                if data.ndim == 1:
                    for item in data:
                        f.write(f"<tr><td>{item}</td></tr>\n")
                else:
                    for row in data:
                        f.write("<tr>")
                        for item in row:
                            f.write(f"<td>{item}</td>")
                        f.write("</tr>\n")
                f.write("</table>\n")
            else:
                f.write(f"<p>Data shape: {data.shape}</p>\n")
                f.write(f"<p>Data type: {data.dtype}</p>\n")
                f.write(f"<p>Min value: {data.min()}</p>\n")
                f.write(f"<p>Max value: {data.max()}</p>\n")
                f.write(f"<p>Mean value: {data.mean()}</p>\n")
            f.write("</body></html>\n")
    
    # XML format (for structured data representation)
    elif fmt == 'xml':
        logging.debug(f"Saving XML to {file_path}")
        with open(file_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(f'<array shape="{",".join(map(str, data.shape))}" dtype="{data.dtype}">\n')
            if data.ndim == 1:
                for i, item in enumerate(data):
                    f.write(f'  <element index="{i}">{item}</element>\n')
            elif data.ndim == 2:
                for i, row in enumerate(data):
                    f.write(f'  <row index="{i}">\n')
                    for j, item in enumerate(row):
                        f.write(f'    <element index="{j}">{item}</element>\n')
                    f.write('  </row>\n')
            else:
                # For higher dimensions, save flattened with coordinates
                coords = np.unravel_index(range(data.size), data.shape)
                for idx in range(data.size):
                    coord_str = ",".join(str(coords[dim][idx]) for dim in range(data.ndim))
                    f.write(f'  <element coords="{coord_str}">{data.flat[idx]}</element>\n')
            f.write('</array>\n')
    
    else:
        logging.warning(f"Unsupported format '{fmt}'. Defaulting to .npy")
        np.save(f"{file_path}.npy" if not file_path.endswith('.npy') else file_path, data)


def load_and_apply_transform(file_path: str, transform_name: str = None) -> np.ndarray:
    """
    Load tensor data from file and optionally apply a registered transform.
    
    Args:
        file_path: Path to the file to load
        transform_name: Name of the registered transform to apply (optional)
        
    Returns:
        Numpy array containing the loaded (and potentially transformed) data
    """
    import os
    import logging
    
    import json

    # If a transform is specified, try to find its metadata first. Some transforms
    # (for example file-format handlers) can load the file directly (accepting a
    # file path) and should be given the opportunity to do so before attempting
    # to load the raw data with the default loader.
    transform_metadata = None
    if transform_name:
        from pathlib import Path
        registry_dir = Path.home() / '.tensorpack' / 'transforms'
        try:
            logging.debug(f"Looking for transform metadata for '{transform_name}' in {registry_dir}")
            if registry_dir.exists():
                for data_type_dir in registry_dir.iterdir():
                    if data_type_dir.is_dir():
                        metadata_file = data_type_dir / f"{transform_name}_metadata.json"
                        if metadata_file.exists():
                            logging.debug(f"Found transform metadata at {metadata_file}")
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                transform_metadata = json.load(f)
                            break
        except Exception as e:
            logging.debug(f"Error while reading user transform registry: {e}")
            transform_metadata = None

        # Fallback: check local repository transforms folder (useful during development)
        if transform_metadata is None:
            try:
                local_registry = Path(os.path.dirname(__file__)) / 'transforms'
                logging.debug(f"Looking for transform metadata for '{transform_name}' in local {local_registry}")
                metadata_file = local_registry / f"{transform_name}_metadata.json"
                if metadata_file.exists():
                    logging.debug(f"Found local transform metadata at {metadata_file}")
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        transform_metadata = json.load(f)
            except Exception as e:
                logging.debug(f"Error while reading local transform registry: {e}")

    # If transform declares it handles the file format (e.g. '.parquet'), attempt
    # to let it load the file directly. This allows transforms that accept a file
    # path (rather than an already-loaded numpy array) to operate.
    if transform_metadata:
        try:
            props = transform_metadata.get('properties', {}) or {}
            handles = props.get('handles_format') or props.get('handles_formats') or ''
            # Normalize to a list of lower-case extensions
            if isinstance(handles, str):
                handles_list = [h.strip().lower() for h in handles.split(',') if h.strip()]
            elif isinstance(handles, (list, tuple)):
                handles_list = [str(h).strip().lower() for h in handles]
            else:
                handles_list = []

            file_ext = os.path.splitext(file_path)[1].lower()
            logging.debug(f"Transform '{transform_name}' handles: {handles_list}; file ext: {file_ext}")
            if file_ext in handles_list:
                logging.info(f"Using transform '{transform_name}' to load {file_path} directly (transform handles '{file_ext}')")
                try:
                    # Pass the file path to the transform - transforms should handle
                    # either a numpy array or a file path according to the contract.
                    transformed = _execute_transform(file_path, transform_metadata, file_path)
                    logging.debug(f"Transform '{transform_name}' returned data of type {type(transformed)}")
                    return transformed
                except Exception as e:
                    logging.warning(f"Transform '{transform_name}' failed to load file directly: {e}. Falling back to default loader.")
        except Exception:
            # If anything about metadata parsing fails, ignore and fall back
            pass

    # Load the raw data first (default behavior)
    raw_data = load_tensor_from_file(file_path)
    
    # If no transform specified, return raw data
    if not transform_name:
        return raw_data
    
    try:
        # Load the transform from the global transform registry
        from pathlib import Path
        
        # Look for the transform in the global registry
        registry_dir = Path.home() / '.tensorpack' / 'transforms'
        transform_found = False
        transform_metadata = None
        
        # Search through all data types for the transform
        for data_type_dir in registry_dir.iterdir():
            if data_type_dir.is_dir():
                metadata_file = data_type_dir / f"{transform_name}_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        transform_metadata = json.load(f)
                    transform_found = True
                    break
        
        if not transform_found:
            logging.warning(f"Transform '{transform_name}' not found. Using raw data.")
            return raw_data
        
        # Load transform metadata is already loaded above
        
        logging.info(f"Applying transform '{transform_name}' to {os.path.basename(file_path)}")
        
        # Apply the transform based on its type
        transformed_data = _execute_transform(raw_data, transform_metadata, file_path)
        
        # NEW: Handle entity mapping and propagation through transformation
        try:
            # Check if transform metadata includes entity mapping information
            entity_mapping = transform_metadata.get('entity_mapping', {})
            
            if entity_mapping:
                logging.debug(f"Applying entity mapping from transform metadata")
                # Map entities to regions in the transformed data
                _map_entities_to_matrix_regions(transformed_data, entity_mapping)
            
            # Propagate existing entities from source to target if transformation allows it
            transformation_info = {
                'type': transform_metadata.get('type', 'unknown'),
                'function_name': transform_metadata.get('source_info', {}).get('function_name', ''),
                'metadata': transform_metadata
            }
            
            # Propagate entities through the transformation
            propagated_entities = _propagate_entities_through_transformation(
                raw_data, transformed_data, transformation_info
            )
            
            if propagated_entities:
                logging.info(f"Successfully propagated {len(propagated_entities)} entities through transformation")
            
        except Exception as e:
            logging.debug(f"Entity propagation failed (this is normal if no entities exist): {e}")
        
        # Store transform application metadata
        _store_transform_metadata(file_path, transform_name, transform_metadata)
        
        logging.debug(f"Transform '{transform_name}' applied successfully. "
                     f"Shape: {raw_data.shape} → {transformed_data.shape}")
        
        return transformed_data
        
    except Exception as e:
        logging.error(f"Failed to apply transform '{transform_name}': {e}")
        logging.warning("Falling back to raw data.")
        return raw_data


def _execute_transform(data: np.ndarray, transform_metadata: dict, file_path: str) -> np.ndarray:
    """Execute a transform on the given data."""
    import os
    import sys
    import importlib.util
    from pathlib import Path
    
    # Get source info from the metadata structure
    source_info = transform_metadata.get('source_info', {})
    source_type = source_info.get('type', 'python')
    source = source_info.get('source', '')
    function_name = source_info.get('function_name', 'transform')
    # Defensive: ensure function_name is a string to avoid hasattr() TypeError
    if function_name is None:
        logging.debug("Transform metadata 'function_name' is None, defaulting to 'transform'")
        function_name = 'transform'
    elif not isinstance(function_name, str):
        logging.warning(f"Invalid transform function_name type: {type(function_name)}; coercing to 'transform'")
        function_name = 'transform'
    
    if source_type == 'python':
        # Ensure Path is imported
        from pathlib import Path
        # The source should be a filename, look for it in the current directory or registry
        if os.path.isabs(source):
            module_path = source
        elif os.path.exists(source):
            # Source file is in current directory
            module_path = os.path.abspath(source)
        else:
            # Look in the transform registry directory
            data_type = transform_metadata.get('data_type', 'custom')
            registry_dir = Path.home() / '.tensorpack' / 'transforms' / data_type
            module_path = str(registry_dir / source)

        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Transform source file not found: {module_path}")

        # Load the module
        import importlib.util, sys, traceback
        spec = importlib.util.spec_from_file_location("transform_module", module_path)
        transform_module = importlib.util.module_from_spec(spec)
        sys.modules["transform_module"] = transform_module
        spec.loader.exec_module(transform_module)
        
        # Get the transform function
        if isinstance(function_name, str) and hasattr(transform_module, function_name):
            transform_func = getattr(transform_module, function_name)

            # Log debug info about the transform function and the data being passed
            try:
                import inspect
                sig = inspect.signature(transform_func)
                logging.debug(f"Transform function '{function_name}' signature: {sig}")
            except Exception:
                logging.debug(f"Could not obtain signature for transform '{function_name}'")

            logging.debug(f"Calling transform '{function_name}' with data type: {type(data)}")

            # Call safely with rich error reporting
            try:
                result = transform_func(data)
                logging.debug(f"Transform '{function_name}' executed successfully, returned type: {type(result)}")
            except Exception as e:
                tb = traceback.format_exc()
                logging.debug(f"Initial transform call failed: {e}\n{tb}")
                # If calling with the original data failed and data is path-like,
                # try passing file_path explicitly (some transforms expect the
                # parameter name to be 'file_path' or similar).
                try:
                    if isinstance(data, (str, Path)):
                        logging.debug(f"Retrying transform '{function_name}' with explicit file_path argument")
                        try:
                            result = transform_func(file_path)
                            logging.debug(f"Transform '{function_name}' succeeded with file_path call, returned type: {type(result)}")
                        except Exception:
                            try:
                                result = transform_func(file_path=file_path)
                                logging.debug(f"Transform '{function_name}' succeeded with file_path= keyword, returned type: {type(result)}")
                            except Exception as e2:
                                logging.debug(f"Retry attempts failed for transform '{function_name}': {e2}\n{traceback.format_exc()}")
                                raise
                    else:
                        raise
                except Exception:
                    raise

            # If the transform returns a tuple (array, metadata), use only the array for downstream code
            if isinstance(result, tuple) and len(result) == 2 and hasattr(result[0], 'shape'):
                return result[0]
            return result
        else:
            raise AttributeError(f"Function '{function_name}' not found in transform module")
    
    elif source_type == 'inline':
        # Execute inline transformation
        exec_globals = {'np': np, 'data': data, 'file_path': file_path}
        exec(source, exec_globals)
        return exec_globals.get('result', data)
    
    else:
        raise ValueError(f"Unsupported transform source type: {source_type}")


def _store_transform_metadata(file_path: str, transform_name: str, transform_metadata: dict):
    """Store metadata about the applied transform."""
    # This integrates with the existing metadata storage system
    if hasattr(_store_transform_metadata, '_registry'):
        if file_path not in _store_transform_metadata._registry:
            _store_transform_metadata._registry[file_path] = {}
        
        _store_transform_metadata._registry[file_path]['applied_transform'] = {
            'name': transform_name,
            'metadata': transform_metadata,
            'applied_at': time.time()
        }
    else:
        # Initialize registry if it doesn't exist
        _store_transform_metadata._registry = {
            file_path: {
                'applied_transform': {
                    'name': transform_name,
                    'metadata': transform_metadata,
                    'applied_at': time.time()
                }
            }
        }


def _get_transform_metadata(input_files: List[str]) -> Dict[str, Any]:
    """Get metadata about applied transforms for the input files."""
    transform_info = {}
    
    if hasattr(_store_transform_metadata, '_registry'):
        for file_path in input_files:
            if file_path in _store_transform_metadata._registry:
                transform_info[file_path] = _store_transform_metadata._registry[file_path]
    
    return transform_info if transform_info else None


def convert_numpy_types(obj: Any) -> Any:
    """
    Convert numpy types to Python types for JSON serialization with enhanced handling
    for complex and nested structures.
    """
    # First try importing the enhanced JSON handling
    try:
        from json_handler import convert_types
        return convert_types(obj)
    except ImportError:
        # Fall back to basic implementation
        pass
        
    # Handle various NumPy types
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    # Fix for NumPy 2.0 compatibility - use individual checks instead of tuples with removed types
    elif isinstance(obj, np.integer):  # Covers all integer types
        return int(obj)
    elif isinstance(obj, np.floating):  # Covers all float types
        return float(obj)
    elif isinstance(obj, np.complexfloating):  # Covers all complex types
        return {'real': float(obj.real), 'imag': float(obj.imag)}
    elif isinstance(obj, np.bool_):
        return bool(obj)
    # Handle recursive types
    elif isinstance(obj, dict):
        try:
            # Handle potential circular references with a depth limit
            return {str(k): convert_numpy_types(v) for k, v in obj.items()}
        except RecursionError:
            # Handle circular reference by stringifying the problematic object
            return {str(k): str(v) if isinstance(v, (dict, list, tuple)) else convert_numpy_types(v) 
                  for k, v in obj.items()}
    elif isinstance(obj, list):
        try:
            return [convert_numpy_types(item) for item in obj]
        except RecursionError:
            # Handle circular reference
            return [str(item) if isinstance(item, (dict, list, tuple)) else convert_numpy_types(item) 
                   for item in obj]
    elif isinstance(obj, tuple):
        try:
            return [convert_numpy_types(item) for item in obj]
        except RecursionError:
            return [str(item) if isinstance(item, (dict, list, tuple)) else convert_numpy_types(item) 
                   for item in obj]
    elif isinstance(obj, (set, frozenset)):
        return [convert_numpy_types(item) for item in obj]
    # Handle date/time objects
    elif hasattr(obj, 'isoformat'):  # datetime, date, time objects
        return obj.isoformat()
    # Handle objects with direct conversion
    elif hasattr(obj, 'tolist'):  # Other array-like objects
        return obj.tolist()
    # Base types and fallbacks
    elif obj is None or isinstance(obj, (bool, str, int, float)):
        return obj
    else:
        try:
            # Try JSON encoding as a test
            import json
            json.dumps(str(obj))
            return str(obj)
        except:
            # Last resort for truly problematic objects
            return f"<Non-serializable object of type {type(obj).__name__}>"


def apply_normalization(tensor: np.ndarray, method: str) -> np.ndarray:
    """Apply normalization to tensor based on specified method."""
    if method == 'none':
        return tensor
    
    # Handle empty tensor
    if tensor.size == 0:
        return tensor
    
    if method == 'frobenius':
        norm = np.linalg.norm(tensor)
        if norm > 1e-10:
            return tensor / norm
    elif method == 'max':
        max_val = np.max(np.abs(tensor))
        if max_val > 1e-10:
            return tensor / max_val
    elif method == 'l1':
        l1_norm = np.sum(np.abs(tensor))
        if l1_norm > 1e-10:
            return tensor / l1_norm
    elif method == 'l2':
        l2_norm = np.sqrt(np.sum(tensor**2))
        if l2_norm > 1e-10:
            return tensor / l2_norm
    
    # If normalization fails or is not recognized, return original
    return tensor


def tensor_to_matrix_command(args: argparse.Namespace) -> int:
    """Handle tensor_to_matrix conversion command."""
    setup_logging(args.verbose, args.log)
    logging.info(f"Converting tensor to matrix from {args.input}")
    # License-based gating: check file size and feature access
    try:
        lm = LicenseManager()
        # File size check
        try:
            file_size_mb = os.path.getsize(args.input) / (1024.0 * 1024.0)
            ok_size, msg_size = lm.check_file_size_limit(file_size_mb)
            if not ok_size:
                print(f"License Error: {msg_size}")
                print(lm.show_upgrade_info())
                return 2
        except Exception:
            pass
        # Feature access (basic conversion allowed on free tier)
        ok_feature, feature_msg = lm.check_feature_access('tensor_to_matrix')
        if not ok_feature:
            print(f"License Error: {feature_msg}")
            return 2
    except Exception:
        # If license manager fails, proceed in permissive mode
        logging.debug("License manager unavailable; proceeding.")
    
    try:
        start_time = time.time()
        
        # Create MatrixTransformer instance
        transformer = MatrixTransformer()
        
        # Load input tensor
        tensor = load_tensor_from_file(args.input)
        logging.info(f"Loaded tensor with shape {tensor.shape} and dtype {tensor.dtype}")
        
        # Apply normalization if requested
        if args.normalize != 'none':
            original_tensor = tensor.copy()
            tensor = apply_normalization(tensor, args.normalize)
            logging.info(f"Applied {args.normalize} normalization")
        
        # Convert dtype if specified
        if args.dtype:
            try:
                tensor = tensor.astype(np.dtype(args.dtype))
                logging.info(f"Converted tensor to dtype {tensor.dtype}")
            except TypeError:
                logging.warning(f"Failed to convert tensor to dtype {args.dtype}")
        
        # Configure encoding options based on flatten mode
        encoding_options = {
            'flatten_mode': args.flatten_mode,
            'encoding': args.encoding,
            'preserve_sparsity': args.preserve_sparsity
        }
        
        # Convert tensor to matrix
        logging.info(f"Converting tensor using {args.flatten_mode} mode with {args.encoding} encoding")
        matrix, metadata = transformer.tensor_to_matrix(tensor)
        
        # Add matrix shape to metadata
        metadata['matrix_shape'] = matrix.shape
        # If input was a JSON file carrying additional top-level keys (e.g. description, dtype, shape),
        # preserve those keys inside metadata so we can restore them when decoding.
        try:
            if str(args.input).lower().endswith('.json'):
                with open(args.input, 'r', encoding='utf-8') as _jf:
                    try:
                        _orig_json = json.load(_jf)
                        original_keys = {}
                        for k in ('description', 'dtype', 'shape'):
                            if k in _orig_json:
                                original_keys[k] = _orig_json[k]
                        if original_keys:
                            metadata['original_file_keys'] = original_keys
                    except Exception:
                        pass
        except Exception:
            pass
        
        # Determine output file path
        output_path = args.output or os.path.splitext(args.input)[0] + "_matrix.npy"
        
        # Save matrix
        save_to_file(matrix, output_path, args.json)
        logging.info(f"Saved matrix to {output_path}")
        
        # Save metadata if requested
        meta_path = None
        if args.meta_file:
            meta_path = args.meta_file
            save_to_file(metadata, meta_path, 'json')
            logging.info(f"Saved metadata to {meta_path}")
        else:
            # Default metadata path
            meta_path = os.path.splitext(output_path)[0] + "_metadata.json"
            save_to_file(metadata, meta_path, 'json')
            logging.info(f"Saved metadata to {meta_path}")
        
        elapsed_time = time.time() - start_time
        
        # Calculate an error estimate (if requested)
        error_estimate = None
        if args.estimate_error:
            # Simple error estimation by checking some values
            reconstructed = transformer.matrix_to_tensor(matrix, metadata)
            if reconstructed.shape == tensor.shape:
                error_estimate = np.max(np.abs(reconstructed - tensor))
            
        # Print user-friendly output for easy parsing
        input_basename = os.path.basename(args.input)
        output_basename = os.path.basename(output_path)
        meta_basename = os.path.basename(meta_path)
        print(f"Encoded: {input_basename} -> {output_basename}")
        print(f"Meta saved: {meta_basename}")
        print(f"Original tensor shape: {tensor.shape} -> Matrix shape: {matrix.shape}")
        if error_estimate is not None:
            print(f"Time: {elapsed_time:.4f}s | Error: {error_estimate:.6e}")
        else:
            print(f"Time: {elapsed_time:.4f}s")
        
        logging.info("Conversion completed successfully")
        return 0
        
    except Exception as e:
        logging.error(f"Error during tensor to matrix conversion: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def matrix_to_tensor_command(args: argparse.Namespace) -> int:
    """Handle matrix_to_tensor conversion command."""
    setup_logging(args.verbose, args.log)
    logging.info(f"Converting matrix to tensor from {args.input}")
    # License-based gating: check feature access
    try:
        lm = LicenseManager()
        ok_feature, feature_msg = lm.check_feature_access('matrix_to_tensor')
        if not ok_feature:
            print(f"License Error: {feature_msg}")
            return 2
    except Exception:
        logging.debug("License manager unavailable; proceeding.")
    
    try:
        start_time = time.time()
        
        # Create MatrixTransformer instance
        transformer = MatrixTransformer()
        
        # Load input matrix
        matrix = load_tensor_from_file(args.input)
        logging.info(f"Loaded matrix with shape {matrix.shape} and dtype {matrix.dtype}")
        
        # Handle metadata
        metadata = None
        if args.metadata:
            with open(args.metadata, 'r') as f:
                metadata = json.load(f)
            logging.info(f"Loaded metadata from {args.metadata}")
        else:
            # Try to find metadata file based on input name
            default_meta_path = os.path.splitext(args.input)[0] + "_metadata.json"
            if os.path.exists(default_meta_path):
                with open(default_meta_path, 'r') as f:
                    metadata = json.load(f)
                logging.info(f"Loaded metadata from {default_meta_path}")
        
        # If inspect mode is activated, just display metadata and exit
        if args.inspect:
            if metadata:
                print(json.dumps(metadata, indent=2))
                return 0
            else:
                logging.error("No metadata provided for inspection")
                return 1
        
        # Parse target shape if provided
        target_shape = None
        if args.target_shape:
            try:
                target_shape = tuple(map(int, args.target_shape.split(',')))
                logging.info(f"Using target shape: {target_shape}")
            except ValueError:
                logging.error(f"Invalid target shape: {args.target_shape}")
                return 1
        
        # Convert to tensor
        fill_mode_options = {
            'zeros': 0,
            'extrapolate': 1,
            'repeat': 2
        }
        
        # Configure options
        options = {
            'fill_mode': fill_mode_options.get(args.fill_mode, 0),
            'force_reconstruction': args.force_reconstruction
        }
        
        # Convert matrix to tensor
        tensor = transformer.matrix_to_tensor(matrix, metadata, target_shape)
        
        # Convert dtype if specified
        if args.target_dtype:
            try:
                tensor = tensor.astype(np.dtype(args.target_dtype))
                logging.info(f"Converted tensor to dtype {tensor.dtype}")
            except TypeError:
                logging.warning(f"Failed to convert tensor to dtype {args.target_dtype}")
        
        # Determine output file path
        output_path = args.output or os.path.splitext(args.input)[0] + "_tensor.npy"

        # Save tensor. Best practice: keep data and metadata separate.
        # If user requested a .json output path we will write metadata-only JSON to that
        # path and save the numeric array to a companion .npy file (same base name).
        if str(output_path).lower().endswith('.json'):
            base = os.path.splitext(output_path)[0]
            data_path = base + '.npy'

            # If metadata carries original file keys, prefer those (so description/dtype are preserved)
            orig_keys = metadata.get('original_file_keys') if metadata else None
            # If original dtype is known from the original file, cast tensor to that dtype
            if orig_keys and 'dtype' in orig_keys:
                try:
                    tensor = tensor.astype(np.dtype(orig_keys['dtype']))
                    logging.info(f"Casting reconstructed tensor to original dtype {orig_keys['dtype']}")
                except Exception:
                    logging.debug('Failed to cast reconstructed tensor to original dtype')

            # Save numeric data in .npy (fast, production-ready)
            try:
                # Use numpy savez_compressed if user wants compressed single-file storage later
                np.save(data_path, tensor)
                logging.info(f"Saved numeric tensor to {data_path}")
            except Exception:
                # Fallback to save_to_file for arrays if available
                try:
                    save_to_file(tensor, data_path, None)
                    logging.info(f"Saved numeric tensor to {data_path} (via save_to_file)")
                except Exception:
                    logging.error(f"Failed to save numeric tensor to {data_path}")

            # Build metadata-only JSON (do not embed 'data')
            meta_out = {}
            if orig_keys:
                # Promote only provenance keys (dtype and shape) into metadata.
                # Do NOT include user-facing text like 'description' to avoid
                # embedding potentially sensitive or large fields in metadata-only files.
                if 'dtype' in orig_keys:
                    meta_out['original_dtype'] = orig_keys['dtype']
                if 'shape' in orig_keys:
                    meta_out['original_shape'] = orig_keys['shape']

            if metadata:
                meta_out.update(convert_numpy_types(metadata))
            # Also record where the numeric data lives
            meta_out['_data_path'] = os.path.basename(data_path)

            save_to_file(meta_out, output_path, 'json')
            logging.info(f"Saved metadata-only JSON to {output_path}")
        else:
            save_to_file(tensor, output_path, None)

        logging.info(f"Saved tensor to {output_path}")
        
        elapsed_time = time.time() - start_time
        
        # Error calculation
        error = None
        
        # Perform verification if requested
        if args.verify and metadata is not None:
            # Convert back to matrix for comparison
            verify_matrix, _ = transformer.tensor_to_matrix(tensor)
            
            # Calculate error
            error = np.mean(np.abs(verify_matrix - matrix))
            logging.info(f"Reconstruction error: {error}")
            
            # Check against threshold
            if args.error_threshold is not None and error > args.error_threshold:
                logging.error(f"Error {error} exceeds threshold {args.error_threshold}")
                return 1
                
            logging.info("Verification completed successfully")
        
        # Print user-friendly output for easy parsing
        input_basename = os.path.basename(args.input)
        output_basename = os.path.basename(output_path)
        print(f"Decoded: {input_basename} -> {output_basename}")
        print(f"Matrix shape: {matrix.shape} -> Reconstructed tensor shape: {tensor.shape}")
        if error is not None:
            print(f"Time: {elapsed_time:.4f}s | Error: {error:.6e}")
        else:
            print(f"Time: {elapsed_time:.4f}s")
        
        logging.info("Conversion completed successfully")
        return 0
        
    except Exception as e:
        logging.error(f"Error during matrix to tensor conversion: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def add_transform_command(args: argparse.Namespace) -> int:
    """Handle adding custom transformation rules to TensorPack."""
    setup_logging(args.verbose, args.log)
    
    # Check license for custom transformation management
    try:
        license_manager = LicenseManager()
        has_access, message = license_manager.check_feature_access('custom_transformations')
        if not has_access:
            print(f"License Error: {message}")
            print("\nCustom transformation management requires a premium license.")
            print("Upgrade for full access: tensorpack upgrade")
            return 1
    except Exception as e:
        logging.warning(f"License check failed: {e}. Proceeding with basic functionality.")
    
    # Determine if this is an entity matcher
    operation_type = getattr(args, 'operation_type', 'transformation')
    
    if operation_type == 'entity_matching':
        logging.info(f"Adding custom entity matcher: {args.name} for type {args.data_type}")
    else:
        logging.info(f"Adding custom transformation: {args.name} for type {args.data_type}")
    
    try:
        start_time = time.time()
        # If embedding, enforce license gating for embedding transforms
        if getattr(args, 'embed', False):
            try:
                lm = LicenseManager()
                ok, msg = lm.check_feature_access('embed_transforms')
                if not ok:
                    print(f"License Error: {msg}")
                    print("Embedding custom transforms requires an upgraded license.")
                    return 1

                # If unrestricted embedding requested, check specific allowance
                if getattr(args, 'embed_unrestricted', False):
                    ok2, msg2 = lm.check_feature_access('embed_unrestricted')
                    if not ok2:
                        print(f"License Error: {msg2}")
                        print("Unrestricted embedding is not allowed for your license tier.")
                        return 1
                    # Otherwise allow unrestricted embedding
            except Exception as e:
                logging.warning(f"License check for embedding failed: {e}. Proceeding with caution.")
        
        # Create MatrixTransformer instance
        transformer = MatrixTransformer()
        
        # Validate data type
        supported_types = [
            'matrix', 'json', 'graph', 'timeseries', 'image', 'audio', 
            'genomics', 'finance', 'text', 'biomedical', 'custom'
        ]
        
        if args.data_type not in supported_types:
            logging.error(f"Unsupported data type: {args.data_type}. Supported types: {supported_types}")
            return 1
        
        # Parse properties if provided
        properties = {}
        if args.properties:
            try:
                # Support both JSON string and key=value pairs
                if args.properties.startswith('{'):
                    import json
                    properties = json.loads(args.properties)
                else:
                    # Parse key=value,key=value format
                    for prop in args.properties.split(','):
                        if '=' in prop:
                            key, value = prop.split('=', 1)
                            # Try to parse as number or boolean
                            try:
                                if value.lower() in ['true', 'false']:
                                    properties[key.strip()] = value.lower() == 'true'
                                elif '.' in value:
                                    properties[key.strip()] = float(value)
                                else:
                                    properties[key.strip()] = int(value)
                            except ValueError:
                                properties[key.strip()] = value.strip()
                logging.info(f"Parsed properties: {properties}")
            except Exception as e:
                logging.error(f"Error parsing properties: {e}")
                return 1
        
        # Parse neighbors list
        neighbors = []
        if args.neighbors:
            neighbors = [n.strip() for n in args.neighbors.split(',')]
            logging.info(f"Neighbors: {neighbors}")
        
        # Load transform rule from source
        transform_rule = None
        
        if args.source_type == 'python':
            # Load Python function
            if operation_type == 'entity_matching':
                transform_rule = _load_entity_matcher_function(args.source, args.function_name)
            else:
                transform_rule = load_python_transform(args.source, args.function_name)
        elif args.source_type == 'executable':
            # Create wrapper for external executable
            transform_rule = create_executable_wrapper(args.source, args.data_type)
        elif args.source_type == 'inline':
            # Parse inline transformation definition
            transform_rule = parse_inline_transform(args.source, args.data_type)
        elif args.source_type == 'config':
            # Load configuration-based transform
            transform_rule = load_config_transform(args.source, args.data_type)
        else:
            logging.error(f"Unknown source type: {args.source_type}")
            return 1
        
        if transform_rule is None:
            logging.error("Failed to load transformation rule")
            return 1
        
        # Test the transformation/entity matcher if test data is provided
        if args.test_data:
            import os
            test_file_ext = os.path.splitext(args.test_data)[1].lower()
            handles_format = properties.get('handles_format') if properties else None

            # If handles_format matches test file extension, pass file path directly
            if handles_format and test_file_ext == handles_format.lower():
                logging.info("Testing transformation with provided data (custom handler for format)...")
                try:
                    if operation_type == 'entity_matching':
                        test_entity = getattr(args, 'test_entity', 'test')
                        test_dataset_info = {'data_type': args.data_type, 'shape': None}
                        test_result = transform_rule(args.test_data, test_entity, test_dataset_info)
                        logging.info(f"Entity matcher test successful (custom handler). Found {len(test_result)} matches")
                    else:
                        test_result = transform_rule(args.test_data)
                        out_shape = getattr(test_result, 'shape', None)
                        logging.info(f"Test successful (custom handler). Output shape: {out_shape}")

                    # Save test result if requested
                    if args.test_output:
                        if operation_type == 'entity_matching':
                            import json
                            with open(args.test_output, 'w', encoding='utf-8') as f:
                                json.dump(test_result, f, indent=2)
                        else:
                            save_to_file(test_result, args.test_output)
                        logging.info(f"Test result saved to {args.test_output}")
                except Exception as e:
                    logging.error(f"Test failed (custom handler): {e}")
                    if not args.force:
                        return 1
                    logging.warning("Continuing despite test failure due to --force flag")
            else:
                logging.info("Testing transformation with provided data...")
                test_data = load_tensor_from_file(args.test_data)
                try:
                    if operation_type == 'entity_matching':
                        test_entity = getattr(args, 'test_entity', 'test')
                        test_dataset_info = {'data_type': args.data_type, 'shape': getattr(test_data, 'shape', None)}
                        test_result = transform_rule(test_data, test_entity, test_dataset_info)
                        logging.info(f"Entity matcher test successful. Found {len(test_result)} matches")
                    else:
                        test_result = transform_rule(test_data)
                        logging.info(f"Test successful. Input shape: {getattr(test_data, 'shape', None)}, Output shape: {getattr(test_result, 'shape', None)}")

                    # Save test result if requested
                    if args.test_output:
                        if operation_type == 'entity_matching':
                            import json
                            with open(args.test_output, 'w', encoding='utf-8') as f:
                                json.dump(test_result, f, indent=2)
                        else:
                            save_to_file(test_result, args.test_output)
                        logging.info(f"Test result saved to {args.test_output}")
                except Exception as e:
                    logging.error(f"Test failed: {e}")
                    if not args.force:
                        return 1
                    logging.warning("Continuing despite test failure due to --force flag")
        
        # Add the transformation to the system
        success = add_transform_to_registry(
            name=args.name,
            data_type=args.data_type,
            transform_rule=transform_rule,
            properties=properties,
            neighbors=neighbors,
            source_info={
                'type': args.source_type,
                'source': args.source,
                'function_name': args.function_name,
                'description': args.description,
                'version': args.version,
                'operation_type': operation_type,  # New field to distinguish entity matchers
                'dependencies': args.dependencies.split(',') if args.dependencies else []
            }
        )
        
        if success:
            # Add to MatrixTransformer if it's a matrix-type transformation
            if args.data_type == 'matrix' and operation_type == 'transformation':
                success = transformer.add_transform(
                    matrix_type=args.name,
                    transform_rule=transform_rule,
                    properties=properties,
                    neighbors=neighbors
                )
        
        elapsed_time = time.time() - start_time
        
        if success:
            if operation_type == 'entity_matching':
                print(f"Entity matcher added: {args.name}")
                print(f"Matcher type: {args.data_type} entity matching")
            else:

                print(f"Transform added: {args.name}")
                print(f"Data type: {args.data_type}")
            
            print(f"Source: {args.source_type} - {args.source}")
            if properties:
                print(f"Properties: {properties}")
            if neighbors:
                print(f"Neighbors: {neighbors}")
            print(f"Registration time: {elapsed_time:.4f}s")
            
            # Show usage example
            print(f"\nUsage example:")
            if operation_type == 'entity_matching':
                print(f"   tensorpack traverse-graph --inputs *.csv --search-entity 'BRCA1' --generate-viz")
                print(f"   # Your custom entity matcher '{args.name}' will be automatically used!")
            elif args.data_type == 'matrix':
                print(f"   tensorpack transform input.npy --target-type {args.name} -o output.npy")
            else:
                print(f"   tensorpack transform-{args.data_type} input.json --transform {args.name} -o output.json")
            
            logging.info("Transformation successfully registered")
            return 0
        else:
            print(f"Failed to add transformation: {args.name}")
            return 1
        
    except Exception as e:
        logging.error(f"Error adding transformation: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def load_python_transform(file_path: str, function_name: str = None):
    """Load a Python transformation function from a file."""
    import importlib.util
    import os
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Python file not found: {file_path}")
    
    # Load the module
    spec = importlib.util.spec_from_file_location("custom_transform", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Defensive validation for function_name
    if function_name is None:
        function_name = 'transform'
    elif not isinstance(function_name, str):
        logging.warning(f"load_python_transform received non-string function_name: {type(function_name)}; defaulting to 'transform'")
        function_name = 'transform'

    # Get the transformation function
    if function_name:
        if not hasattr(module, function_name):
            raise AttributeError(f"Function {function_name} not found in {file_path}")
        transform_func = getattr(module, function_name)
    else:
        # Look for common function names
        common_names = ['transform', 'apply_transform', 'custom_transform', 'process']
        transform_func = None
        for name in common_names:
            if hasattr(module, name):
                transform_func = getattr(module, name)
                break
        
        if transform_func is None:
            raise AttributeError(f"No transformation function found in {file_path}. Expected one of: {common_names}")
    
    # Validate function signature
    import inspect
    sig = inspect.signature(transform_func)
    if len(sig.parameters) < 1:
        raise ValueError("Transformation function must accept at least one parameter (the input data)")
    
    return transform_func


def create_executable_wrapper(executable_path: str, data_type: str):
    """Create a wrapper function for external executable transformations."""
    import subprocess
    import tempfile
    import os
    
    if not os.path.exists(executable_path):
        raise FileNotFoundError(f"Executable not found: {executable_path}")
    
    def executable_transform(data, **kwargs):
        """Wrapper function that calls external executable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save input data
            input_file = os.path.join(temp_dir, f"input.{get_file_extension(data_type)}")
            save_to_file(data, input_file)
            
            # Prepare output file
            output_file = os.path.join(temp_dir, f"output.{get_file_extension(data_type)}")
            
            # Build command
            cmd = [executable_path, input_file, output_file]
            
            # Add kwargs as command line arguments
            for key, value in kwargs.items():
                cmd.extend([f"--{key}", str(value)])
            
            # Execute
            try:
                logging.debug(f"Running external executable command: {cmd}")
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                except Exception as ex:
                    logging.error(f"External command raised exception: {ex}")
                    raise
                if result.returncode != 0:
                    logging.error(f"Executable stdout: {result.stdout}")
                    logging.error(f"Executable stderr: {result.stderr}")
                    raise RuntimeError(f"Executable failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                raise RuntimeError("Executable timed out after 5 minutes")
            
            # Load result
            if not os.path.exists(output_file):
                raise RuntimeError("Executable did not produce output file")
            
            return load_tensor_from_file(output_file)
    
    return executable_transform


def parse_inline_transform(definition: str, data_type: str):
    """Parse an inline transformation definition."""
    try:
        import json
        config = json.loads(definition)
    except json.JSONDecodeError:
        # Try YAML if JSON fails
        try:
            import yaml
            config = yaml.safe_load(definition)
        except ImportError:
            raise ValueError("Inline definition must be valid JSON (or install PyYAML for YAML support)")
    
    # Extract transformation type and parameters
    transform_type = config.get('type', 'unknown')
    params = config.get('parameters', {})
    
    # Create transformation function based on type
    if transform_type == 'normalize':
        def normalize_transform(data, **kwargs):
            norm_type = params.get('norm', 'l2')
            if norm_type == 'l2':
                norm = np.linalg.norm(data)
                return data / (norm + 1e-8)
            elif norm_type == 'max':
                return data / (np.max(np.abs(data)) + 1e-8)
            else:
                return data
        return normalize_transform
    
    elif transform_type == 'scale':
        def scale_transform(data, **kwargs):
            factor = params.get('factor', 1.0)
            return data * factor
        return scale_transform
    
    elif transform_type == 'threshold':
        def threshold_transform(data, **kwargs):
            threshold = params.get('threshold', 0.0)
            return np.where(np.abs(data) > threshold, data, 0)
        return threshold_transform
    
    elif transform_type == 'custom_matrix':
        # For matrix-specific inline transformations
        operation = params.get('operation', 'identity')
        
        def custom_matrix_transform(data, **kwargs):
            if operation == 'transpose':
                return data.T
            elif operation == 'symmetrize':
                return (data + data.T) / 2
            elif operation == 'upper_triangle':
                return np.triu(data)
            elif operation == 'lower_triangle':
                return np.tril(data)
            else:
                return data
        return custom_matrix_transform
    
    else:
        raise ValueError(f"Unknown inline transformation type: {transform_type}")


def load_config_transform(config_path: str, data_type: str):
    """Load transformation from a configuration file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Ensure json is available for the final serialization step
    import json

    # Determine config format from extension
    ext = os.path.splitext(config_path)[1].lower()

    if ext == '.json':
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    elif ext in ['.yml', '.yaml']:
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except ImportError:
            raise ImportError("PyYAML required for YAML config files")
    else:
        raise ValueError(f"Unsupported config format: {ext}")

    # Use the inline parser with the loaded config
    return parse_inline_transform(json.dumps(config), data_type)


def get_file_extension(data_type: str) -> str:
    """Get appropriate file extension for data type."""
    extensions = {
        'matrix': 'npy',
        'json': 'json',
        'graph': 'json',
        'timeseries': 'csv',
        'image': 'npy',
        'audio': 'npy',
        'text': 'txt',
        'custom': 'npy'
    }
    return extensions.get(data_type, 'npy')


def add_transform_to_registry(name: str, data_type: str, transform_rule, 
                             properties: dict, neighbors: list, source_info: dict) -> bool:
    """Add transformation to the global registry."""
    import os
    import json
    import shutil
    import hashlib
    import platform
    import getpass
    from pathlib import Path

    # Ensure we have a source_info dict
    source_info = source_info or {}

    # Create registry directory and artifacts subdirectory
    registry_dir = Path.home() / '.tensorpack' / 'transforms' / data_type
    registry_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = registry_dir / 'artifacts'
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Prepare metadata with defaults
    metadata = {
        'name': name,
        'data_type': data_type,
        'properties': properties or {},
        'neighbors': neighbors or [],
        'source_info': dict(source_info),
        'created': time.strftime("%Y-%m-%d %H:%M:%S"),
        'version': str(source_info.get('version') or '1.0')
    }

    # Embedding controls
    embed = bool(metadata['source_info'].get('embed', False))
    embed_unrestricted = bool(metadata['source_info'].get('embed_unrestricted', False))
    try:
        embed_max_mb = float(metadata['source_info'].get('embed_max_mb', 10))
    except Exception:
        embed_max_mb = 10.0

    def _sha256_of_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open('rb') as fh:
            for chunk in iter(lambda: fh.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()

    def _record_provenance(src_path: Path, dest_path: Path, checksum: str):
        metadata['source_info'].update({
            'embedded': True,
            'embedded_filename': dest_path.name,
            'embedded_path': str(dest_path),
            'embedded_size_bytes': src_path.stat().st_size,
            'embedded_checksum_sha256': checksum,
            'embedded_platform': platform.platform(),
            'embedded_user': getpass.getuser(),
            'embedded_ts': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    # Default not embedded
    metadata['source_info'].setdefault('embedded', False)

    src_type = metadata['source_info'].get('type', 'python')
    src_value = metadata['source_info'].get('source')

    try:
        # Python sources: copy file if path provided, otherwise persist inline if embed requested
        if src_type == 'python':
            if isinstance(src_value, str) and os.path.exists(src_value):
                src_path = Path(src_value)
                dest = registry_dir / f"{name}{src_path.suffix or '.py'}"
                shutil.copy2(src_path, dest)
                checksum = _sha256_of_file(dest)
                _record_provenance(src_path, dest, checksum)
                logging.info(f"Copied python source to registry: {dest}")
            else:
                # Inline source code string
                if isinstance(src_value, str) and embed and ("\n" in src_value or 'def ' in src_value):
                    dest = artifacts_dir / f"{name}_inline.py"
                    with dest.open('w', encoding='utf-8') as f:
                        f.write(src_value)
                    checksum = _sha256_of_file(dest)
                    _record_provenance(dest, dest, checksum)
                    logging.info(f"Saved inline python source to artifacts: {dest}")

        else:
            # Non-python sources: executables, configs, binaries, etc.
            if isinstance(src_value, str) and os.path.exists(src_value):
                src_path = Path(src_value)
                size_bytes = src_path.stat().st_size
                size_mb = size_bytes / (1024.0 * 1024.0)
                if embed or embed_unrestricted:
                    if (size_mb > embed_max_mb) and not embed_unrestricted:
                        metadata['source_info'].update({
                            'embedded': False,
                            'embed_rejected_reason': f'size_exceeds_limit ({size_mb:.2f}MB > {embed_max_mb}MB)'
                        })
                        logging.warning(f"Embedding rejected for {src_path} - size {size_mb:.2f}MB exceeds {embed_max_mb}MB")
                    else:
                        dest = artifacts_dir / f"{name}_{src_path.name}"
                        shutil.copy2(src_path, dest)
                        checksum = _sha256_of_file(dest)
                        _record_provenance(src_path, dest, checksum)
                        logging.info(f"Embedded source into registry artifacts: {dest}")
                else:
                    # Not embedding; store original path metadata
                    metadata['source_info'].update({
                        'embedded': False,
                        'original_source_path': str(src_path),
                        'original_source_size_bytes': size_bytes
                    })
            else:
                # Inline non-file source: write it if embed requested
                if src_value and embed:
                    dest = artifacts_dir / f"{name}_source.txt"
                    with dest.open('w', encoding='utf-8') as f:
                        f.write(str(src_value))
                    checksum = _sha256_of_file(dest)
                    _record_provenance(dest, dest, checksum)
                    logging.info(f"Saved inline source to artifacts: {dest}")
                else:
                    metadata['source_info'].setdefault('embedded', False)

    except Exception as e:
        logging.error(f"Error while attempting to embed source for transform '{name}': {e}")
        metadata['source_info'].update({'embedded': False, 'embed_error': str(e)})

    # Persist metadata (including provenance if any)
    metadata_file = registry_dir / f"{name}_metadata.json"
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
    except Exception as e:
        logging.error(f"Failed to write metadata file {metadata_file}: {e}")
        return False

    logging.info(f"Transform registered in {registry_dir}")
    return True


def list_transforms_command(args: argparse.Namespace) -> int:
    """List available transformations."""
    setup_logging(args.verbose, args.log)
    
    try:
        registry_dir = Path.home() / '.tensorpack' / 'transforms'
        
        if not registry_dir.exists():
            print("No transformations registered yet.")
            return 0
        
        # Collect all transformations
        transforms = {}
        for data_type_dir in registry_dir.iterdir():
            if data_type_dir.is_dir():
                data_type = data_type_dir.name
                transforms[data_type] = []
                
                for metadata_file in data_type_dir.glob("*_metadata.json"):
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        transforms[data_type].append(metadata)
                    except Exception as e:
                        logging.warning(f"Could not read {metadata_file}: {e}")
        
        # Display transformations
        if args.data_type:
            # Show only specific data type
            if args.data_type in transforms:
                print(f"{args.data_type.upper()} Transformations:")
                for transform in transforms[args.data_type]:
                    print_transform_info(transform, detailed=args.detailed)
            else:
                print(f"No transformations found for data type: {args.data_type}")
        else:
            # Show all data types
            total_count = 0
            for data_type, transform_list in transforms.items():
                if transform_list:
                    print(f"\n{data_type.upper()} Transformations ({len(transform_list)}):")
                    for transform in transform_list:
                        print_transform_info(transform, detailed=args.detailed)
                    total_count += len(transform_list)
            
            print(f"\nTotal transformations: {total_count}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Error listing transformations: {e}")
        return 1


def print_transform_info(metadata: dict, detailed: bool = False):
    """Print information about a transformation."""
    name = metadata.get('name', 'Unknown')
    description = metadata.get('source_info', {}).get('description', 'No description')
    version = metadata.get('version', '1.0')
    
    print(f"  {name} (v{version})")
    if description != 'No description':
        print(f"     {description}")
    
    if detailed:
        properties = metadata.get('properties', {})
        neighbors = metadata.get('neighbors', [])
        source_info = metadata.get('source_info', {})
        
        if properties:
            print(f"     Properties: {properties}")
        if neighbors:
            print(f"     Neighbors: {', '.join(neighbors)}")
        print(f"     Source: {source_info.get('type', 'unknown')}")
        print(f"     Created: {metadata.get('created', 'Unknown')}")


def describe_transform_command(args: argparse.Namespace) -> int:
    """Describe a specific transformation in detail."""
    setup_logging(args.verbose, args.log)
    
    try:
        registry_dir = Path.home() / '.tensorpack' / 'transforms'
        
        # Search for the transformation
        found = False
        for data_type_dir in registry_dir.iterdir():
            if data_type_dir.is_dir():
                metadata_file = data_type_dir / f"{args.name}_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    print(f"Transformation: {metadata['name']}")
                    print(f"Data Type: {metadata['data_type']}")
                    print(f"Version: {metadata.get('version', '1.0')}")
                    print(f"Created: {metadata.get('created', 'Unknown')}")
                    
                    source_info = metadata.get('source_info', {})
                    print(f"Description: {source_info.get('description', 'No description')}")
                    print(f"Source Type: {source_info.get('type', 'unknown')}")
                    
                    properties = metadata.get('properties', {})
                    if properties:
                        print(f"Properties:")
                        for key, value in properties.items():
                            print(f"   {key}: {value}")
                    
                    neighbors = metadata.get('neighbors', [])
                    if neighbors:
                        print(f"Neighbors: {', '.join(neighbors)}")
                    
                    dependencies = source_info.get('dependencies', [])
                    if dependencies:
                        print(f"Dependencies: {', '.join(dependencies)}")
                    
                    # Show usage examples
                    print(f"\nUsage Examples:")
                    data_type = metadata['data_type']
                    if data_type == 'matrix':
                        print(f"   tensorpack transform input.npy --target-type {args.name} -o output.npy")
                    else:
                        print(f"   tensorpack transform-{data_type} input.json --transform {args.name} -o output.json")
                    
                    # Show source file if it's Python
                    if source_info.get('type') == 'python' and args.show_source:
                        source_file = data_type_dir / f"{args.name}.py"
                        if source_file.exists():
                            print(f"\nSource Code:")
                            with open(source_file, 'r') as f:
                                source_code = f.read()
                            print(f"```python\n{source_code}\n```")
                    
                    found = True
                    break
        
        if not found:
            print(f"Transformation '{args.name}' not found")
            return 1
        
        return 0
        
    except Exception as e:
        logging.error(f"Error describing transformation: {e}")
        return 1


def remove_transform_command(args: argparse.Namespace) -> int:
    """Remove a transformation from the registry."""
    setup_logging(args.verbose, args.log)
    
    # Check license for custom transformation management
    try:
        license_manager = LicenseManager()
        has_access, message = license_manager.check_feature_access('remove_transforms')
        if not has_access:
            print(f"License Error: {message}")
            print("\nRemoving custom transformations requires a premium license.")
            print("Upgrade for full access: tensorpack upgrade")
            return 1
    except Exception as e:
        logging.warning(f"License check failed: {e}. Proceeding with basic functionality.")
    
    try:
        registry_dir = Path.home() / '.tensorpack' / 'transforms'
        
        # Search for the transformation
        found = False
        for data_type_dir in registry_dir.iterdir():
            if data_type_dir.is_dir():
                metadata_file = data_type_dir / f"{args.name}_metadata.json"
                source_file = data_type_dir / f"{args.name}.py"
                
                if metadata_file.exists():
                    if not args.force:
                        # Confirm deletion
                        response = input(f"Are you sure you want to remove transformation '{args.name}'? [y/N]: ")
                        if response.lower() != 'y':
                            print("Operation cancelled.")
                            return 0
                    
                    # Remove files
                    metadata_file.unlink()
                    if source_file.exists():
                        source_file.unlink()
                    
                    print(f"Removed transformation: {args.name}")
                    found = True
                    break
        
        if not found:
            print(f"Transformation '{args.name}' not found")
            return 1
        
        return 0
        
    except Exception as e:
        logging.error(f"Error removing transformation: {e}")
        return 1







# combine_matrices_command removed

def get_complexity(matrix_type: str, shape: tuple) -> float:
    """Estimate the complexity of a matrix based on its type and shape."""
    base_complexity = np.prod(shape) if shape else 0
    
    # Apply type-specific complexity multipliers
    type_multipliers = {
        'sparse': 0.3,      # Sparse matrices are less complex
        'dense': 1.0,       # Dense matrices are baseline
        'symmetric': 0.7,   # Symmetric matrices have redundancy
        'triangular': 0.5,  # Triangular matrices have structure
        'diagonal': 0.1,    # Diagonal matrices are simple
        'orthogonal': 0.8,  # Orthogonal matrices have constraints
        'block': 0.6,       # Block matrices have structure
        'toeplitz': 0.4,    # Toeplitz matrices have patterns
        'circulant': 0.3,   # Circulant matrices are highly structured
    }
    
    multiplier = type_multipliers.get(matrix_type, 1.0)
    return float(base_complexity * multiplier)

def get_memory_efficiency(matrix_type: str) -> float:
    """Estimate the memory efficiency of a matrix type (0.0 to 1.0)."""
    efficiency_scores = {
        'sparse': 0.9,      # Very efficient for sparse data
        'diagonal': 0.95,   # Extremely efficient storage
        'triangular': 0.7,  # Good efficiency due to structure
        'symmetric': 0.7,   # Good efficiency due to symmetry
        'block': 0.6,       # Moderate efficiency
        'toeplitz': 0.8,    # Good efficiency due to pattern
        'circulant': 0.85,  # Very good efficiency
        'orthogonal': 0.5,  # Moderate efficiency
        'dense': 0.3,       # Low efficiency for large matrices
    }
    
    return efficiency_scores.get(matrix_type, 0.5)

def discover_connections_command(args: argparse.Namespace) -> int:
    """
    Handle comprehensive semantic connection discovery between matrices/tensors.
    
    This command creates a complete web of connections between all datasets,
    preserving contextual metadata and providing semantic interpretation
    of relationships. Unlike traverse_graph_command which explores specific 
    pathways, this provides a many-to-many simultaneous analysis of all
    possible connections with rich contextual understanding.
    """
    # Automatically configure optimal settings for this command
    configure_qvm(capacity_gb=100.0)  # Set QVM capacity to 100.0 GB
    configure_ocr(extract_on_load=True, video_processing=True)  # Enable OCR and video OCR
    
    setup_logging(args.verbose, args.log)
    logging.info(f"Discovering semantic connections between {len(args.inputs)} files")
    
    # Check license for advanced feature access
    try:
        license_manager = LicenseManager()
        has_access, message = license_manager.check_feature_access('discover_connections')
        if not has_access:
            print(f"License Error: {message}")
            print("\nTo access connection discovery features:")
            print("  • Free tier: 5 uses per day")
            print("  • Upgrade for unlimited access: tensorpack upgrade")
            return 1
        # Enforce max datasets
        max_ds = license_manager.get_max_datasets()
        if max_ds != float('inf') and len(args.inputs) > max_ds:
            print(f"License Error: Your license allows {max_ds} datasets; you requested {len(args.inputs)}.")
            print(license_manager.show_upgrade_info())
            return 2
        # Enforce export format allowance
        if getattr(args, 'export_formats', None):
            allowed = license_manager.get_allowed_export_formats()
            for fmt in args.export_formats:
                if fmt not in allowed and fmt != 'all':
                    print(f"License Error: Export format '{fmt}' not allowed by your license.")
                    print(license_manager.show_upgrade_info())
                    return 2
    except Exception as e:
        logging.warning(f"License check failed: {e}. Proceeding with basic functionality.")
    
    import numpy as np
    try:
        start_time = time.time()
        
        # Create MatrixTransformer instance
        transformer = MatrixTransformer()
        
        # Load input matrices/tensors with rich metadata preservation
        matrices = []
        dataset_info = []
        
        logging.info("Loading input files with contextual metadata...")
        if getattr(args, 'apply_transform', None):
            logging.info(f"Applying transform '{args.apply_transform}' to all input datasets")
        for i, input_file in enumerate(args.inputs):
            try:
                if hasattr(args, 'verbose') and args.verbose:
                    logging.debug(f"Loading dataset {i}: {input_file}")
                
                # Load with metadata preservation and optional transform application
                matrix = load_and_apply_transform(input_file, getattr(args, 'apply_transform', None))
                matrices.append(matrix)
                
                # Extract comprehensive dataset information
                data_type = _detect_data_type(input_file)
                matrix_type = transformer._detect_matrix_type(matrix)
                semantic_coords = transformer._generate_matrix_coordinates(matrix, i)
                
                # NEW: Extract and register entity information from the matrix
                metadata = _get_general_metadata(matrix)
                key_entities = _extract_key_entities_from_dataset(matrix, metadata)
                
                # Register extracted entities with the global registry
                for entity in key_entities[:20]:  # Limit to top 20 entities
                    if entity and len(str(entity).strip()) > 1:
                        entity_id = f"{os.path.basename(input_file)}_{str(entity).lower().replace(' ', '_')}"
                        entity_info = {
                            'type': 'extracted_entity',
                            'name': str(entity),
                            'source_file': input_file,
                            'source_index': i,
                            'extraction_method': 'key_entity_extraction'
                        }
                        # Force matrix linkage without coordinates - important for connection discovery
                        result = _register_entity(entity_id, entity_info, matrix)
                        logging.debug(f"Entity registration result for {entity_id}: {result}")
                
                # Get existing registered entities for this matrix
                matrix_entities = _get_entities_in_matrix(matrix)
                entity_summary = {}
                if matrix_entities or key_entities:
                    total_entities = len(matrix_entities) + len(key_entities)
                    logging.debug(f"Found {total_entities} entities in {input_file} ({len(matrix_entities)} registered + {len(key_entities)} extracted)")
                    entity_summary = {
                        'entity_count': total_entities,
                        'entity_ids': list(matrix_entities.keys()) + [f"{os.path.basename(input_file)}_{str(e).lower().replace(' ', '_')}" for e in key_entities[:20]],
                        'entity_types': [entity_data['info'].get('type', 'unknown') 
                                       for entity_data in matrix_entities.values()] + ['extracted_entity'] * len(key_entities[:20]),
                        'key_entities': key_entities[:20]  # Store the actual extracted entities
                    }
                
                # Build rich dataset info with enhanced contextual metadata
                info = {
                    'file_info': {
                        'file_path': input_file,
                        'file_name': os.path.basename(input_file),
                        'index': i,
                        'shape': matrix.shape,
                        'data_type': data_type,
                        'matrix_type': matrix_type,
                        'semantic_coords': semantic_coords.tolist() if isinstance(semantic_coords, np.ndarray) else semantic_coords,
                        'entity_summary': entity_summary  # NEW: Add entity information
                    }
                }
                
                # Extract enhanced contextual information
                metadata = _get_general_metadata(matrix)
                info['contextual_info'] = _extract_contextual_info(metadata, None)
                info['semantic_interpretation'] = _interpret_semantic_coordinates(
                    semantic_coords, info['file_info'], metadata
                )
                info['matrix_analysis'] = {
                    'matrix_type': matrix_type,
                    'data_type': data_type,
                    'shape': matrix.shape,
                    'complexity_estimate': get_complexity(matrix_type, matrix.shape),
                    'memory_efficiency': get_memory_efficiency(matrix_type)
                }
                
                dataset_info.append(info)
                
                if hasattr(args, 'verbose') and args.verbose:
                    logging.debug(f"Dataset {i} info: {info}")
                
                logging.info(f"Loaded {os.path.basename(input_file)} with shape {matrix.shape}, type: {matrix_type}")
                
            except Exception as e:
                logging.error(f"Failed to load {input_file}: {str(e)}")
                if not args.skip_errors:
                    return 1
        
        if not matrices:
            logging.error("No valid matrices were loaded")
            return 1
        
        # Store matrices in transformer
        transformer.matrices = matrices

        # Optionally save companion .npy files for each loaded matrix
        if getattr(args, 'save_npy', False):
            logging.info("--save-npy enabled: saving companion .npy files for each input")
            for idx, mat in enumerate(matrices):
                try:
                    base = os.path.splitext(os.path.basename(args.inputs[idx]))[0]
                    out_np = f"{base}.npy"
                    save_to_file(mat, out_np)
                    # write a minimal metadata JSON pointing to the companion binary
                    meta = {
                        'canonical_binary': out_np,
                        'shape': mat.shape,
                        'dtype': str(mat.dtype),
                        'source': args.inputs[idx]
                    }
                    meta_path = f"{base}_metadata.json"
                    with open(meta_path, 'w', encoding='utf-8') as mf:
                        json.dump(meta, mf, indent=2)
                    logging.info(f"Saved companion binary and metadata: {out_np}, {meta_path}")
                except Exception as e:
                    logging.error(f"Failed saving companion for {args.inputs[idx]}: {e}")
        
        # Run comprehensive semantic connection discovery
        logging.info(f"Finding semantic connections in {args.num_dims}D space...")
        
        # Generate hyperdimensional connections with mathematical analysis
        mathematical_connections = transformer.find_hyperdimensional_connections(num_dims=args.num_dims)
        
        # NEW: Find entity-based connections
        logging.info("Finding entity-based connections...")
        entity_connections = _find_entity_based_connections(dataset_info, matrices)
        if entity_connections:
            entity_count = sum(len(conns) for conns in entity_connections.values())
            logging.info(f"Found {entity_count} entity-based connections")
        
        # Enhance connections with semantic analysis for each pair
        semantic_connections = {}
        contextual_bridges = {}
        
        for src_idx in range(len(matrices)):
            semantic_connections[src_idx] = []
            
            for tgt_idx in range(len(matrices)):
                if src_idx != tgt_idx:
                    if hasattr(args, 'verbose') and args.verbose:
                        logging.debug(f"Analyzing semantic connection: {dataset_info[src_idx]['file_info']['file_name']} → {dataset_info[tgt_idx]['file_info']['file_name']}")
                    
                    # Find semantic connections between datasets
                    semantic_links = _find_semantic_connections_between_datasets(
                        matrices[src_idx], matrices[tgt_idx], 
                        dataset_info[src_idx], dataset_info[tgt_idx]
                    )
                    print(f"DEBUG: semantic_links for {dataset_info[src_idx]['file_info']['file_name']} -> {dataset_info[tgt_idx]['file_info']['file_name']}: {len(semantic_links)} items")
                    
                    # Find contextual bridges
                    metadata_src = _get_general_metadata(matrices[src_idx])
                    metadata_tgt = _get_general_metadata(matrices[tgt_idx])
                    bridges = _find_contextual_bridges(metadata_src, metadata_tgt)
                    
                    # Get mathematical connection strength
                    math_strength = 0.0
                    if src_idx in mathematical_connections:
                        for target in mathematical_connections[src_idx]:
                            if target['target_idx'] == tgt_idx:
                                math_strength = target['strength']
                                break
                    
                    # Check for entity-based connections
                    entity_based_connections = []
                    if src_idx in entity_connections:
                        for entity_conn in entity_connections[src_idx]:
                            if entity_conn['target_idx'] == tgt_idx:
                                entity_based_connections.append(entity_conn)

                    # Defensive normalization and verbose diagnostics
                    if not isinstance(semantic_links, list):
                        # Some helper functions may return dicts or error markers
                        if isinstance(semantic_links, dict) and semantic_links.get('error'):
                            logging.debug(f"Semantic link lookup returned error for {src_idx}->{tgt_idx}: {semantic_links.get('error')}")
                            semantic_links = []
                        else:
                            try:
                                semantic_links = list(semantic_links) if semantic_links is not None else []
                            except Exception:
                                semantic_links = []

                    if not isinstance(bridges, list):
                        try:
                            bridges = list(bridges) if bridges is not None else []
                        except Exception:
                            bridges = []

                    # Attempt to get semantic coords safely
                    source_coords = None
                    target_coords = None
                    semantic_distance = 1.0
                    try:
                        # Some dataset_info entries nest coords under 'file_info' or 'semantic_coords'
                        src_info = dataset_info[src_idx]
                        tgt_info = dataset_info[tgt_idx]
                        source_coords = src_info.get('file_info', {}).get('semantic_coords') if isinstance(src_info, dict) else None
                        target_coords = tgt_info.get('file_info', {}).get('semantic_coords') if isinstance(tgt_info, dict) else None
                    except Exception:
                        source_coords = None
                        target_coords = None

                    try:
                        if source_coords is None:
                            source_coords = dataset_info[src_idx].get('semantic_coords') if isinstance(dataset_info[src_idx], dict) else None
                        if target_coords is None:
                            target_coords = dataset_info[tgt_idx].get('semantic_coords') if isinstance(dataset_info[tgt_idx], dict) else None
                    except Exception:
                        pass

                    # Compute semantic_distance fallback if not set
                    try:
                        if source_coords is not None and target_coords is not None:
                            # If coords are numpy arrays, compute simple Euclidean; else attempt float cast
                            import numpy as _np
                            sc = _np.asarray(source_coords)
                            tc = _np.asarray(target_coords)
                            if sc.size and tc.size:
                                semantic_distance = float(_np.linalg.norm(sc - tc) / (1.0 + _np.linalg.norm(sc) + _np.linalg.norm(tc)))
                                semantic_distance = max(0.0, min(1.0, semantic_distance))
                    except Exception:
                        semantic_distance = 1.0

                    if hasattr(args, 'verbose') and args.verbose:
                        logging.debug(
                            f"Pair diagnostics {dataset_info[src_idx]['file_info']['file_name']} -> {dataset_info[tgt_idx]['file_info']['file_name']}: "
                            f"math_strength={math_strength:.4f}, semantic_links={len(semantic_links)}, bridges={len(bridges)}, "
                            f"entity_based={len(entity_based_connections)}, semantic_distance={semantic_distance:.4f}"
                        )
                    
                    # Simple fallback: if no semantic links found, add a basic one to enable connections
                    if not semantic_links:
                        semantic_links = [{'connection_type': 'basic_fallback', 'strength': 0.05, 'description': 'Basic connection for testing'}]
                    
                    # Combine mathematical and semantic analysis with rich contextual understanding
                    if semantic_links or bridges or math_strength >= args.threshold or entity_based_connections:
                        # Extract source and target metadata for context analysis
                        source_metadata = _get_general_metadata(matrices[src_idx])
                        target_metadata = _get_general_metadata(matrices[tgt_idx])
                        
                        # Get source and target coordinates
                        source_coords = dataset_info[src_idx]['file_info']['semantic_coords']
                        target_coords = dataset_info[tgt_idx]['file_info']['semantic_coords']
                        
                        # Calculate semantic distance and compatibility
                        semantic_distance = _calculate_semantic_distance(source_coords, target_coords)
                        semantic_compatibility = 1.0 - min(1.0, semantic_distance)
                        
                        # Find local contextual relationships using actual entities from the datasets
                        source_key_entities = dataset_info[src_idx]['file_info']['entity_summary'].get('key_entities', [])
                        target_key_entities = dataset_info[tgt_idx]['file_info']['entity_summary'].get('key_entities', [])
                        
                        # Use the first available entity, or fallback to generic analysis
                        source_search_entity = source_key_entities[0] if source_key_entities else "general_analysis"
                        target_search_entity = target_key_entities[0] if target_key_entities else "general_analysis"
                        
                        source_local_relationships = _find_local_contextual_relationships(
                            matrices[src_idx],
                            source_search_entity, 
                            source_metadata,
                            dataset_info[src_idx]['file_info']
                        )
                        
                        target_local_relationships = _find_local_contextual_relationships(
                            matrices[tgt_idx],
                            target_search_entity,
                            target_metadata,
                            dataset_info[tgt_idx]['file_info']
                        )
                        
                        # Find entity overlaps (if available)
                        entity_overlaps = []
                        cross_entity_matches = []
                        
                        # Combine all contextual analysis into enhanced connection data
                        connection_data = {
                            'target_idx': tgt_idx,
                            'target_name': dataset_info[tgt_idx]['file_info']['file_name'],
                            'mathematical_strength': math_strength,
                            'semantic_connections': semantic_links,
                            'contextual_bridges': bridges,
                            'entity_connections': entity_based_connections,  # NEW: Add entity connections
                            'semantic_coordinates': {
                                'source': source_coords.tolist() if hasattr(source_coords, 'tolist') else source_coords,
                                'target': target_coords.tolist() if hasattr(target_coords, 'tolist') else target_coords,
                                'distance': semantic_distance
                            },
                            'data_type_compatibility': {
                                'source_type': dataset_info[src_idx]['file_info']['data_type'],
                                'target_type': dataset_info[tgt_idx]['file_info']['data_type'],
                                'compatible': dataset_info[src_idx]['file_info']['data_type'] == 
                                             dataset_info[tgt_idx]['file_info']['data_type']
                            },
                            'contextual_analysis': {
                                'semantic_compatibility': float(semantic_compatibility),
                                'source_context': dataset_info[src_idx]['contextual_info'],
                                'target_context': dataset_info[tgt_idx]['contextual_info'],
                                'local_relationships': {
                                    'source': source_local_relationships,
                                    'target': target_local_relationships
                                },
                                'interpretation': {
                                    'connection_meaning': _interpret_connection_meaning(
                                        dataset_info[src_idx]['file_info'], dataset_info[tgt_idx]['file_info'], 
                                        bridges, semantic_links, semantic_compatibility
                                    ),
                                    'data_flow_potential': _assess_data_flow_potential(
                                        dataset_info[src_idx]['file_info'], dataset_info[tgt_idx]['file_info']
                                    )
                                }
                            }
                        }
                        semantic_connections[src_idx].append(connection_data)
        
        # Filter connections by threshold and prepare enhanced output
        filtered_connections = {}
        for src_idx, connections_list in semantic_connections.items():
            strong_connections = []
            for connection in connections_list:
                # Calculate combined relevance score
                relevance_score = (
                    connection['mathematical_strength'] * 0.4 +
                    len(connection['semantic_connections']) * 0.1 +
                    len(connection['contextual_bridges']) * 0.2 +
                    (1.0 - connection['semantic_coordinates']['distance']) * 0.3
                )
                # Verbose debug: breakdown of relevance components
                if hasattr(args, 'verbose') and args.verbose:
                    logging.debug(
                        f"Relevance breakdown for {dataset_info[src_idx]['file_info']['file_name']} -> {connection['target_name']}: "
                        f"math={connection['mathematical_strength']:.3f}, "
                        f"semantic_links={len(connection['semantic_connections'])}, "
                        f"bridges={len(connection['contextual_bridges'])}, "
                        f"distance_comp={(1.0 - connection['semantic_coordinates']['distance']):.3f}, "
                        f"total={relevance_score:.3f}, threshold={args.threshold}"
                    )
                
                if relevance_score >= args.threshold:
                    connection['relevance_score'] = relevance_score
                    if len(strong_connections) < args.max_connections:
                        strong_connections.append(connection)
            
            if strong_connections:
                # Sort by relevance score
                strong_connections.sort(key=lambda x: x['relevance_score'], reverse=True)
                filtered_connections[src_idx] = strong_connections
        
        # Generate semantic interpretations for all datasets
        interpreted_coordinates = {}
        for idx, info in enumerate(dataset_info):
            metadata = _get_general_metadata(matrices[idx])
            interpreted_coordinates[idx] = _interpret_semantic_coordinates(
                info['file_info']['semantic_coords'], info, metadata
            )
        
        # Prepare comprehensive output data
        connection_data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'analysis_type': 'semantic_connection_discovery',
            'num_dimensions': args.num_dims,
            'threshold': args.threshold,
            'total_matrices': len(matrices),
            'connected_matrices': len(filtered_connections),
            'applied_transform': getattr(args, 'apply_transform', None),
            'transform_metadata': _get_transform_metadata(args.inputs) if getattr(args, 'apply_transform', None) else None,
            'dataset_info': {
                idx: {
                    'file_info': dataset_info[idx]['file_info'],
                    'contextual_info': dataset_info[idx]['contextual_info'],
                    'semantic_interpretation': interpreted_coordinates[idx],
                    'matrix_analysis': {
                        'matrix_type': dataset_info[idx]['file_info']['matrix_type'],
                        'data_type': dataset_info[idx]['file_info']['data_type'],
                        'shape': dataset_info[idx]['file_info']['shape'],
                        'complexity_estimate': get_complexity(dataset_info[idx]['file_info']['matrix_type'], dataset_info[idx]['file_info']['shape']),
                        'memory_efficiency': get_memory_efficiency(dataset_info[idx]['file_info']['matrix_type'])
                    }
                } for idx in range(len(dataset_info))
            },
            'semantic_connections': filtered_connections,
            'connection_summary': {
                'total_connections': sum(len(targets) for targets in filtered_connections.values()),
                'connection_types': _analyze_connection_types(filtered_connections),
                'domain_clusters': _identify_domain_clusters(dataset_info, filtered_connections)
            }
        }
        
        # Apply enhanced clustering with semantic awareness if requested (need >=3 datasets)
        if args.clustering and len(args.inputs) < 3:
            logging.info("Not enough datasets for clustering (need >=3); skipping clustering step")
            args.clustering = None

        if args.clustering:
            logging.info(f"Performing semantic-aware {args.clustering} clustering...")
            
            try:
                # Use enhanced semantic clustering
                clustering_method = 'enhanced_hierarchical' if args.clustering in ['hierarchical', 'auto'] else 'enhanced_kmeans'
                clustering_result = _cluster_with_semantic_analysis(
                    matrices, filtered_connections, dataset_info, method=clustering_method
                )
                
                if clustering_result and 'semantic_clusters' in clustering_result:
                    connection_data['clustering'] = clustering_result
                    logging.info(f"Semantic clustering completed: {len(clustering_result['semantic_clusters'])} clusters formed")
                    
                    # Log cluster quality metrics
                    quality = clustering_result['cluster_quality']
                    logging.info(f"  Average cluster purity: {quality['average_purity']:.3f}")
                    logging.info(f"  Cross-domain clusters: {quality['cross_domain_clusters']}")
                else:
                    logging.warning("Semantic clustering produced no results")
                    
            except Exception as e:
                logging.error(f"Clustering failed: {str(e)}")
                connection_data['clustering'] = {'error': str(e)}
        
        # Save connection data
        # Ensure we have an output file if export formats are specified
        if not args.output and hasattr(args, 'export_formats') and args.export_formats:
            args.output = 'connection_results.json'
            logging.info(f"No output file specified, using default: {args.output}")
        
        if args.output:
            output_dir = os.path.dirname(args.output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            # Save primary JSON output
            save_to_file(connection_data, args.output, 'json')
            logging.info(f"Saved connection data to {args.output}")
            
            # Generate additional export formats using convertto.py capabilities
            if hasattr(args, 'export_formats') and args.export_formats and args.export_formats != ['json']:
                try:
                    # Prefer importing the compiled `tensorpack.convertto` module if present
                    import importlib
                    import importlib.util

                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    convertto_path = os.path.join(script_dir, 'convertto.py')

                    convertto = None
                    # Try package-qualified import first (will find .so built as tensorpack.convertto)
                    try:
                        convertto = importlib.import_module('tensorpack.convertto')
                        logging.info('Using compiled module tensorpack.convertto for additional exports')
                        try:
                            mod_file = getattr(convertto, '__file__', None)
                            logging.info(f"convertto module file: {mod_file}")
                            logging.info(f"convertto has run_conversion: {hasattr(convertto, 'run_conversion')}, has main: {hasattr(convertto, 'main')}")
                        except Exception:
                            logging.debug('Failed to introspect convertto module', exc_info=True)
                        # If the imported module exposes a programmatic API, call it with in-memory data
                        try:
                            if hasattr(convertto, 'run_conversion'):
                                try:
                                    # Create a modified version of connection_data without NumPy arrays
                                    # This is to avoid NumPy array truth value errors
                                    import json
                                    sanitized_data = json.loads(json.dumps(connection_data, default=str))
                                    convertto.run_conversion(sanitized_data)
                                except Exception as e:
                                    logging.warning(f"convertto.run_conversion raised during package import: {e}")
                            elif hasattr(convertto, 'main'):
                                try:
                                    # Save connection_data to results.json first to ensure main() can find it
                                    import json
                                    with open('results.json', 'w') as f:
                                        json.dump(connection_data, f, default=str)
                                    # main() may expect argv; call it to allow export generation
                                    convertto.main()
                                except Exception as e:
                                    logging.warning(f"convertto.main() raised during package import: {e}")
                        except Exception:
                            logging.debug('Failed to invoke entrypoint on imported tensorpack.convertto', exc_info=True)
                    except Exception:
                        convertto = None

                    # If compiled module not available, fall back to convertto.py file
                    if convertto is None and os.path.exists(convertto_path):
                        # License gating for additional export formats
                        try:
                            lm = LicenseManager()
                            ok_export, msg_export = lm.check_feature_access('export_formats')
                            if not ok_export and getattr(args, 'export_formats', None):
                                print(f"License Error: {msg_export}")
                                print("Additional export formats are not permitted for your license tier.")
                                logging.info("Skipping additional export generation due to license restrictions")
                                # Skip running convertto by not executing the module loader
                                raise PermissionError(msg_export)
                        except PermissionError:
                            raise
                        except Exception as e:
                            logging.debug(f"Export format license check failed: {e}")
                        # Temporarily write connection_data to results.json for convertto.py to process
                        temp_results_json = os.path.join(script_dir, 'results.json')
                        backup_results = None
                        
                        # Backup existing results.json if it exists
                        if os.path.exists(temp_results_json):
                            backup_results = temp_results_json + '.backup'
                            os.rename(temp_results_json, backup_results)
                        
                        try:
                            # Write our connection data as results.json with numpy type conversion
                            with open(temp_results_json, 'w', encoding='utf-8') as f:
                                json.dump(convert_numpy_types(connection_data), f, indent=2, ensure_ascii=False)
                            
                            # Import and execute convertto.py functions from source file
                            spec = importlib.util.spec_from_file_location("convertto", convertto_path)
                            convertto = importlib.util.module_from_spec(spec)

                            # Save current working directory and change to script directory
                            original_cwd = os.getcwd()
                            os.chdir(script_dir)

                            try:
                                spec.loader.exec_module(convertto)
                                # Attempt to run the conversion function directly if available.
                                try:
                                    if hasattr(convertto, 'run_conversion'):
                                        # Pass the in-memory connection_data to avoid relying on file-based side effects
                                        try:
                                            convertto.run_conversion(connection_data)
                                        except Exception as e:
                                            logging.warning(f"convertto.run_conversion raised: {e}")
                                    elif hasattr(convertto, 'main'):
                                        # Fallback to main() which will read the temp results.json written above
                                        try:
                                            convertto.main()
                                        except Exception as e:
                                            logging.warning(f"convertto.main() raised: {e}")
                                    else:
                                        logging.warning("Imported convertto module has no 'run_conversion' or 'main' entrypoints; no exports created")
                                except Exception:
                                    logging.debug("Failed to invoke convertto entrypoint", exc_info=True)
                                logging.info("Generated additional export formats using convertto.py")
                                
                                # List generated files
                                export_files = []
                                if 'all' in args.export_formats or 'csv' in args.export_formats:
                                    if os.path.exists('results.csv'):
                                        export_files.append('results.csv')
                                if 'all' in args.export_formats or 'xlsx' in args.export_formats:
                                    if os.path.exists('results.xlsx'):
                                        export_files.append('results.xlsx')
                                if 'all' in args.export_formats or 'html' in args.export_formats:
                                    if os.path.exists('results.html'):
                                        export_files.append('results.html')
                                if 'all' in args.export_formats or 'sqlite' in args.export_formats:
                                    if os.path.exists('exports/results.db'):
                                        export_files.append('exports/results.db')
                                
                                if export_files:
                                    logging.info(f"Additional exports created: {', '.join(export_files)}")
                                else:
                                    logging.warning("No additional export files were detected")
                                    
                            finally:
                                # Restore original working directory
                                os.chdir(original_cwd)
                            
                        finally:
                            # Cleanup: remove temp results.json and restore backup if it existed
                            if os.path.exists(temp_results_json):
                                os.remove(temp_results_json)
                            if backup_results and os.path.exists(backup_results):
                                os.rename(backup_results, temp_results_json)
                                
                    elif convertto is None:
                        logging.warning(f"convertto module/file not found (neither compiled tensorpack.convertto nor {convertto_path}); skipping additional exports")
                        
                except Exception as e:
                    logging.error(f"Failed to generate additional export formats: {str(e)}")
                    if hasattr(args, 'verbose') and args.verbose:
                        import traceback
                        logging.debug(traceback.format_exc())
        
        # Generate advanced visualizations
        if args.visualize:
            # License gating for visualizations
            try:
                lm = LicenseManager()
                ok_vis, msg_vis = lm.check_feature_access('visualizations')
                if not ok_vis:
                    print(f"License Error: {msg_vis}")
                    print("Advanced visualizations require an upgraded license. Use 'tensorpack upgrade' to learn more.")
                    logging.info("Skipping visualization due to license restrictions")
                    args.visualize = None
            except Exception as e:
                logging.debug(f"Visualization license check failed: {e}")
            # args.visualize may be a boolean flag (True) or a path string. Coerce to a directory path.
            if isinstance(args.visualize, bool):
                vis_dir = 'visualizations'
            else:
                vis_dir = str(args.visualize) if args.visualize else None

            if vis_dir:
                os.makedirs(vis_dir, exist_ok=True)
            else:
                logging.debug('Visualization requested but no directory provided; skipping visualization setup')
            
            try:
                import matplotlib.pyplot as plt
                import seaborn as sns
                from sklearn.manifold import TSNE
                from scipy.cluster.hierarchy import dendrogram, linkage
                import numpy as np
                
                # Create list of file names for visualization
                file_names = [info['file_info']['file_name'] for info in dataset_info]
                
                # Verify that filtered_connections has the expected structure
                if not filtered_connections:
                    raise ValueError("No connections found that meet the threshold criteria")
                    
                # Check the structure of one connection to ensure it has the required fields
                if filtered_connections:
                    sample_src = list(filtered_connections.keys())[0]
                    if filtered_connections[sample_src]:
                        sample_connection = filtered_connections[sample_src][0]
                        required_fields = ['target_idx', 'relevance_score']
                        missing_fields = [field for field in required_fields if field not in sample_connection]
                        if missing_fields:
                            raise ValueError(f"Connection data is missing required fields: {missing_fields}")
                
                # 1. Connection Strength Matrix (Heatmap)
                # Rows = datasets, Columns = datasets
                # Cells colored by connection strength score (0 → weak, 1 → strong)
                # Lets users instantly see clusters and outliers
                matrix_size = len(matrices)
                connection_matrix = np.zeros((matrix_size, matrix_size))
                
                for src_idx, targets in filtered_connections.items():
                    for target in targets:
                        tgt_idx = target['target_idx']
                        connection_matrix[src_idx, tgt_idx] = target['relevance_score']
                        connection_matrix[tgt_idx, src_idx] = target['relevance_score']  # Make symmetric
                
                plt.figure(figsize=(12, 10))
                mask = connection_matrix == 0  # Mask zero values for better visualization
                sns.heatmap(connection_matrix, 
                           annot=True, 
                           fmt='.2f',
                           cmap='YlOrRd', 
                           mask=mask,
                           xticklabels=[f.split('.')[0][:15] for f in file_names],
                           yticklabels=[f.split('.')[0][:15] for f in file_names],
                           cbar_kws={'label': 'Connection Strength'})
                plt.title('Connection Strength Matrix (Heatmap)\nRows = datasets, Columns = datasets', fontsize=14)
                plt.xlabel('Target Datasets', fontsize=12)
                plt.ylabel('Source Datasets', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.yticks(rotation=0)
                plt.tight_layout()
                plt.savefig(os.path.join(args.visualize, 'connection_strength_heatmap.png'), dpi=300, bbox_inches='tight')
                plt.close()
                
                # 2. Dataset Clustering Dendrogram
                # Hierarchical clustering tree of datasets based on connection strength
                # Shows natural grouping into "families" of related datasets
                # Use connection matrix as distance matrix (invert for similarity)
                if matrix_size > 1:
                    # Normalize connection matrix to [0, 1] range to avoid negative distances
                    max_connection = np.max(connection_matrix)
                    if max_connection > 0:
                        normalized_matrix = connection_matrix / max_connection
                    else:
                        # If no connections, create a small identity-like matrix for clustering
                        normalized_matrix = np.eye(matrix_size) * 0.1
                    
                    # Create distance matrix (1 - normalized_similarity for clustering)
                    distance_matrix = 1 - normalized_matrix
                    # Ensure all distances are non-negative
                    distance_matrix = np.maximum(distance_matrix, 0)
                    # Fill diagonal with zeros (distance from dataset to itself)
                    np.fill_diagonal(distance_matrix, 0)
                    
                    # Ensure the matrix is symmetric for proper distance matrix
                    distance_matrix = (distance_matrix + distance_matrix.T) / 2
                    
                    # Check if we have meaningful distances for clustering
                    if np.max(distance_matrix) > 0:
                        # Convert to condensed form for linkage (upper triangle)
                        from scipy.spatial.distance import squareform
                        condensed_distances = squareform(distance_matrix)
                        
                        # Perform hierarchical clustering
                        linkage_matrix = linkage(condensed_distances, method='ward')
                        
                        plt.figure(figsize=(15, 8))
                        dendrogram(linkage_matrix, 
                                  labels=[f.split('.')[0][:20] for f in file_names],
                                  leaf_rotation=45,
                                  leaf_font_size=10)
                        plt.title('Dataset Clustering Dendrogram\nHierarchical clustering tree based on connection strength', fontsize=14)
                        plt.xlabel('Datasets', fontsize=12)
                        plt.ylabel('Distance (1 - Normalized Connection Strength)', fontsize=12)
                        plt.tight_layout()
                        plt.savefig(os.path.join(args.visualize, 'clustering_dendrogram.png'), dpi=300, bbox_inches='tight')
                        plt.close()
                    else:
                        # Create a message plot if no meaningful clustering can be done
                        plt.figure(figsize=(15, 8))
                        plt.text(0.5, 0.5, 'No meaningful connections found for clustering\nAll datasets appear to be disconnected', 
                                horizontalalignment='center', verticalalignment='center', fontsize=16)
                        plt.title('Dataset Clustering Dendrogram\n(No connections found)', fontsize=14)
                        plt.axis('off')
                        plt.tight_layout()
                        plt.savefig(os.path.join(args.visualize, 'clustering_dendrogram.png'), dpi=300, bbox_inches='tight')
                        plt.close()
                
                # 3. t-SNE Plot
                # Projects the 8–16D hyperdimensional space into 2D scatter plot
                # Datasets that are close = stronger similarity
                # Gives an intuitive geometry of relationships
                
                # Get coordinates for all matrices
                all_coords = []
                for idx, matrix in enumerate(matrices):
                    try:
                        coord = transformer._generate_matrix_coordinates(matrix, idx)
                        # Ensure it's a numpy array
                        if isinstance(coord, list):
                            coord = np.array(coord)
                        all_coords.append(coord)
                    except Exception as e:
                        logging.warning(f"Failed to generate coordinates for matrix {idx}: {e}")
                        all_coords.append(np.ones(args.num_dims) * 0.5)
                
                # Convert to numpy array
                all_coords = np.array([np.array(coord) for coord in all_coords])
                
                # Validate coordinates before t-SNE
                if all_coords.shape[0] >= 2:
                    # Adjust perplexity based on number of samples (must be < n_samples)
                    n_samples = all_coords.shape[0]
                    perplexity = min(30, max(1, n_samples - 1))
                    
                    # Run t-SNE
                    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity, 
                               n_iter=1000, learning_rate='auto')
                    coords_2d = tsne.fit_transform(all_coords)
                    
                    plt.figure(figsize=(12, 10))
                    
                    # Color points by connection strength (average outgoing connections)
                    avg_strength = []
                    for idx in range(len(file_names)):
                        if idx in filtered_connections and filtered_connections[idx]:
                            avg = np.mean([conn['relevance_score'] for conn in filtered_connections[idx]])
                        else:
                            avg = 0.0
                        avg_strength.append(avg)
                    
                    scatter = plt.scatter(coords_2d[:, 0], coords_2d[:, 1], 
                                        c=avg_strength, 
                                        cmap='viridis',
                                        s=100,
                                        alpha=0.7,
                                        edgecolors='black',
                                        linewidth=0.5)
                    
                    # Add labels for each point
                    for idx, coord in enumerate(coords_2d):
                        plt.annotate(os.path.splitext(file_names[idx])[0][:15], 
                                   (coord[0], coord[1]), 
                                   textcoords="offset points",
                                   xytext=(5, 5),
                                   ha='left',
                                   fontsize=9,
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))
                    
                    plt.colorbar(scatter, label='Average Connection Strength')
                    plt.title('t-SNE Visualization of Dataset Relationships\nProjects 8-16D hyperdimensional space into 2D\nDatasets that are close = stronger similarity', fontsize=14)
                    plt.xlabel('t-SNE Dimension 1', fontsize=12)
                    plt.ylabel('t-SNE Dimension 2', fontsize=12)
                    plt.grid(True, alpha=0.3)
                    plt.tight_layout()
                    plt.savefig(os.path.join(args.visualize, 'tsne_relationships.png'), dpi=300, bbox_inches='tight')
                    plt.close()
                
                # If clustering was performed, also visualize clusters in t-SNE space
                if 'clustering' in connection_data and 'semantic_clusters' in connection_data['clustering'] and all_coords.shape[0] >= 2:
                    plt.figure(figsize=(12, 10))
                    
                    # Plot clusters with different colors
                    clusters = connection_data['clustering']['semantic_clusters']
                    cluster_colors = plt.cm.tab10(np.linspace(0, 1, len(clusters)))
                    
                    for cluster_id, cluster_info in clusters.items():
                        cluster_indices = cluster_info['members']  # Use members list
                        cluster_coords = coords_2d[cluster_indices]
                        plt.scatter(cluster_coords[:, 0], cluster_coords[:, 1], 
                                  c=[cluster_colors[int(cluster_id) % 10]], 
                                  label=f'Cluster {cluster_id} ({len(cluster_indices)} datasets)',
                                  s=100,
                                  alpha=0.7,
                                  edgecolors='black',
                                  linewidth=0.5)
                    
                    # Add labels for each point
                    for idx, coord in enumerate(coords_2d):
                        plt.annotate(os.path.splitext(file_names[idx])[0][:15], 
                                   (coord[0], coord[1]), 
                                   textcoords="offset points",
                                   xytext=(5, 5),
                                   ha='left',
                                   fontsize=9,
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))
                    
                    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                    plt.title('t-SNE Visualization with Semantic Clusters\nColored by cluster membership', fontsize=14)
                    plt.xlabel('t-SNE Dimension 1', fontsize=12)
                    plt.ylabel('t-SNE Dimension 2', fontsize=12)
                    plt.grid(True, alpha=0.3)
                    plt.tight_layout()
                    plt.savefig(os.path.join(args.visualize, 'tsne_clusters.png'), dpi=300, bbox_inches='tight')
                    plt.close()
                
                logging.info(f"Advanced visualizations saved to {args.visualize}")
                print(f"Generated visualizations:")
                print(f"  • Connection Strength Heatmap: {os.path.join(args.visualize, 'connection_strength_heatmap.png')}")
                if matrix_size > 1:
                    print(f"  • Clustering Dendrogram: {os.path.join(args.visualize, 'clustering_dendrogram.png')}")
                if all_coords.shape[0] >= 2:
                    print(f"  • t-SNE Relationships: {os.path.join(args.visualize, 'tsne_relationships.png')}")
                    if 'clustering' in connection_data and 'semantic_clusters' in connection_data['clustering']:
                        print(f"  • t-SNE with Clusters: {os.path.join(args.visualize, 'tsne_clusters.png')}")
                
            except ImportError as e:
                logging.error(f"Visualization failed - missing dependency: {e}")
                print(f"To use advanced visualizations, install: pip install scikit-learn seaborn")
            except Exception as e:
                logging.error(f"Error creating visualizations: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
                    
                # Create a simple error visualization to show what happened
                try:
                    plt.figure(figsize=(10, 6))
                    plt.text(0.5, 0.5, f"Visualization Error:\n{str(e)}", 
                             horizontalalignment='center', fontsize=14)
                    plt.axis('off')
                    plt.savefig(os.path.join(args.visualize, 'error_visualization.png'))
                    plt.close()
                    logging.info(f"Created error visualization at {os.path.join(args.visualize, 'error_visualization.png')}")
                except:
                    pass  # Silently fail if we can't even create the error visualization
        
        # Generate formatted output
        if args.format == 'edge-list':
            edge_list_file = os.path.join(args.visualize if args.visualize else '.', 'connections_edge_list.txt')
            with open(edge_list_file, 'w') as f:
                for src_idx, targets in filtered_connections.items():
                    src_name = file_names[src_idx]
                    for target in targets:
                        tgt_idx = target['target_idx']
                        tgt_name = file_names[tgt_idx]
                        strength = target['relevance_score']
                        f.write(f"{src_name} {tgt_name} {strength:.4f}\n")
            logging.info(f"Edge list saved to {edge_list_file}")
        
        # Calculate processing time
        elapsed_time = time.time() - start_time
        
        # Print enhanced summary with semantic insights
        total_connection_pairs = sum(len(targets) for targets in filtered_connections.values())
        total_semantic_connections = 0
        for src_idx, connections_list in filtered_connections.items():
            for connection in connections_list:
                total_semantic_connections += len(connection.get('semantic_connections', []))
        
        print("Semantic connection discovery complete")
        print(f"Files analyzed: {len(matrices)}")
        print(f"Connected matrices: {len(filtered_connections)}")
        print(f"Total connection pairs: {total_connection_pairs}")
        print(f"Total individual semantic connections: {total_semantic_connections}")
        
        # Show strongest connection with context
        strongest_src = None
        strongest_tgt = None
        strongest_val = 0
        strongest_connection = None
        
        for src_idx, connections_list in filtered_connections.items():
            for connection in connections_list:
                if connection['relevance_score'] > strongest_val:
                    strongest_val = connection['relevance_score']
                    strongest_src = src_idx
                    strongest_tgt = connection['target_idx']
                    strongest_connection = connection
        
        if strongest_src is not None:
            src_name = dataset_info[strongest_src]['file_info']['file_name']
            tgt_name = dataset_info[strongest_tgt]['file_info']['file_name']
            print(f"Strongest connection: {src_name} → {tgt_name}")
            # Detailed metrics removed from CLI output
        
        # Show data type distribution
        data_types = {}
        for info in dataset_info:
            dt = info['file_info']['data_type']
            if dt not in data_types:
                data_types[dt] = 0
            data_types[dt] += 1
        
        print(f"Data type distribution:")
        for dtype, count in data_types.items():
            print(f"   {dtype}: {count} datasets")
        
        # Show clustering summary if performed
        if 'clustering' in connection_data and 'semantic_clusters' in connection_data['clustering']:
            clusters = connection_data['clustering']['semantic_clusters']
            quality = connection_data['clustering']['cluster_quality']
            print(f"Semantic clusters: {len(clusters)}")
            print(f"Average cluster purity: {quality['average_purity']:.3f}")
            print(f"Cross-domain clusters: {quality['cross_domain_clusters']}")
            
            # Show largest cluster with context
            largest_cluster = max(clusters.items(), key=lambda x: len(x[1]['members']))
            cluster_id, cluster_info = largest_cluster
            cluster_id = int(cluster_id)  # Convert to Python int if needed
            print(f"Largest cluster: Cluster {cluster_id}")
            print(f"   Size: {len(cluster_info['members'])} matrices")
            print(f"   Dominant type: {cluster_info['dominant_data_type']}")
            print(f"   Type purity: {cluster_info['data_type_purity']:.3f}")
        
        print(f"Processing time: {elapsed_time:.4f}s")
        
        if args.output:
            print(f"Semantic connection data saved to: {args.output}")
        
        if args.visualize:
            print(f"Enhanced visualizations saved to: {args.visualize}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Error during semantic connection discovery: {str(e)}")
        if args.verbose:
            traceback.print_exc()
        return 1


# Helper methods for enhanced discover_connections_command

def _find_entity_based_connections(dataset_info, matrices):
    """
    Find connections between datasets based on shared entities and entity relationships.
    
    Args:
        dataset_info: List of dataset information dictionaries
        matrices: List of matrices corresponding to dataset_info
        
    Returns:
        dict: Entity-based connections indexed by source dataset
    """
    entity_connections = {}
    
    # Build entity-to-dataset mapping
    entity_to_datasets = {}
    
    for i, info in enumerate(dataset_info):
        entity_summary = info['file_info'].get('entity_summary', {})
        entity_ids = entity_summary.get('entity_ids', [])
        
        for entity_id in entity_ids:
            if entity_id not in entity_to_datasets:
                entity_to_datasets[entity_id] = []
            entity_to_datasets[entity_id].append(i)
    
    logging.debug(f"Found {len(entity_to_datasets)} unique entities across {len(dataset_info)} datasets")
    
    # Find datasets that share entities
    for i, info in enumerate(dataset_info):
        entity_summary = info['file_info'].get('entity_summary', {})
        entity_ids = entity_summary.get('entity_ids', [])
        
        if not entity_ids:
            continue
            
        if i not in entity_connections:
            entity_connections[i] = []
        
        # Check for shared entities with other datasets
        for entity_id in entity_ids:
            sharing_datasets = entity_to_datasets[entity_id]
            
            for j in sharing_datasets:
                if i != j:  # Don't connect to self
                    # Get entity details from both datasets
                    source_entities = _get_entities_in_matrix(matrices[i])
                    target_entities = _get_entities_in_matrix(matrices[j])
                    
                    source_entity_data = source_entities.get(entity_id, {})
                    target_entity_data = target_entities.get(entity_id, {})
                    
                    connection = {
                        'type': 'entity_based',
                        'target_idx': j,
                        'shared_entity_id': entity_id,
                        'confidence': 0.9,  # High confidence for exact entity matches
                        'description': f"Datasets share entity: {entity_id}",
                        'source_entity_info': source_entity_data.get('info', {}),
                        'target_entity_info': target_entity_data.get('info', {}),
                        'connection_strength': 'strong'
                    }
                    
                    # Check if this connection already exists
                    exists = any(
                        conn['type'] == 'entity_based' and 
                        conn['target_idx'] == j and 
                        conn['shared_entity_id'] == entity_id
                        for conn in entity_connections[i]
                    )
                    
                    if not exists:
                        entity_connections[i].append(connection)
                        logging.debug(f"Found entity-based connection: {i} -> {j} via entity {entity_id}")
    
    return entity_connections

def _calculate_entity_similarity(entity_info1, entity_info2):
    """Calculate similarity score between two entity info dictionaries."""
    if not entity_info1 or not entity_info2:
        return 0.0
    
    # Simple similarity based on common keys and values
    common_keys = set(entity_info1.keys()) & set(entity_info2.keys())
    if not common_keys:
        return 0.0
    
    score = 0.0
    for key in common_keys:
        val1 = str(entity_info1[key]).lower()
        val2 = str(entity_info2[key]).lower()
        
        if val1 == val2:
            score += 1.0
        elif val1 in val2 or val2 in val1:
            score += 0.5
    
    return min(1.0, score / len(common_keys))

def _analyze_connection_types(filtered_connections):
    """Analyze the types of connections found."""
    connection_types = {
        'mathematical_only': 0,
        'semantic_only': 0,
        'contextual_only': 0,
        'hybrid': 0,
        'entity_based': 0,  # NEW: Track entity-based connections
        'entity_semantic': 0  # NEW: Track semantic entity connections
    }
    
    for src_idx, connections_list in filtered_connections.items():
        for connection in connections_list:
            conn_type = connection.get('type', '')
            
            if conn_type == 'entity_based':
                connection_types['entity_based'] += 1
            elif conn_type == 'entity_semantic':
                connection_types['entity_semantic'] += 1
            else:
                # Original logic for other connection types
                has_math = connection.get('mathematical_strength', 0) > 0
                has_semantic = len(connection.get('semantic_connections', [])) > 0
                has_contextual = len(connection.get('contextual_bridges', [])) > 0
                
                if has_math and has_semantic and has_contextual:
                    connection_types['hybrid'] += 1
                elif has_math and not has_semantic and not has_contextual:
                    connection_types['mathematical_only'] += 1
                elif not has_math and has_semantic and not has_contextual:
                    connection_types['semantic_only'] += 1
                elif not has_math and not has_semantic and has_contextual:
                    connection_types['contextual_only'] += 1
    
    return connection_types

def _identify_domain_clusters(dataset_info, filtered_connections):
    """Identify clusters of datasets within specific domains."""
    domain_clusters = {}
    
    # Group by data type
    for info in dataset_info:
        data_type = info['file_info']['data_type']
        if data_type not in domain_clusters:
            domain_clusters[data_type] = []
        domain_clusters[data_type].append(info['file_info']['index'])
    
    # Analyze intra-domain vs inter-domain connections
    intra_domain_connections = 0
    inter_domain_connections = 0
    
    for src_idx, connections_list in filtered_connections.items():
        src_type = dataset_info[src_idx]['file_info']['data_type']
        for connection in connections_list:
            tgt_idx = connection['target_idx']
            tgt_type = dataset_info[tgt_idx]['file_info']['data_type']
            
            if src_type == tgt_type:
                intra_domain_connections += 1
            else:
                inter_domain_connections += 1
    
    return {
        'domain_groups': domain_clusters,
        'intra_domain_connections': intra_domain_connections,
        'inter_domain_connections': inter_domain_connections,
        'cross_domain_ratio': inter_domain_connections / max(1, intra_domain_connections + inter_domain_connections)
    }


def _cluster_with_semantic_analysis(matrices, filtered_connections, dataset_info, method='enhanced_hierarchical'):
    """Perform semantic-aware clustering of connection data with rich context."""
    import numpy as np
    from sklearn.cluster import KMeans
    from collections import defaultdict, Counter
    
    if not matrices or not filtered_connections:
        return {'semantic_clusters': {}, 'cluster_quality': {}}
    
    # Build enhanced similarity matrix with semantic weighting
    n_matrices = len(matrices)
    similarity_matrix = np.zeros((n_matrices, n_matrices))
    semantic_weights = np.zeros((n_matrices, n_matrices))
    
    # Fill similarity matrix with multi-dimensional scoring
    for src_idx, connections_list in filtered_connections.items():
        for connection in connections_list:
            tgt_idx = connection['target_idx']
            
            # Multi-factor similarity calculation
            math_score = connection['mathematical_strength']
            semantic_score = len(connection['semantic_connections']) / 10.0  # Normalize
            contextual_score = len(connection['contextual_bridges']) / 5.0   # Normalize
            relevance_score = connection['relevance_score']
            
            # Weighted combination favoring semantic understanding
            combined_score = (
                0.3 * math_score +
                0.4 * semantic_score +
                0.2 * contextual_score +
                0.1 * relevance_score
            )
            
            similarity_matrix[src_idx, tgt_idx] = combined_score
            similarity_matrix[tgt_idx, src_idx] = combined_score  # Symmetric
            semantic_weights[src_idx, tgt_idx] = semantic_score
    
    # Add self-similarity (diagonal) based on data type compatibility
    for i in range(n_matrices):
        similarity_matrix[i, i] = 1.0
        for j in range(i + 1, n_matrices):
            if dataset_info[i]['file_info']['data_type'] == dataset_info[j]['file_info']['data_type']:
                # Boost similarity for same data types
                similarity_matrix[i, j] *= 1.2
                similarity_matrix[j, i] *= 1.2
    
    # Convert similarity to distance for clustering
    distance_matrix = 1.0 - similarity_matrix
    np.fill_diagonal(distance_matrix, 0)
    
    # Use optimized cluster selection from MatrixTransformer
    from .matrixtransformer import MatrixTransformer
    temp_transformer = MatrixTransformer()
    
    # Convert distance matrix to coordinate space for optimized selection
    # Create feature vectors from similarity matrix for cluster optimization
    feature_vectors = []
    for i in range(n_matrices):
        # Use row of similarity matrix as feature vector
        feature_vectors.append(similarity_matrix[i, :])
    
    feature_array = np.array(feature_vectors)
    best_n_clusters = temp_transformer.optimized_cluster_selection(feature_array, max_clusters=min(8, n_matrices))
    
    # Use MatrixTransformer's internal clustering capabilities instead of sklearn
    # Store the matrices temporarily in transformer for clustering
    temp_transformer.matrices = matrices
    
    # Generate coordinates for clustering using MatrixTransformer's coordinate system
    coordinates = []
    for i, matrix in enumerate(matrices):
        try:
            coord = temp_transformer._generate_matrix_coordinates(matrix, i)
            coordinates.append(coord)
        except Exception as e:
            logging.warning(f"Could not generate coordinates for matrix {i}: {e}")
            # Fallback to similarity vector as coordinate
            coordinates.append(similarity_matrix[i, :])
    
    if coordinates:
        coordinates_array = np.array([np.array(coord) for coord in coordinates])
        
        # Use MatrixTransformer's optimized clustering instead of sklearn
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=best_n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(coordinates_array)
    else:
        # Fallback if coordinate generation fails
        cluster_labels = np.zeros(n_matrices, dtype=np.int64)
    
    # Build semantic cluster analysis
    semantic_clusters = defaultdict(lambda: {
        'members': [],
        'data_types': Counter(),
        'avg_internal_similarity': 0.0,
        'semantic_coherence': 0.0,
        'dominant_data_type': '',
        'data_type_purity': 0.0,
        'cross_connections': 0,
        'total_connections': 0
    })
    
    # Populate cluster information
    for idx, cluster_id in enumerate(cluster_labels):
        # Convert NumPy int32 to Python int
        cluster_id = int(cluster_id)
        cluster_info = semantic_clusters[cluster_id]
        cluster_info['members'].append(idx)
        cluster_info['data_types'][dataset_info[idx]['file_info']['data_type']] += 1
    
    # Calculate semantic cluster metrics
    for cluster_id, cluster_info in semantic_clusters.items():
        members = cluster_info['members']
        n_members = len(members)
        
        # Calculate average internal similarity
        internal_similarities = []
        for i in range(n_members):
            for j in range(i + 1, n_members):
                idx_i, idx_j = members[i], members[j]
                internal_similarities.append(similarity_matrix[idx_i, idx_j])
        
        cluster_info['avg_internal_similarity'] = np.mean(internal_similarities) if internal_similarities else 0.0
        
        # Calculate semantic coherence based on data type homogeneity
        most_common_type, count = cluster_info['data_types'].most_common(1)[0]
        cluster_info['dominant_data_type'] = most_common_type
        cluster_info['data_type_purity'] = count / n_members
        
        # Count cross-cluster connections
        for member_idx in members:
            if member_idx in filtered_connections:
                for connection in filtered_connections[member_idx]:
                    # Convert NumPy int32 to Python int
                    target_cluster = int(cluster_labels[connection['target_idx']])
                    if target_cluster != cluster_id:
                        cluster_info['cross_connections'] += 1
                    cluster_info['total_connections'] += 1
        
        # Calculate semantic coherence score
        semantic_coherence = (
            0.4 * cluster_info['data_type_purity'] +
            0.3 * cluster_info['avg_internal_similarity'] +
            0.3 * (1.0 - cluster_info['cross_connections'] / max(1, cluster_info['total_connections']))
        )
        cluster_info['semantic_coherence'] = semantic_coherence
    
    # Calculate overall cluster quality metrics
    all_purities = [info['data_type_purity'] for info in semantic_clusters.values()]
    all_coherences = [info['semantic_coherence'] for info in semantic_clusters.values()]
    cross_domain_clusters = sum(1 for info in semantic_clusters.values() if info['data_type_purity'] < 1.0)
    
    cluster_quality = {
        'average_purity': np.mean(all_purities) if all_purities else 0.0,
        'average_coherence': np.mean(all_coherences) if all_coherences else 0.0,
        'cross_domain_clusters': cross_domain_clusters,
        'total_clusters': len(semantic_clusters)
    }
    
    # Create final result dictionary with integer cluster IDs
    # Convert defaultdict to regular dict with properly typed keys
    fixed_semantic_clusters = {}
    for cluster_id, cluster_info in semantic_clusters.items():
        # Convert NumPy types to Python native types
        fixed_semantic_clusters[int(cluster_id)] = cluster_info
    
    return {
        'semantic_clusters': fixed_semantic_clusters,
        'cluster_quality': cluster_quality,
        'cluster_labels': cluster_labels.tolist(),
        'similarity_matrix': similarity_matrix.tolist(),
        'method_used': method
    }

def traverse_graph_command(args) -> int:
    """
    Explore semantic pathways and connections between datasets.
    
    This command enables users to navigate and discover relationships between datasets,
    find pathways between specific data points, and explore how different datasets 
    connect semantically without performing any transformations.
    
    Provides standard exports (GraphML, JSON, CSV) for compatibility with external
    network analysis tools like Gephi, Cytoscape, and Neo4j.
    """
    try:
        # Automatically configure optimal settings for this command
        # Set QVM capacity to 100.0 GB
        configure_ocr(extract_on_load=True, video_processing=True)  # Enable OCR and video OCR

        # Handle the case where args is a list (from Python API call)
        if isinstance(args, list):
            parser = create_parser()
            args = parser.parse_args(args)

        # Setup logging first
        setup_logging(args.verbose if hasattr(args, 'verbose') else False,
                      getattr(args, 'log', None))

        # Check license for advanced feature access
        try:
            license_manager = LicenseManager()
            has_access, message = license_manager.check_feature_access('traverse_graph')
            if not has_access:
                print(f"License Error: {message}")
                print("\nTo access graph traversal features:")
                print("  • Free tier: 5 uses per day")
                print("  • Upgrade for unlimited access: tensorpack upgrade")
                return 1
        except Exception as e:
            logging.warning(f"License check failed: {e}. Proceeding with basic functionality.")

        # Enforce max datasets limit
        try:
            max_ds = license_manager.get_max_datasets()
            if max_ds != float('inf') and len(getattr(args, 'inputs', [])) > max_ds:
                print(f"License Error: Your license allows {max_ds} datasets; you requested {len(getattr(args, 'inputs', []))}.")
                print(license_manager.show_upgrade_info())
                return 2
        except Exception:
            pass

        from .matrixtransformer import MatrixTransformer
        import json
        import time
        import glob
        import os

        # Configure logging based on verbose flag
        setup_logging(args.verbose if hasattr(args, 'verbose') else False,
                      getattr(args, 'log', None))

        start_time = time.time()
        transformer = MatrixTransformer()

        # Expand input file patterns
        input_files = []
        inputs = getattr(args, 'inputs', None)

        # If inputs attribute is missing, check for source/target attributes
        if not inputs and hasattr(args, 'source') and args.source:
            input_files.append(args.source)
            if hasattr(args, 'target') and args.target:
                input_files.append(args.target)
        # Process inputs attribute if available
        elif inputs:
            for pattern in inputs:
                if '*' in pattern or '?' in pattern:
                    input_files.extend(glob.glob(pattern))
                else:
                    input_files.append(pattern)

        if not input_files:
            logging.error("No input files found matching the specified patterns")
            return 1

        print(f"Exploring pathways across {len(input_files)} datasets...")

        # OCR is already enabled in the command handler
        # We can optionally adjust OCR configuration based on specific needs
        if hasattr(args, 'search_entity') and args.search_entity:
            # For entity search, we want to ensure high recall
            configure_ocr(
                confidence_threshold=0.4,  # Lower threshold for better recall in search
                include_in_search=True     # Ensure OCR text is included in search
            )

        # Load datasets for exploration
        datasets = []
        dataset_info = []

        for i, file_path in enumerate(input_files):
            try:
                # Load dataset with optional transform application
                data = load_and_apply_transform(file_path, getattr(args, 'apply_transform', None))
                datasets.append(data)

                # Log transform application if applied
                if getattr(args, 'apply_transform', None):
                    print(f"  Applied transform '{args.apply_transform}' to {os.path.basename(file_path)}")

                # Extract semantic information directly from data content and structure
                info = {
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'index': i,
                    'shape': data.shape,
                    'data_type': _detect_data_type(file_path),
                    'matrix_type': transformer._detect_matrix_type(data),
                    'semantic_coords': transformer._generate_matrix_coordinates(data, i)
                }
                dataset_info.append(info)

                if i % 5 == 0:
                    print(f"Loaded {i+1}/{len(input_files)} datasets...")

            except Exception as e:
                logging.warning(f"Failed to load {file_path}: {str(e)}")
                continue

        if not datasets:
            logging.error("No valid datasets were loaded for exploration")
            return 1

        print(f"Ready to explore {len(datasets)} datasets")

        # Perform pathfinding exploration
        exploration_results = {}

        # Handle different exploration modes
        if getattr(args, 'verbose', False):
            logging.debug(f"Checking exploration mode...")
            logging.debug(f"Has source_dataset: {hasattr(args, 'source_dataset')}")
            logging.debug(f"Has target_dataset: {hasattr(args, 'target_dataset')}")
            logging.debug(f"Has find_bridges: {hasattr(args, 'find_bridges')}")
            logging.debug(f"Has search_entity: {hasattr(args, 'search_entity')}")
            if hasattr(args, 'search_entity'):
                logging.debug(f"search_entity value: {args.search_entity}")

        # Check for source and target, either from source_dataset/target_dataset attributes
        # or from source/target attributes
        source_dataset = None
        target_dataset = None

        if hasattr(args, 'source_dataset') and args.source_dataset:
            source_dataset = args.source_dataset
        elif hasattr(args, 'source') and args.source:
            source_dataset = args.source

        if hasattr(args, 'target_dataset') and args.target_dataset:
            target_dataset = args.target_dataset
        elif hasattr(args, 'target') and args.target:
            target_dataset = args.target

        if source_dataset and target_dataset:
            # Specific path finding between two datasets
            logging.info("Using dataset pathway exploration mode")
            exploration_results = _explore_dataset_pathway(
                transformer, datasets, dataset_info,
                source_dataset, target_dataset, args
            )
            # Add rich CLI visualization for pathway results
            _display_pathway_table(exploration_results, source_dataset, target_dataset, args)

        elif hasattr(args, 'find_bridges') and args.find_bridges:
            # Find datasets that act as semantic bridges
            logging.info("Using semantic bridges exploration mode")
            exploration_results = _find_semantic_bridges(
                transformer, datasets, dataset_info, args
            )
            # Add rich CLI visualization for bridge finder results
            _display_bridge_finder_summary(exploration_results)

        elif hasattr(args, 'search_entity') and args.search_entity:
            # Search for specific entities across datasets
            logging.info(f"Using entity search mode for: {args.search_entity}")
            exploration_results = _search_entities_across_datasets(
                transformer, datasets, dataset_info, args.search_entity, args
            )
            # Add rich CLI visualization for entity search results
            _display_pathway_tree(exploration_results, args.search_entity)
        else:
            # No specific exploration mode specified - show available options
            print("No exploration mode specified!")
            print("\nAvailable exploration modes:")
            print("  Bridge Discovery:     --find-bridges")
            print("  Entity Search:        --search-entity 'ENTITY_NAME' [--generate-viz]")
            print("  Point-to-Point:      --source-dataset file1.csv --target-dataset file2.csv")
            print("\nExample:")
            print("  python tensorpack.py traverse-graph --inputs *.csv --find-bridges")
            return

        # Export exploration results in multiple formats
        output_base = getattr(args, 'output', 'pathway_results')

        # Create directory for output if it doesn't exist
        output_dir = os.path.dirname(output_base)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Ensure shared_entities have numeric confidence before exporting
        try:
            if isinstance(exploration_results, dict) and 'shared_entities' in exploration_results:
                for ent in exploration_results.get('shared_entities', []):
                    try:
                        if ent is None:
                            continue
                        if 'confidence' not in ent or ent.get('confidence') is None:
                            ent['confidence'] = _compute_shared_entity_confidence(ent)
                    except Exception:
                        # Defensive: don't let a single bad entity stop exporting
                        pass
        except Exception:
            pass

        # JSON export (always do this as the primary format)
        json_path = f"{output_base}.json"
        save_to_file(exploration_results, json_path, 'json')
        print(f"Results saved to: {json_path}")

        # === NEW: Save main numeric results as .npy/.npz if requested ===
        import numpy as np
        numeric_arrays = {}
        # Find main numeric arrays in exploration_results (top-level and one level nested)
        if isinstance(exploration_results, dict):
            for k, v in exploration_results.items():
                if isinstance(v, (np.ndarray, list)):
                    arr = np.array(v)
                    if arr.dtype.kind in 'fiubc' and arr.size > 0:
                        numeric_arrays[k] = arr
                if isinstance(v, dict):
                    for kk, vv in v.items():
                        if isinstance(vv, (np.ndarray, list)):
                            arr = np.array(vv)
                            if arr.dtype.kind in 'fiubc' and arr.size > 0:
                                numeric_arrays[f"{k}_{kk}"] = arr

        if getattr(args, 'save_npy', False):
            for name, arr in numeric_arrays.items():
                npy_path = f"{output_base}_{name}.npy"
                np.save(npy_path, arr)
                print(f"Saved numeric result: {npy_path}")

        if getattr(args, 'save_npz', False):
            npz_path = f"{output_base}.npz"
            np.savez(npz_path, **numeric_arrays)
            print(f"Saved all numeric results in: {npz_path}")

        # Use convertto (compiled module or fallback .py) for additional export formats if specified
        if hasattr(args, 'export_formats') and args.export_formats:
            try:
                import importlib
                import importlib.util
                import sys

                convertto = None
                # Try package-qualified import first (compiled .so)
                try:
                    convertto = importlib.import_module('tensorpack.convertto')
                    print('Using compiled module tensorpack.convertto for additional exports')
                    try:
                        mf = getattr(convertto, '__file__', None)
                        print(f"convertto module file: {mf}")
                        print(f"convertto has run_conversion: {hasattr(convertto, 'run_conversion')}, has main: {hasattr(convertto, 'main')}")
                    except Exception:
                        import traceback
                        traceback.print_exc()
                    # If module provides a run_conversion API, try calling it with exploration_results
                    try:
                        if hasattr(convertto, 'run_conversion'):
                            try:
                                # Create a modified version of exploration_results without NumPy arrays
                                # This is to avoid NumPy array truth value errors
                                import json
                                sanitized_results = json.loads(json.dumps(exploration_results, default=str))
                                convertto.run_conversion(sanitized_results)
                            except Exception as e:
                                print(f"convertto.run_conversion raised during package import: {e}")
                        elif hasattr(convertto, 'main'):
                            try:
                                # Save exploration_results to results.json first to ensure main() can find it
                                import json
                                with open('results.json', 'w') as f:
                                    json.dump(exploration_results, f, default=str)
                                convertto.main()
                            except Exception as e:
                                print(f"convertto.main() raised during package import: {e}")
                    except Exception:
                        import traceback
                        traceback.print_exc()
                except Exception:
                    convertto = None

                # Get the convertto.py module path for fallback
                convertto_path = os.path.join(os.path.dirname(__file__), 'convertto.py')

                if convertto is None and os.path.exists(convertto_path):
                    # Temporarily write exploration_results to results.json for convertto.py to process
                    temp_results_json = os.path.join(os.path.dirname(__file__), 'results.json')
                    backup_results = None

                    # Backup existing results.json if it exists
                    if os.path.exists(temp_results_json):
                        backup_results = temp_results_json + '.backup'
                        os.rename(temp_results_json, backup_results)

                    try:
                        # Write our exploration data as results.json with numpy type conversion
                        with open(temp_results_json, 'w', encoding='utf-8') as f:
                            json.dump(convert_numpy_types(exploration_results), f, indent=2, ensure_ascii=False)

                        # Load and execute convertto.py functions from source file
                        spec = importlib.util.spec_from_file_location("convertto", convertto_path)
                        convertto = importlib.util.module_from_spec(spec)

                        # Save current working directory and change to script directory
                        original_cwd = os.getcwd()
                        os.chdir(os.path.dirname(__file__))
                        try:
                            spec.loader.exec_module(convertto)
                            # Prefer calling run_conversion with the in-memory exploration_results
                            try:
                                if hasattr(convertto, 'run_conversion'):
                                    try:
                                        convertto.run_conversion(exploration_results)
                                    except Exception as e:
                                        print(f"convertto.run_conversion raised: {e}")
                                elif hasattr(convertto, 'main'):
                                    try:
                                        convertto.main()
                                    except Exception as e:
                                        print(f"convertto.main() raised: {e}")
                                else:
                                    print("Imported convertto module has no 'run_conversion' or 'main' entrypoints; no exports created")
                            except Exception:
                                import traceback
                                traceback.print_exc()
                            print("Generated additional export formats using convertto.py")

                            # List generated files
                            export_files = []
                            for fmt in args.export_formats:
                                if fmt == 'all' or fmt == 'csv':
                                    if os.path.exists('results.csv'):
                                        export_files.append('results.csv')
                                if fmt == 'all' or fmt == 'xlsx':
                                    if os.path.exists('results.xlsx'):
                                        export_files.append('results.xlsx')
                                if fmt == 'all' or fmt == 'html':
                                    if os.path.exists('results.html'):
                                        export_files.append('results.html')
                                if fmt == 'all' or fmt in ['sqlite', 'db']:
                                    if os.path.exists('exports/results.db'):
                                        export_files.append('exports/results.db')
                                if fmt == 'all' or fmt == 'parquet':
                                    if os.path.exists('exports/results.parquet'):
                                        export_files.append('exports/results.parquet')
                                if fmt == 'all' or fmt == 'md':
                                    if os.path.exists('exports/results.md'):
                                        export_files.append('exports/results.md')

                            if export_files:
                                print(f"Additional exports created: {', '.join(export_files)}")
                            else:
                                print("Note: No additional export files were detected")

                        finally:
                            # Restore original working directory
                            os.chdir(original_cwd)

                    finally:
                        # Cleanup: remove temp results.json and restore backup if it existed
                        if os.path.exists(temp_results_json):
                            os.remove(temp_results_json)
                        if backup_results and os.path.exists(backup_results):
                            os.rename(backup_results, temp_results_json)

                elif convertto is None:
                    print(f"Warning: convertto module/file not found (neither compiled tensorpack.convertto nor {convertto_path}); skipping additional exports")

            except Exception as e:
                print(f"Warning: Could not generate additional export formats: {e}")

        # Print exploration summary
        _print_exploration_summary(exploration_results, len(datasets), time.time() - start_time)

        return 0
    except Exception as e:
        logging.error(f"Error during dataset exploration: {str(e)}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1

def _recursively_remove_local_relationships(data):
    """Recursively remove local_relationships from nested dictionaries."""
    if isinstance(data, dict):
        # Create a new dict without local_relationships
        filtered = {}
        for key, value in data.items():
            if key != 'local_relationships':
                filtered[key] = _recursively_remove_local_relationships(value)
        return filtered
    elif isinstance(data, list):
        return [_recursively_remove_local_relationships(item) for item in data]
    else:
        return data

def _explore_dataset_pathway(transformer, datasets, dataset_info, source_dataset, target_dataset, args):
    """Find semantic pathways between two specific datasets with rich contextual information."""
    try:
        source_idx = None
        target_idx = None

        # Find source and target datasets by name or index
        for i, info in enumerate(dataset_info):
            if info['file_name'] == source_dataset or str(i) == source_dataset:
                source_idx = i
            if info['file_name'] == target_dataset or str(i) == target_dataset:
                target_idx = i

        if source_idx is None or target_idx is None:
            return {'error': 'Source or target dataset not found'}

        source_data = datasets[source_idx]
        target_data = datasets[target_idx]

        # Normalize dataset_info entries to support both flat and nested ('file_info') styles
        def _unwrap_info(info):
            if not isinstance(info, dict):
                return {}
            if 'file_name' in info and 'shape' in info:
                return info
            if 'file_info' in info and isinstance(info['file_info'], dict):
                merged = {**info['file_info']}
                # carry forward possible contextual fields
                for k in ('contextual_info', 'semantic_interpretation', 'matrix_analysis'):
                    if k in info:
                        merged[k] = info[k]
                return merged
            return info

        normalized_info = [_unwrap_info(i) for i in dataset_info]

        # Extract key entities from both datasets to create search queries
        source_metadata = _get_general_metadata(source_data)
        target_metadata = _get_general_metadata(target_data)

        # Create hybrid entity search terms from both datasets
        # Use normalized info for safe key access
        source_name = normalized_info[source_idx].get('file_name')
        target_name = normalized_info[target_idx].get('file_name')
        connection_entity = f"{source_name}→{target_name}"

        # Find entity matches in both datasets using their own key entities
        source_entities = _extract_key_entities_from_dataset(source_data, source_metadata)
        target_entities = _extract_key_entities_from_dataset(target_data, target_metadata)

        logging.debug(f"Extracted {len(source_entities)} key entities from source dataset")
        logging.debug(f"Extracted {len(target_entities)} key entities from target dataset")

        # Find matches for source entities in source dataset
        source_entity_matches = []
        for entity in source_entities[:25]:  # Limit to top entities to avoid excessive processing
            matches = _find_entity_matches_in_dataset(source_data, entity, dataset_info[source_idx])
            if matches:
                source_entity_matches.extend(matches)

        # Find matches for target entities in target dataset
        target_entity_matches = []
        for entity in target_entities[:5]:  # Limit to top entities
            matches = _find_entity_matches_in_dataset(target_data, entity, dataset_info[target_idx])
            if matches:
                target_entity_matches.extend(matches)

        # Also try to find matches of target entities in source dataset and vice versa (cross-matching)
        cross_source_matches = []
        cross_target_matches = []
        for entity in target_entities[:3]:
            matches = _find_entity_matches_in_dataset(source_data, entity, dataset_info[source_idx])
            if matches:
                cross_source_matches.extend(matches)

        for entity in source_entities[:3]:
            matches = _find_entity_matches_in_dataset(target_data, entity, dataset_info[target_idx])
            if matches:
                cross_target_matches.extend(matches)

        # Use transformer's _traverse_graph to find pathways
        path, attention_scores, metadata = transformer._traverse_graph(
            source_data,
            recent_matrices=[target_data],
            source_type=dataset_info[source_idx]['matrix_type'],
            update_field=True
        )

        # Also find semantic connections (traditional approach)
        semantic_connections = _find_semantic_connections_between_datasets(
            source_data, target_data,
            dataset_info[source_idx], dataset_info[target_idx]
        )

        # Enrich semantic connections with entity matches for better contextual understanding
        enriched_connections = []
        for connection in semantic_connections:
            # Add entity context if available
            connection_entities = []
            if cross_source_matches or cross_target_matches:
                for match in cross_source_matches + cross_target_matches:
                    if match.get('type') == connection.get('connection_type'):
                        connection_entities.append({
                            'entity': match.get('entity_name', match.get('location', '')),
                            'confidence': match.get('confidence', 0.5),
                            'context': match.get('description', '')
                        })

            enriched_connections.append({
                **connection,
                'entity_context': connection_entities
            })

        # Generate enriched pathway data with contextual elements
        # Calculate shared entities and their importance
        shared_entities = []
        for s_entity in source_entities:
            if s_entity in target_entities:
                ent = {
                    'entity_name': s_entity,
                    'in_source': True,
                    'in_target': True,
                    'importance': 'high',
                    'source_count': source_entities.count(s_entity),
                    'target_count': target_entities.count(s_entity)
                }
                # Compute numeric confidence for shared entity
                ent['confidence'] = _compute_shared_entity_confidence(ent)
                shared_entities.append(ent)

        # Prepare the detailed contextual connections
        contextual_connections = []
        if cross_source_matches or cross_target_matches:
            # Create connections for each cross-matched entity
            for match in cross_source_matches:
                entity_name = match.get('entity_name', match.get('location', ''))
                connection = {
                    'entity_name': entity_name,
                    'source': target_name,
                    'target': source_name,
                    'connection_type': 'cross_entity',
                    'confidence': match.get('confidence', 0.5),
                    'description': f"{entity_name} from {target_name} found in {source_name}"
                }
                contextual_connections.append(connection)

            for match in cross_target_matches:
                entity_name = match.get('entity_name', match.get('location', ''))
                connection = {
                    'entity_name': entity_name,
                    'source': source_name,
                    'target': target_name,
                    'connection_type': 'cross_entity',
                    'confidence': match.get('confidence', 0.5),
                    'description': f"{entity_name} from {source_name} found in {target_name}"
                }
                contextual_connections.append(connection)

        # Generate the comprehensive result with rich contextual information
        # Extract local relationships first (before traverse_graph potentially overwrites them)
        source_local_rels = _find_local_contextual_relationships(
            source_data,
            source_entities[0] if source_entities else "name",
            source_metadata,
            normalized_info[source_idx]
        )

        target_local_rels = _find_local_contextual_relationships(
            target_data,
            target_entities[0] if target_entities else "name",
            target_metadata,
            normalized_info[target_idx]
        )

        # Ensure we don't have nested local_relationships in metadata
        if metadata and isinstance(metadata, dict):
            if 'local_relationships' in metadata:
                del metadata['local_relationships']

            # Check for nested traverse_metadata as well
            if 'traverse_metadata' in metadata and isinstance(metadata['traverse_metadata'], dict):
                if 'local_relationships' in metadata['traverse_metadata']:
                    del metadata['traverse_metadata']['local_relationships']

        # Create the final result
        result = {
            'pathway_type': 'direct_exploration',
            'applied_transform': getattr(args, 'apply_transform', None),
            'transform_metadata': _get_transform_metadata([dataset_info[source_idx]['file_path'], dataset_info[target_idx]['file_path']]) if getattr(args, 'apply_transform', None) else None,
            'source_dataset': {
                **normalized_info[source_idx],
                'contextual_info': _extract_contextual_info(source_metadata, source_entities[0] if source_entities else None),
                'semantic_coordinates': {
                    'numerical': transformer._generate_matrix_coordinates(source_data, source_idx),
                    'interpretations': _interpret_semantic_coordinates(
                        transformer._generate_matrix_coordinates(source_data, source_idx),
                        dataset_info[source_idx],
                        source_metadata
                    )
                },
                'entity_matches': source_entity_matches,  # Direct entity matches in source
                'cross_matches': cross_source_matches,     # Target entities found in source
                'key_entities': [{'entity': e, 'importance': 'high' if e in shared_entities else 'medium'}
                                 for e in source_entities[:10]],
                'local_relationships': source_local_rels  # Use our contextual version
            },
            'target_dataset': {
                **normalized_info[target_idx],
                'contextual_info': _extract_contextual_info(target_metadata, target_entities[0] if target_entities else None),
                'semantic_coordinates': {
                    'numerical': transformer._generate_matrix_coordinates(target_data, target_idx),
                    'interpretations': _interpret_semantic_coordinates(
                        transformer._generate_matrix_coordinates(target_data, target_idx),
                        dataset_info[target_idx],
                        target_metadata
                    )
                },
                'entity_matches': target_entity_matches,  # Direct entity matches in target
                'cross_matches': cross_target_matches,     # Source entities found in target
                'key_entities': [{'entity': e, 'importance': 'high' if e in shared_entities else 'medium'}
                                 for e in target_entities[:10]],
                'local_relationships': target_local_rels  # Use our contextual version
            },
            'transformation_path': path,
            'attention_scores': attention_scores,
            'semantic_connections': enriched_connections,  # Enhanced with entity context
            'contextual_bridges': _find_contextual_bridges(source_metadata, target_metadata),
            'contextual_connections': contextual_connections,  # New explicit entity connections
            'shared_entities': shared_entities,  # Entities found in both datasets
            'pathway_metadata': {
                # Keep only the useful parts of metadata, exclude conflicting local_relationships
                'path_info': path,
                'matrix_analysis': _recursively_remove_local_relationships(metadata) if metadata else {},
                'transformation_details': metadata.get('tensor_metadata', {}) if metadata else {}
            }
        }

        # Compute canonical confidence and breakdown and attach to result
        structural_payload = {
            'shared_entities': len(shared_entities),
            'total_entities': len(set(source_entities + target_entities)),
            'semantic_connections': enriched_connections,
            'contextual_bridges': _find_contextual_bridges(source_metadata, target_metadata),
            'entity_coverage': {
                'source_shared_coverage': len(shared_entities) / max(1, len(source_entities)) if source_entities else 0,
                'target_shared_coverage': len(shared_entities) / max(1, len(target_entities)) if target_entities else 0,
                'overall_coverage': len(shared_entities) / max(1, len(set(source_entities + target_entities))) if shared_entities else 0
            },
            'direct_pathways': 1 if path else 0
        }

        conf_val, conf_breakdown = _build_confidence(attention_scores, structural_payload)
        result['confidence'] = conf_val
        result['confidence_breakdown'] = conf_breakdown
        # Include detailed metadata only if requested
        if hasattr(args, 'include_metadata') and args.include_metadata:
            result['source_dataset']['full_metadata'] = source_metadata
            result['target_dataset']['full_metadata'] = target_metadata
            result['full_pathway_metadata'] = metadata
            result['source_dataset_info_full'] = dataset_info[source_idx]
            result['target_dataset_info_full'] = dataset_info[target_idx]

        return result

    except Exception as e:
        return {'error': f'Pathway exploration failed: {str(e)}'}

def _find_contextual_bridges(source_metadata, target_metadata):
    """Find contextual bridges between two datasets."""
    bridges = []
    
    try:
        if source_metadata and target_metadata:
            # Compare tabular data
            if (source_metadata.get('is_tabular') and target_metadata.get('is_tabular')):
                source_cols = set(source_metadata.get('columns', []))
                target_cols = set(target_metadata.get('columns', []))
                common_cols = source_cols.intersection(target_cols)
                
                for col in common_cols:
                    bridges.append({
                        'bridge_type': 'common_column',
                        'bridge_name': col,
                        'source_context': f"Column in {source_metadata.get('file_path', 'source')}",
                        'target_context': f"Column in {target_metadata.get('file_path', 'target')}",
                        'strength': 1.0
                    })
            
            # Compare file types and formats
            if source_metadata.get('data_type') == target_metadata.get('data_type'):
                bridges.append({
                    'bridge_type': 'data_type_match',
                    'bridge_name': source_metadata.get('data_type'),
                    'source_context': source_metadata.get('file_format', 'unknown'),
                    'target_context': target_metadata.get('file_format', 'unknown'),
                    'strength': 0.7
                })
    
    except Exception as e:
        logging.debug(f"Error finding contextual bridges: {e}")
    
    return bridges

def _find_semantic_bridges(transformer, datasets, dataset_info, args):
    """Find datasets acting as semantic bridges with contextual analysis.

    NOTE: traverse_graph_command builds dataset_info as a FLAT list of dicts:
      { 'file_path', 'file_name', 'index', 'shape', 'data_type', 'matrix_type', 'semantic_coords' }
    Earlier code expected a nested structure dataset_info[i]['file_info']['file_name'] which causes KeyError.
    This function now works with the flat structure; if a nested style sneaks in it gracefully adapts.
    """
    bridge_results = []
    logging.info(f"Analyzing {len(datasets)} datasets for semantic bridges...")

    def _unwrap(info):
        """Return a unified view with keys: file_name, file_path, shape, data_type, matrix_type, semantic_coords."""
        if not info:
            return {}
        # If already flat
        if 'file_name' in info and 'shape' in info:
            return info
        # If nested under file_info
        if 'file_info' in info:
            merged = {**info['file_info']}
            # Carry forward any contextual fields
            for k in ('contextual_info','semantic_interpretation','matrix_analysis'):
                if k in info:
                    merged[k] = info[k]
            return merged
        return info

    # Pre-normalize dataset_info entries to avoid repeated branching
    normalized_info = [_unwrap(di) for di in dataset_info]

    for i, potential_bridge in enumerate(datasets):
        bridge_score = 0.0
        connections = []
        base_info = normalized_info[i]
        file_name_i = base_info.get('file_name', f'dataset_{i}')
        logging.debug(f"Testing dataset {i} ({file_name_i}) as potential bridge...")
        
        # Get rich metadata for the potential bridge dataset
        bridge_metadata = _get_general_metadata(potential_bridge)
        bridge_contextual_info = _extract_contextual_info(bridge_metadata, None)
        bridge_semantic_coords = transformer._generate_matrix_coordinates(potential_bridge, i)
        
        # Extract key entities from the bridge dataset for contextual analysis
        bridge_entities = _extract_key_entities_from_dataset(potential_bridge, bridge_metadata)
        
        # Test how well this dataset connects to others
        for j, other_dataset in enumerate(datasets):
            if i != j:
                try:
                    other_info = normalized_info[j]
                    logging.debug(f"  → Testing connection to dataset {j} ({other_info.get('file_name', f'dataset_{j}')})")
                    
                    # Get contextual info for the target dataset
                    target_metadata = _get_general_metadata(other_dataset)
                    target_contextual_info = _extract_contextual_info(target_metadata, None)
                    target_semantic_coords = transformer._generate_matrix_coordinates(other_dataset, j)
                    target_entities = _extract_key_entities_from_dataset(other_dataset, target_metadata)
                    
                    # Use traverse_graph to measure connection strength
                    path, attention_scores, metadata = transformer._traverse_graph(
                        potential_bridge,
                        recent_matrices=[other_dataset],
                        source_type=base_info.get('matrix_type'),
                        update_field=False
                    )
                    
                    # Handle attention_scores being a dictionary or list/array
                    if attention_scores:
                        if isinstance(attention_scores, dict):
                            # If it's a dictionary, take the mean of the values
                            connection_strength = np.mean(list(attention_scores.values()))
                        else:
                            # If it's a list/array, take the mean directly
                            connection_strength = np.mean(attention_scores)
                    else:
                        connection_strength = 0
                    
                    logging.debug(f"    Connection strength: {connection_strength:.4f}")
                    
                    # Even lower threshold - these datasets show consistent 0.073 connections
                    if connection_strength > 0.05:  # Lowered to 0.05 to catch the 0.073 connections
                        
                        # Find semantic connections between the bridge and target
                        semantic_connections = _find_semantic_connections_between_datasets(
                            potential_bridge, other_dataset, 
                            dataset_info[i], dataset_info[j]
                        )
                        
                        # Find contextual bridges between the datasets
                        contextual_bridges = _find_contextual_bridges(bridge_metadata, target_metadata)
                        
                        # Calculate semantic distance and compatibility
                        semantic_distance = _calculate_semantic_distance(bridge_semantic_coords, target_semantic_coords)
                        semantic_compatibility = 1.0 - min(1.0, semantic_distance)
                        
                        # Find entity overlaps and cross-matches
                        entity_overlaps = []
                        cross_entity_matches = []
                        
                        # Check for shared entities
                        for bridge_entity in bridge_entities[:5]:  # Limit to avoid excessive processing
                            if bridge_entity in target_entities:
                                entity_overlaps.append({
                                    'entity_name': bridge_entity,
                                    'context': 'shared_entity',
                                    'relevance': 'high'
                                })
                        
                        # Find cross-entity matches (bridge entities in target dataset)
                        for entity in bridge_entities[:3]:
                            entity_matches = _find_entity_matches_in_dataset(other_dataset, entity, dataset_info[j])
                            if entity_matches:
                                cross_entity_matches.extend([{
                                    'entity_name': entity,
                                    'source_dataset': base_info.get('file_name', f'dataset_{i}'),
                                    'target_dataset': other_info.get('file_name', f'dataset_{j}'),
                                    'matches_found': len(entity_matches),
                                    'confidence': max([m.get('confidence', 0) for m in entity_matches]),
                                    'connection_type': 'cross_entity_bridge'
                                }])
                        
                        # Find target entities in bridge dataset
                        for entity in target_entities[:3]:
                            entity_matches = _find_entity_matches_in_dataset(potential_bridge, entity, dataset_info[i])
                            if entity_matches:
                                cross_entity_matches.extend([{
                                    'entity_name': entity,
                                    'source_dataset': other_info.get('file_name', f'dataset_{j}'),
                                    'target_dataset': base_info.get('file_name', f'dataset_{i}'),
                                    'matches_found': len(entity_matches),
                                    'confidence': max([m.get('confidence', 0) for m in entity_matches]),
                                    'connection_type': 'reverse_entity_bridge'
                                }])
                        
                        # Find local contextual relationships within the bridge dataset
                        bridge_local_relationships = _find_local_contextual_relationships(
                            potential_bridge, 
                            bridge_entities[0] if bridge_entities else "bridge_analysis", 
                            bridge_metadata, 
                            base_info
                        )
                        
                        # Create enriched connection with full contextual information
                        enriched_connection = {
                            'target_dataset': {**other_info, 'dataset_index': j},  # Add dataset_index
                            'connection_strength': float(connection_strength),
                            'pathway': path,
                            'contextual_analysis': {
                                'bridge_context': bridge_contextual_info,
                                'target_context': target_contextual_info,
                                'semantic_compatibility': float(semantic_compatibility),
                                'semantic_distance': float(semantic_distance)
                            },
                            'semantic_coordinates': {
                                'bridge_coords': {
                                    'numerical': bridge_semantic_coords,
                                    'interpretations': _interpret_semantic_coordinates(
                                        bridge_semantic_coords, base_info, bridge_metadata
                                    )
                                },
                                'target_coords': {
                                    'numerical': target_semantic_coords,
                                    'interpretations': _interpret_semantic_coordinates(
                                        target_semantic_coords, other_info, target_metadata
                                    )
                                }
                            },
                            'entity_analysis': {
                                'bridge_entities': bridge_entities[:25],
                                'target_entities': target_entities[:25],
                                'entity_overlaps': entity_overlaps,
                                'cross_entity_matches': cross_entity_matches,
                                'total_shared_entities': len(entity_overlaps),
                                'total_cross_matches': len(cross_entity_matches)
                            },
                            'semantic_connections': semantic_connections,
                            'contextual_bridges': contextual_bridges,
                            'local_relationships': bridge_local_relationships,
                            'attention_scores': attention_scores,
                            'connection_metadata': {
                                'data_type_compatibility': base_info.get('data_type') == other_info.get('data_type'),
                                'matrix_type_compatibility': base_info.get('matrix_type') == other_info.get('matrix_type'),
                                'shape_similarity': _calculate_shape_similarity(base_info.get('shape'), other_info.get('shape')),
                                'connection_quality': _assess_connection_quality(
                                    connection_strength, semantic_connections, contextual_bridges, entity_overlaps
                                )
                            }
                        }
                        
                        connections.append(enriched_connection)
                        bridge_score += connection_strength
                        logging.debug(f"    Connection added (strength: {connection_strength:.4f})")
                        
                except Exception as e:
                    logging.debug(f"    Connection failed: {str(e)}")
                    continue
        
        if len(connections) >= 2:  # Must connect to at least 2 other datasets
            # Create enriched bridge result with full contextual analysis
            bridge_result = {
                'bridge_dataset': base_info,
                'bridge_score': float(bridge_score),  # Use total score, not average
                'connections': connections,
                'connectivity_count': len(connections),
                'bridge_analysis': {
                    'contextual_info': bridge_contextual_info,
                    'semantic_coordinates': {
                        'numerical': bridge_semantic_coords,
                        'interpretations': _interpret_semantic_coordinates(
                            bridge_semantic_coords, base_info, bridge_metadata
                        )
                    },
                    'key_entities': bridge_entities[:15],
                    'local_relationships': _find_local_contextual_relationships(
                        potential_bridge, 
                        "bridge_dataset", 
                        bridge_metadata, 
                        base_info
                    ),
                    'bridge_characteristics': {
                        'data_type': base_info.get('data_type'),
                        'matrix_type': base_info.get('matrix_type'),
                        'shape': base_info.get('shape'),
                        'complexity_estimate': get_complexity(base_info.get('matrix_type'), base_info.get('shape')) if base_info.get('matrix_type') and base_info.get('shape') else None,
                        'memory_efficiency': get_memory_efficiency(base_info.get('matrix_type')) if base_info.get('matrix_type') else None,
                        'centrality_score': bridge_score / len(connections),  # Average connection strength
                        'diversity_score': (len(set(conn['target_dataset'].get('data_type') for conn in connections)) / len(connections)) if connections else 0
                    }
                },
                'connection_summary': {
                    'total_entity_overlaps': sum(len(conn['entity_analysis']['entity_overlaps']) for conn in connections),
                    'total_cross_matches': sum(len(conn['entity_analysis']['cross_entity_matches']) for conn in connections),
                    'total_semantic_connections': sum(len(conn['semantic_connections']) for conn in connections),
                    'total_contextual_bridges': sum(len(conn['contextual_bridges']) for conn in connections),
                    'avg_semantic_compatibility': np.mean([conn['contextual_analysis']['semantic_compatibility'] for conn in connections]),
                    'data_types_connected': list(set(conn['target_dataset'].get('data_type') for conn in connections)),
                    'matrix_types_connected': list(set(conn['target_dataset'].get('matrix_type') for conn in connections))
                }
            }
            
            # Include detailed metadata only if requested
            if hasattr(args, 'include_metadata') and args.include_metadata:
                bridge_result['bridge_full_metadata'] = bridge_metadata
                bridge_result['bridge_dataset_info_full'] = base_info
                # Add full metadata to connections as well
                for conn in bridge_result['connections']:
                    try:
                        if 'target_dataset' in conn and 'dataset_index' in conn['target_dataset']:
                            dataset_idx = conn['target_dataset']['dataset_index']
                            if 0 <= dataset_idx < len(datasets):
                                conn['full_metadata'] = _get_general_metadata(datasets[dataset_idx])
                                conn['full_dataset_info'] = conn['target_dataset']
                            else:
                                logging.warning(f"Invalid dataset_index {dataset_idx} for connection metadata")
                        else:
                            logging.warning(f"Connection missing target_dataset or dataset_index: {conn.keys()}")
                    except Exception as e:
                        logging.warning(f"Error adding full metadata to connection: {e}")
                        # Continue processing other connections
            
            bridge_results.append(bridge_result)
            logging.info(f"    Bridge found: {normalized_info[i].get('file_name', f'dataset_{i}') } (total score: {bridge_score:.4f}, {len(connections)} connections)")
            logging.info(f"       Entity overlaps: {bridge_result['connection_summary']['total_entity_overlaps']}")
            logging.info(f"       Cross-matches: {bridge_result['connection_summary']['total_cross_matches']}")
            logging.info(f"       Semantic compatibility: {bridge_result['connection_summary']['avg_semantic_compatibility']:.3f}")
        else:
            logging.debug(f"    Dataset {i} ({normalized_info[i].get('file_name', f'dataset_{i}')}) connects to only {len(connections)} datasets (need ≥2)")
    
    # Sort by bridge score
    bridge_results.sort(key=lambda x: x['bridge_score'], reverse=True)
    
    logging.info(f"Bridge analysis complete: {len(bridge_results)} bridges found")
    
    # Add debugging info about connection patterns with contextual insights
    if bridge_results:
        all_strengths = []
        all_compatibilities = []
        all_entity_overlaps = []
        
        for bridge in bridge_results:
            for conn in bridge['connections']:
                all_strengths.append(conn['connection_strength'])
                all_compatibilities.append(conn['contextual_analysis']['semantic_compatibility'])
                all_entity_overlaps.append(len(conn['entity_analysis']['entity_overlaps']))
        
        if all_strengths:
            avg_strength = np.mean(all_strengths)
            max_strength = np.max(all_strengths)
            min_strength = np.min(all_strengths)
            avg_compatibility = np.mean(all_compatibilities)
            total_entity_overlaps = sum(all_entity_overlaps)
            
            logging.debug(f"Connection stats: avg={avg_strength:.4f}, max={max_strength:.4f}, min={min_strength:.4f}")
            logging.debug(f"Semantic compatibility: avg={avg_compatibility:.3f}")
            logging.debug(f"Total entity overlaps found: {total_entity_overlaps}")
    else:
        logging.debug("No bridges found - all connection strengths may be below threshold")
    
    return {
        'exploration_type': 'semantic_bridges',
        'bridges_found': len(bridge_results),
        'applied_transform': getattr(args, 'apply_transform', None),
        'transform_metadata': _get_transform_metadata([info['file_path'] for info in dataset_info]) if getattr(args, 'apply_transform', None) else None,
        'bridge_datasets': bridge_results[:10],  # Top 10 bridges
        'bridge_analysis_summary': {
            'total_bridges_analyzed': len(datasets),
            'successful_bridges': len(bridge_results),
            'avg_connections_per_bridge': np.mean([b['connectivity_count'] for b in bridge_results]) if bridge_results else 0,
            'data_type_distribution': _analyze_bridge_data_types(bridge_results),
            'connectivity_patterns': _analyze_bridge_connectivity_patterns(bridge_results)
        }
    }


def _calculate_shape_similarity(shape1, shape2):
    """Calculate similarity between two dataset shapes."""
    if shape1 == shape2:
        return 1.0
    elif len(shape1) == len(shape2):
        # Same number of dimensions
        similarity = 0.8
        # Bonus for similar sizes
        total_size1 = np.prod(shape1) if shape1 else 0
        total_size2 = np.prod(shape2) if shape2 else 0
        if total_size1 > 0 and total_size2 > 0:
            size_ratio = min(total_size1, total_size2) / max(total_size1, total_size2)
            similarity += 0.2 * size_ratio
        return similarity
    else:
        # Different dimensions
        return 0.3


def _assess_connection_quality(connection_strength, semantic_connections, contextual_bridges, entity_overlaps):
    """Assess the overall quality of a connection between datasets."""
    quality_score = 0.0
    
    # Base score from connection strength
    quality_score += connection_strength * 0.4
    
    # Bonus for semantic connections
    if semantic_connections:
        quality_score += min(0.3, len(semantic_connections) * 0.1)
    
    # Bonus for contextual bridges
    if contextual_bridges:
        quality_score += min(0.2, len(contextual_bridges) * 0.05)
    
    # Bonus for entity overlaps
    if entity_overlaps:
        quality_score += min(0.1, len(entity_overlaps) * 0.02)
    
    return min(1.0, quality_score)


def _analyze_bridge_data_types(bridge_results):
    """Analyze data type distribution among bridge datasets."""
    data_type_counts = {}
    for bridge in bridge_results:
        data_type = bridge['bridge_dataset']['data_type']
        if data_type not in data_type_counts:
            data_type_counts[data_type] = 0
        data_type_counts[data_type] += 1
    return data_type_counts


def _analyze_bridge_connectivity_patterns(bridge_results):
    """Analyze connectivity patterns among bridge datasets."""
    patterns = {
        'high_connectivity_bridges': [],  # Bridges with >3 connections
        'cross_domain_bridges': [],       # Bridges connecting different data types
        'high_compatibility_bridges': []  # Bridges with high semantic compatibility
    }
    
    for bridge in bridge_results:
        # High connectivity
        if bridge['connectivity_count'] > 3:
            patterns['high_connectivity_bridges'].append({
                'name': bridge['bridge_dataset']['file_name'],
                'connections': bridge['connectivity_count']
            })
        
        # Cross-domain connectivity
        connected_types = bridge['connection_summary']['data_types_connected']
        if len(connected_types) > 1:
            patterns['cross_domain_bridges'].append({
                'name': bridge['bridge_dataset']['file_name'],
                'data_types': connected_types
            })
        
        # High compatibility
        avg_compatibility = bridge['connection_summary']['avg_semantic_compatibility']
        if avg_compatibility > 0.7:
            patterns['high_compatibility_bridges'].append({
                'name': bridge['bridge_dataset']['file_name'],
                'compatibility': avg_compatibility
            })
    
    return patterns

def _search_entities_across_datasets(transformer, datasets, dataset_info, search_entity, args):
    """Search for specific entities or patterns across all datasets."""
    search_results = []
    
    logging.info(f"Searching for entity '{search_entity}' across {len(datasets)} datasets")
    
    for i, dataset in enumerate(datasets):
        try:
            logging.debug(f"Searching in dataset {i}: {dataset_info[i].get('file_name', f'dataset_{i}')}")
            logging.debug(f"Dataset shape: {dataset.shape}, type: {dataset.dtype}")
            
            # Get the original metadata for this dataset
            metadata = _get_general_metadata(dataset)
            has_metadata = metadata is not None
            logging.debug(f"Has original metadata: {has_metadata}")
            
            if hasattr(args, 'verbose') and args.verbose:
                logging.debug(f"Dataset info: {dataset_info[i]}")
                if metadata:
                    logging.debug(f"Metadata sample: {str(metadata)[:200]}...")
            
            # Find entity matches in this dataset
            logging.debug(f"Looking for matches of '{search_entity}' in dataset {i}...")
            entity_matches = _find_entity_matches_in_dataset(dataset, search_entity, dataset_info[i])
            
            logging.debug(f"Found {len(entity_matches)} matches in dataset {i}")
            if getattr(args, 'verbose', False) and entity_matches:
                for j, match in enumerate(entity_matches):  # Show first 3 matches
                    logging.debug(f"Match {j+1}: {match}")
            
            if entity_matches:
                logging.info(f"Found {len(entity_matches)} matches for '{search_entity}' in {dataset_info[i].get('file_name', f'dataset_{i}')}")
                
                # Get semantic coordinates with context
                semantic_coords = transformer._generate_matrix_coordinates(dataset, i)
                
                # Use traverse_graph to understand how this entity connects
                logging.debug(f"Starting graph traversal for {dataset_info[i].get('file_name', f'dataset_{i}')}...")
                # Set skip_local_relations=True to indicate we'll use our own contextual version
                path, attention_scores, traverse_metadata = transformer._traverse_graph(
                    dataset,
                    recent_matrices=[],
                    source_type=dataset_info[i]['matrix_type'],
                    update_field=False
                )
                
                # Ensure we remove any local_relationships from the returned metadata using recursive filtering
                filtered_traverse_metadata = _recursively_remove_local_relationships(traverse_metadata)
                
                if getattr(args, 'verbose', False):
                    logging.debug(f"Graph traversal complete. Path length: {len(path)}")
                    logging.debug(f"Path: {path}")
                    
                    # Convert NumPy values to Python native types for logging
                    top_scores = {}
                    for k, v in sorted(attention_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
                        if hasattr(v, 'item'):  # Check if it's a NumPy scalar
                            top_scores[k] = v.item()  # Convert to Python native type
                        else:
                            top_scores[k] = v
                    logging.debug(f"Top attention scores: {top_scores}")
                
                # Filter out matrixtransformer's local_relationships from traverse_metadata
                filtered_traverse_metadata = _recursively_remove_local_relationships(filtered_traverse_metadata)
                
                # Create rich contextual result
                result = {
                    'dataset_index': i,
                    'dataset_name': dataset_info[i].get('file_name', f'dataset_{i}'),
                    'dataset_path': dataset_info[i]['file_path'],
                    'data_type': dataset_info[i]['data_type'],
                    'entity_matches': entity_matches,
                    'semantic_coordinates': {
                        'numerical': semantic_coords,
                        'interpretations': _interpret_semantic_coordinates(semantic_coords, dataset_info[i], metadata)
                    },
                    'contextual_info': _extract_contextual_info(metadata, search_entity),
                    'local_relationships': _find_local_contextual_relationships(dataset, search_entity, metadata, dataset_info[i]),
                    'semantic_context': path,
                    'relevance_score': max([match.get('confidence', 0) for match in entity_matches]),
                    'attention_scores': attention_scores
                }
                
                # Include detailed metadata only if requested
                if hasattr(args, 'include_metadata') and args.include_metadata:
                    result['traverse_metadata'] = filtered_traverse_metadata
                    # Keep traverse metadata and dataset info, but omit embedding
                    # the entire dataset metadata in each result to keep JSON output
                    # compact and focused on search results.
                    result['dataset_info_full'] = dataset_info[i]
                
                search_results.append(result)
            else:
                logging.debug(f"No matches found for '{search_entity}' in {dataset_info[i].get('file_name', f'dataset_{i}')}")
                
        except Exception as e:
            logging.warning(f"Entity search failed for {dataset_info[i].get('file_name', f'dataset_{i}')}: {str(e)}")
            if getattr(args, 'verbose', False):
                import traceback
                traceback.print_exc()
            continue
    
    # Sort by relevance score
    search_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # Create the results dictionary
    results_dict = {
        'exploration_type': 'entity_search',
        'search_query': search_entity,
        'matches_found': len(search_results),
        'applied_transform': getattr(args, 'apply_transform', None),
        'transform_metadata': _get_transform_metadata([info['file_path'] for info in dataset_info]) if getattr(args, 'apply_transform', None) else None,
        'results': search_results
    }
    
    return results_dict




def _find_semantic_connections_between_datasets(source_data, target_data, source_info, target_info):
    """Find specific semantic connections between two datasets."""
    connections = []

    try:
        # Normalize info dictionaries: support nested 'file_info' style used elsewhere
        def _normalize_info(info):
            if not isinstance(info, dict):
                return {}
            # If 'file_info' is present, merge it up for easier access
            if 'file_info' in info and isinstance(info['file_info'], dict):
                merged = {**info}
                # move nested file_info keys to top-level (without overwriting existing keys)
                for k, v in info['file_info'].items():
                    if k not in merged:
                        merged[k] = v
                return merged
            return info

        s_info = _normalize_info(source_info or {})
        t_info = _normalize_info(target_info or {})

        # Infer data_type from file extension if missing
        def _infer_type(info):
            if not isinstance(info, dict):
                return None
            dt = info.get('data_type')
            if dt:
                return dt
            fp = info.get('file_path') or info.get('file_info', {}).get('file_path')
            if fp and isinstance(fp, str):
                ext = os.path.splitext(fp)[1].lower()
                if ext in ('.csv', '.tsv'):
                    return 'tabular'
                if ext in ('.json', '.jsonl'):
                    return 'json'
                if ext in ('.xlsx', '.xls'):
                    return 'excel'
                if ext in ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'):
                    return 'image'
            return None

        source_type = _infer_type(s_info) or s_info.get('data_type')
        target_type = _infer_type(t_info) or t_info.get('data_type')
        logging.debug(f"_find_semantic_connections_between_datasets: inferred types -> source: {source_type}, target: {target_type}")

        # JSON-specific handling
        if source_type == 'json' and target_type == 'json':
            # Get metadata to access the original structured JSON data
            source_metadata = _get_general_metadata(source_data)
            target_metadata = _get_general_metadata(target_data)

            # Add detailed debug logging for metadata
            logging.debug(f"Source metadata available: {source_metadata is not None}")
            logging.debug(f"Target metadata available: {target_metadata is not None}")

            # First, try direct access to file paths to guarantee we have the data
            source_file_path = s_info.get('file_info', {}).get('file_path', '') or s_info.get('file_path', '')
            target_file_path = t_info.get('file_info', {}).get('file_path', '') or t_info.get('file_path', '')

            # Direct loading approach - always prioritize this
            source_json_data = None
            target_json_data = None

            # Try direct file loading first - most reliable approach
            if source_file_path and os.path.exists(source_file_path) and source_file_path.endswith('.json'):
                try:
                    logging.debug(f"Direct loading of source JSON from {source_file_path}")
                    with open(source_file_path, 'r', encoding='utf-8') as f:
                        source_json_data = json.load(f)
                    logging.info(f"Successfully loaded source JSON directly from file: {type(source_json_data).__name__}")
                except Exception as e:
                    logging.warning(f"Failed direct JSON loading for source: {e}, will try fallback methods")

            if target_file_path and os.path.exists(target_file_path) and target_file_path.endswith('.json'):
                try:
                    logging.debug(f"Direct loading of target JSON from {target_file_path}")
                    with open(target_file_path, 'r', encoding='utf-8') as f:
                        target_json_data = json.load(f)
                    logging.info(f"Successfully loaded target JSON directly from file: {type(target_json_data).__name__}")
                except Exception as e:
                    logging.warning(f"Failed direct JSON loading for target: {e}, will try fallback methods")

            # Try temporary storage if direct loading failed
            if source_json_data is None:
                source_temp_key = f"temp_json_data_{hash(source_file_path)}"
                if source_temp_key in _GENERAL_METADATA:
                    source_json_data = _GENERAL_METADATA[source_temp_key]
                    logging.debug(f"Found source JSON data in temporary storage: {type(source_json_data).__name__}")
                elif source_metadata and 'original_data' in source_metadata:
                    source_json_data = source_metadata.get('original_data')
                    logging.debug(f"Found source JSON data in metadata: {type(source_json_data).__name__}")

            if target_json_data is None:
                target_temp_key = f"temp_json_data_{hash(target_file_path)}"
                if target_temp_key in _GENERAL_METADATA:
                    target_json_data = _GENERAL_METADATA[target_temp_key]
                    logging.debug(f"Found target JSON data in temporary storage: {type(target_json_data).__name__}")
                elif target_metadata and 'original_data' in target_metadata:
                    target_json_data = target_metadata.get('original_data')
                    logging.debug(f"Found target JSON data in metadata: {type(target_json_data).__name__}")

            # Detailed debug log for JSON data availability after all attempts
            logging.debug(f"Final source JSON data available: {source_json_data is not None}, Type: {type(source_json_data).__name__ if source_json_data else 'None'}")
            logging.debug(f"Final target JSON data available: {target_json_data is not None}, Type: {type(target_json_data).__name__ if target_json_data else 'None'}")

            # Extensive logging of sample data to verify content is usable
            if source_json_data:
                if isinstance(source_json_data, list) and len(source_json_data) > 0:
                    sample = source_json_data[0] if source_json_data else None
                    if isinstance(sample, dict):
                        logging.debug(f"Source JSON sample keys: {list(sample.keys())}")
                    logging.debug(f"Source JSON total items: {len(source_json_data)}")
                elif isinstance(source_json_data, dict):
                    logging.debug(f"Source JSON root keys: {list(source_json_data.keys())}")
            else:
                logging.warning("Source JSON data is not available after all recovery attempts")

            if target_json_data:
                if isinstance(target_json_data, list) and len(target_json_data) > 0:
                    sample = target_json_data[0] if target_json_data else None
                    if isinstance(sample, dict):
                        logging.debug(f"Target JSON sample keys: {list(sample.keys())}")
                    logging.debug(f"Target JSON total items: {len(target_json_data)}")
                elif isinstance(target_json_data, dict):
                    logging.debug(f"Target JSON root keys: {list(target_json_data.keys())}")
            else:
                logging.warning("Target JSON data is not available after all recovery attempts")

            # Step 1: Create deep extraction functions to get all data at any level
            def extract_all_fields_and_values(json_data, prefix=""):
                """Extract all fields and values from nested JSON structures for matching"""
                results = {}

                if isinstance(json_data, dict):
                    # Process dictionary fields
                    for key, value in json_data.items():
                        current_path = f"{prefix}.{key}" if prefix else key

                        # Store scalar values directly
                        if isinstance(value, (str, int, float)) and not isinstance(value, bool):
                            results[current_path] = str(value)

                        # Recursively process nested structures
                        if isinstance(value, (dict, list)):
                            nested_results = extract_all_fields_and_values(value, current_path)
                            results.update(nested_results)

                elif isinstance(json_data, list):
                    # Process list items (for each item, extract fields)
                    for i, item in enumerate(json_data):
                        current_path = f"{prefix}[{i}]"

                        # Store scalar values directly
                        if isinstance(item, (str, int, float)) and not isinstance(item, bool):
                            results[current_path] = str(item)

                        # Recursively process nested structures
                        if isinstance(item, (dict, list)):
                            nested_results = extract_all_fields_and_values(item, current_path)
                            results.update(nested_results)

                return results

            # Helper function to extract flat field names from nested structures
            def extract_all_field_names(json_data, prefix=""):
                """Extract all field names from nested JSON structures"""
                field_names = set()

                if isinstance(json_data, dict):
                    for key, value in json_data.items():
                        current_path = f"{prefix}.{key}" if prefix else key
                        field_names.add(current_path)

                        if isinstance(value, (dict, list)):
                            nested_fields = extract_all_field_names(value, current_path)
                            field_names.update(nested_fields)

                elif isinstance(json_data, list) and len(json_data) > 0:
                    # For lists, check the first item as representative
                    if isinstance(json_data[0], dict):
                        for key in json_data[0].keys():
                            current_path = f"{prefix}.{key}" if prefix else key
                            field_names.add(current_path)

                        for key, value in json_data[0].items():
                            current_path = f"{prefix}.{key}" if prefix else key
                            if isinstance(value, (dict, list)):
                                nested_fields = extract_all_field_names(value, current_path)
                                field_names.update(nested_fields)

                return field_names

            # Function to extract values from all fields for cross-field value matching
            def extract_all_scalar_values(json_data):
                """Extract all scalar values from any level in the JSON data"""
                all_values = {}

                def _extract_values(data, path=""):
                    if isinstance(data, dict):
                        for key, value in data.items():
                            current_path = f"{path}.{key}" if path else key

                            if isinstance(value, (str, int, float)) and not isinstance(value, bool):
                                if str(value) not in all_values:
                                    all_values[str(value)] = []
                                all_values[str(value)].append(current_path)

                            if isinstance(value, (dict, list)):
                                _extract_values(value, current_path)

                    elif isinstance(data, list):
                        for i, item in enumerate(data):
                            current_path = f"{path}[{i}]"

                            if isinstance(item, (str, int, float)) and not isinstance(item, bool):
                                if str(item) not in all_values:
                                    all_values[str(item)] = []
                                all_values[str(item)].append(current_path)

                            if isinstance(item, (dict, list)):
                                _extract_values(item, current_path)

                _extract_values(json_data)
                return all_values

            if source_json_data and target_json_data:
                # Log JSON data details for debugging
                logging.debug(f"Source JSON data type: {type(source_json_data).__name__}")
                logging.debug(f"Target JSON data type: {type(target_json_data).__name__}")

                # For JSON data, treat like tabular data with common fields
                json_connections = []

                # Extract all field values from both datasets
                logging.info("Extracting all fields and values from JSON data...")

                try:
                    source_all_values = extract_all_fields_and_values(source_json_data)
                    target_all_values = extract_all_fields_and_values(target_json_data)
                    logging.debug(f"Extracted {len(source_all_values)} fields from source JSON")
                    logging.debug(f"Extracted {len(target_all_values)} fields from target JSON")
                except Exception as e:
                    logging.error(f"Error extracting field values: {e}")
                    source_all_values = {}
                    target_all_values = {}

                # Extract field names for structure comparison
                try:
                    source_fields = extract_all_field_names(source_json_data)
                    target_fields = extract_all_field_names(target_json_data)
                    logging.debug(f"Extracted {len(source_fields)} field names from source JSON")
                    logging.debug(f"Extracted {len(target_fields)} field names from target JSON")
                except Exception as e:
                    logging.error(f"Error extracting field names: {e}")
                    # Fallback to simplistic extraction
                    source_fields = set()
                    target_fields = set()

                    if isinstance(source_json_data, dict):
                        source_fields = set(source_json_data.keys())
                    elif isinstance(source_json_data, list) and source_json_data and isinstance(source_json_data[0], dict):
                        source_fields = set(source_json_data[0].keys())

                    if isinstance(target_json_data, dict):
                        target_fields = set(target_json_data.keys())
                    elif isinstance(target_json_data, list) and target_json_data and isinstance(target_json_data[0], dict):
                        target_fields = set(target_json_data[0].keys())

                # Find common fields that might indicate connections
                common_fields = source_fields.intersection(target_fields)
                logging.info(f"Found {len(common_fields)} common field paths between JSON datasets")

                # Track matches between fields
                field_matches = {}

                # Also check for fields with different names that might contain matching values
                cross_field_matches = {}

                # Find exact path matches first
                for field in common_fields:
                    if field in source_all_values and field in target_all_values:
                        if source_all_values[field] == target_all_values[field]:
                            field_matches[field] = {
                                'total_matches': 1,
                                'unique_matches': 1,
                                'match_values': [source_all_values[field]],
                                'source_records': 1,
                                'target_records': 1
                            }

                # Now find cross-field value matches (different fields with same values)
                logging.info("Looking for cross-field value matches...")
                try:
                    # Extract all scalar values from both datasets with their paths
                    source_value_paths = extract_all_scalar_values(source_json_data)
                    target_value_paths = extract_all_scalar_values(target_json_data)

                    logging.debug(f"Extracted {len(source_value_paths)} unique values from source JSON")
                    logging.debug(f"Extracted {len(target_value_paths)} unique values from target JSON")

                    # Find common values between datasets
                    common_values = set(source_value_paths.keys()).intersection(set(target_value_paths.keys()))

                    # Filter out very short values as they're likely to match by chance
                    filtered_common_values = [v for v in common_values if len(v) > 3]

                    logging.info(f"Found {len(filtered_common_values)} common values between JSON datasets")

                    # Create connections for matching values
                    for value in filtered_common_values[:100]:  # Limit to top 100 matches to avoid performance issues
                        source_paths = source_value_paths[value]
                        target_paths = target_value_paths[value]

                        # Create cross-field match entries for each source-target path pair
                        for source_path in source_paths[:5]:  # Limit to 5 paths per value
                            for target_path in target_paths[:5]:  # Limit to 5 paths per value
                                cross_field_key = f"{source_path}→{target_path}"

                                cross_field_matches[cross_field_key] = {
                                    'total_matches': 1,
                                    'unique_matches': 1,
                                    'match_values': [value],
                                    'source_field': source_path,
                                    'target_field': target_path,
                                    'source_records': 1,
                                    'target_records': 1
                                }

                except Exception as e:
                    logging.error(f"Error finding cross-field matches: {str(e)}")
                    traceback.print_exc()

                # Generate connections from the matches
                logging.info("Generating JSON connections from matches...")

                # Add detailed connections for matching fields
                for field, match_info in field_matches.items():
                    # Calculate connection strength
                    source_coverage = match_info['total_matches'] / max(1, match_info['source_records'])
                    target_coverage = match_info['total_matches'] / max(1, match_info['target_records'])
                    avg_coverage = (source_coverage + target_coverage) / 2

                    json_connections.append({
                        'type': 'json_field_match',
                        'field': field,
                        'match_count': match_info['total_matches'],
                        'unique_matches': match_info['unique_matches'],
                        'match_values': match_info['match_values'],
                        'source_coverage': source_coverage,
                        'target_coverage': target_coverage,
                        'strength': avg_coverage,
                        'confidence': 0.9  # Higher confidence for exact field matches
                    })

                # Add cross-field connections (different fields with matching values)
                for field_pair, match_info in cross_field_matches.items():
                    source_coverage = match_info['total_matches'] / max(1, match_info['source_records'])
                    target_coverage = match_info['total_matches'] / max(1, match_info['target_records'])
                    avg_coverage = (source_coverage + target_coverage) / 2

                    json_connections.append({
                        'type': 'json_cross_field_match',
                        'field': field_pair,
                        'source_field': match_info['source_field'],
                        'target_field': match_info['target_field'],
                        'match_count': match_info['total_matches'],
                        'unique_matches': match_info['unique_matches'],
                        'match_values': match_info['match_values'],
                        'source_coverage': source_coverage,
                        'target_coverage': target_coverage,
                        'strength': avg_coverage,
                        'confidence': 0.8  # Slightly lower confidence for cross-field matches
                    })

                # Also check for structural similarities (similar JSON patterns/schemas)
                if len(source_fields) > 0 and len(target_fields) > 0:
                    # Calculate Jaccard similarity between field sets
                    jaccard_sim = len(common_fields) / (len(source_fields) + len(target_fields) - len(common_fields))

                    if jaccard_sim > 0.3:  # If structures are at least somewhat similar
                        json_connections.append({
                            'type': 'json_structure_similarity',
                            'similarity': jaccard_sim,
                            'common_fields': list(common_fields)[:10],  # Limit to 10 fields for brevity
                            'description': f"JSON structures show {jaccard_sim:.2f} similarity in their field patterns",
                            'confidence': 0.7 + (jaccard_sim * 0.3)  # Higher similarity = higher confidence
                        })

                # Return connections if found
                if json_connections:
                    # Mark these as high-quality semantic connections from actual JSON fields
                    for conn in json_connections:
                        conn['semantic_connection_type'] = 'json_field_level'
                        conn['semantic_quality'] = 'high'
                        # Add relationship type
                        if conn['type'] == 'json_field_match':
                            conn['relationship'] = 'exact_field_match'
                        elif conn['type'] == 'json_cross_field_match':
                            conn['relationship'] = 'value_match'
                        elif conn['type'] == 'json_structure_similarity':
                            conn['relationship'] = 'structural'

                    logging.info(f"Found {len(json_connections)} JSON field-level connections between datasets")
                    return json_connections
                else:
                    # No connections found between JSON datasets
                    logging.warning("No field matches found between JSON datasets after comprehensive analysis")
                    return [{'type': 'no_matches', 'message': 'No field matches found between JSON datasets'}]

        # For different data types, use standard approaches
        # Handle mixed JSON <-> Tabular pairs (e.g., .json <-> .csv) by comparing
        # JSON field names/values against tabular column names/values.
        if (source_type == 'json' and target_type == 'tabular') or (source_type == 'tabular' and target_type == 'json'):
            try:
                logging.debug("Handling mixed JSON <-> Tabular pair for semantic matching")

                # Determine which side is JSON and which is tabular
                if source_type == 'json':
                    json_data = source_json_data if 'source_json_data' in locals() else None
                    json_info_local = s_info
                    tab_matrix = target_data
                    tab_info_local = t_info
                else:
                    json_data = target_json_data if 'target_json_data' in locals() else None
                    json_info_local = t_info
                    tab_matrix = source_data
                    tab_info_local = s_info

                # Attempt to recover JSON content if not already loaded
                if json_data is None:
                    # Try metadata
                    jm = _get_general_metadata(tab_matrix) if json_data is None else None
                    # Try to look up the other matrix's metadata if needed
                    json_meta = _get_general_metadata(source_data) if source_type == 'json' else _get_general_metadata(target_data)
                    if json_meta and 'original_data' in json_meta:
                        json_data = json_meta.get('original_data')

                # Extract JSON fields and scalar values (simple implementation)
                def _extract_json_field_names(data, prefix=""):
                    fields = set()
                    if isinstance(data, dict):
                        for k, v in data.items():
                            p = f"{prefix}.{k}" if prefix else k
                            fields.add(p)
                            if isinstance(v, (dict, list)):
                                fields.update(_extract_json_field_names(v, p))
                    elif isinstance(data, list) and data:
                        # Use first element as representative for structure
                        if isinstance(data[0], dict):
                            for k, v in data[0].items():
                                p = f"{prefix}.{k}" if prefix else k
                                fields.add(p)
                                if isinstance(v, (dict, list)):
                                    fields.update(_extract_json_field_names(v, p))
                    return fields

                def _extract_json_scalar_values(data):
                    vals = {}
                    def _recurse(d, path=""):
                        if isinstance(d, dict):
                            for k, v in d.items():
                                p = f"{path}.{k}" if path else k
                                if isinstance(v, (str, int, float)) and not isinstance(v, bool):
                                    vals.setdefault(str(v), []).append(p)
                                if isinstance(v, (dict, list)):
                                    _recurse(v, p)
                        elif isinstance(d, list):
                            for i, item in enumerate(d):
                                p = f"{path}[{i}]"
                                if isinstance(item, (str, int, float)) and not isinstance(item, bool):
                                    vals.setdefault(str(item), []).append(p)
                                if isinstance(item, (dict, list)):
                                    _recurse(item, p)
                    _recurse(data)
                    return vals

                json_fields = _extract_json_field_names(json_data) if json_data is not None else set()
                json_values_map = _extract_json_scalar_values(json_data) if json_data is not None else {}

                # Collect tabular columns and sample values
                tab_cols = []
                tab_col_values = {}
                # Try metadata first
                tab_meta = _get_general_metadata(tab_matrix)
                if tab_meta:
                    if 'columns' in tab_meta:
                        tab_cols = list(tab_meta.get('columns') or [])
                    if 'dataframe' in tab_meta:
                        try:
                            df = tab_meta.get('dataframe')
                            if df is not None:
                                tab_cols = tab_cols or list(df.columns)
                                for c in tab_cols:
                                    try:
                                        tab_col_values[c] = df[c].dropna().astype(str).unique().tolist()[:200]
                                    except Exception:
                                        tab_col_values[c] = []
                        except Exception:
                            pass

                # Try info file path and pandas fallback
                if not tab_cols:
                    fp = tab_info_local.get('file_info', {}).get('file_path') or tab_info_local.get('file_path')
                    try:
                        import pandas as _pd
                        if fp and os.path.exists(fp):
                            df = _pd.read_csv(fp, nrows=2000)
                            tab_cols = list(df.columns)
                            for c in tab_cols:
                                try:
                                    tab_col_values[c] = df[c].dropna().astype(str).unique().tolist()[:200]
                                except Exception:
                                    tab_col_values[c] = []
                    except Exception:
                        pass

                # If still no columns, infer generic col names from numpy shape
                if not tab_cols:
                    try:
                        if hasattr(tab_matrix, 'ndim') and tab_matrix.ndim == 2:
                            ncols = tab_matrix.shape[1]
                            tab_cols = [f'col_{i}' for i in range(ncols)]
                            for i, c in enumerate(tab_cols):
                                try:
                                    tab_col_values[c] = list(np.unique(tab_matrix[:, i]).astype(str).tolist()[:200])
                                except Exception:
                                    tab_col_values[c] = []
                    except Exception:
                        pass

                connections_found = []

                # Compare JSON field names to tabular column names using text similarity
                for jf in list(json_fields)[:200]:
                    for col in tab_cols:
                        sim = _calculate_text_similarity(jf.split('.')[-1], col)
                        if sim > 0.65:
                            connections_found.append({
                                'type': 'json_field_to_tabular_column',
                                'json_field': jf,
                                'tabular_column': col,
                                'similarity': float(sim),
                                'confidence': float(0.6 + sim * 0.4),
                                'relationship': 'field_name_match'
                            })

                # Compare JSON scalar values against tabular column sample values
                # Build quick lookup of tabular value sets
                tab_value_sets = {c: set([str(v) for v in vals]) for c, vals in tab_col_values.items()}
                for val, src_paths in list(json_values_map.items())[:500]:
                    if len(val) <= 3:
                        continue
                    for col, vset in tab_value_sets.items():
                        if not vset:
                            continue
                        if val in vset:
                            connections_found.append({
                                'type': 'json_value_to_tabular_value',
                                'value': val,
                                'json_paths': src_paths[:5],
                                'tabular_column': col,
                                'match_count': 1,
                                'strength': 1.0,
                                'confidence': 0.85,
                                'relationship': 'value_overlap'
                            })

                if connections_found:
                    logging.info(f"Found {len(connections_found)} JSON↔Tabular semantic connections")
                    return connections_found
                else:
                    logging.warning("No JSON↔Tabular semantic connections found")
                    return [{'type': 'no_matches', 'message': 'No JSON↔Tabular semantic connections found'}]
            except Exception as e:
                logging.error(f"Error during JSON↔Tabular semantic matching: {e}")
                traceback.print_exc()
                return [{'type': 'error', 'message': str(e)}]
        if source_type == 'excel' and target_type == 'excel':
            # Handle Excel data specially like JSON
            excel_connections = _find_excel_field_connections(source_data, target_data, source_info, target_info)
            if excel_connections:
                # Mark these as high-quality semantic connections from actual Excel fields
                for conn in excel_connections:
                    conn['semantic_connection_type'] = 'excel_field_level'
                    conn['semantic_quality'] = 'high'
                connections.extend(excel_connections)
                logging.info(f"Found {len(excel_connections)} Excel field-level connections between datasets")
        elif source_type == 'tabular' and target_type == 'tabular':
            # Look for overlapping patterns in tabular data
            connections = _find_tabular_connections(source_data, target_data, source_info, target_info)
        elif (source_type and 'image' in source_type) or (target_type and 'image' in target_type):
            # Look for visual pattern connections
            connections = _find_visual_connections(source_data, target_data, source_info, target_info)
        else:
            # General numerical pattern connections
            connections = _find_numerical_connections(source_data, target_data, source_info, target_info)

    except Exception as e:
        logging.error(f"Error analyzing semantic connections: {str(e)}")
        traceback.print_exc()
        connections = [{'type': 'error', 'message': str(e)}]

    return connections

def _find_excel_field_connections(source_data, target_data, source_info, target_info):
    """Find detailed field-level connections between Excel datasets."""
    connections = []
    
    try:
        logging.debug("Finding Excel field-level semantic connections")
        
        # Get source and target file paths
        source_file_path = source_info.get('file_info', {}).get('file_path', '') or source_info.get('file_path', '')
        target_file_path = target_info.get('file_info', {}).get('file_path', '') or target_info.get('file_path', '')
        
        # Try to get Excel dataframes from storage
        source_df = None
        target_df = None
        
        # Try direct excel data key first
        source_excel_key = f"excel_data_{hash(source_file_path)}"
        if source_excel_key in _GENERAL_METADATA:
            source_df = _GENERAL_METADATA[source_excel_key]
            logging.debug(f"Found source Excel data with key {source_excel_key}")
        
        target_excel_key = f"excel_data_{hash(target_file_path)}"
        if target_excel_key in _GENERAL_METADATA:
            target_df = _GENERAL_METADATA[target_excel_key]
            logging.debug(f"Found target Excel data with key {target_excel_key}")
        
        # Fallback to metadata search
        if source_df is None:
            for meta_key, meta_value in _GENERAL_METADATA.items():
                if isinstance(meta_value, dict) and meta_value.get('file_path') == source_file_path and 'dataframe' in meta_value:
                    source_df = meta_value['dataframe']
                    logging.debug(f"Found source Excel dataframe in metadata")
                    break
        
        if target_df is None:
            for meta_key, meta_value in _GENERAL_METADATA.items():
                if isinstance(meta_value, dict) and meta_value.get('file_path') == target_file_path and 'dataframe' in meta_value:
                    target_df = meta_value['dataframe']
                    logging.debug(f"Found target Excel dataframe in metadata")
                    break
        
        # If we found both dataframes, find connections between them
        if source_df is not None and target_df is not None:
            logging.debug(f"Found Excel dataframes, source shape: {source_df.shape}, target shape: {target_df.shape}")
            
            # 1. Match column names between dataframes
            for source_col in source_df.columns:
                for target_col in target_df.columns:
                    if str(source_col) and str(target_col):
                        # Calculate similarity between column names
                        similarity = _calculate_text_similarity(str(source_col), str(target_col))
                        if similarity > 0.7:  # Higher threshold for column names
                            connections.append({
                                'type': 'excel_column_match',
                                'source_column': str(source_col),
                                'target_column': str(target_col),
                                'similarity': float(similarity),
                                'confidence': float(similarity),
                                'connection_type': 'semantic'
                            })
            
            # 2. Look for similar data patterns in columns
            # Sample a subset of rows for performance
            max_rows = min(1000, min(len(source_df), len(target_df)))
            source_sample = source_df.head(max_rows) if len(source_df) > 0 else source_df
            target_sample = target_df.head(max_rows) if len(target_df) > 0 else target_df
            
            # Check for columns with similar values
            for source_col in source_df.columns:
                source_vals = source_sample[source_col].dropna().astype(str).tolist()
                
                if not source_vals:
                    continue
                    
                for target_col in target_df.columns:
                    target_vals = target_sample[target_col].dropna().astype(str).tolist()
                    
                    if not target_vals:
                        continue
                    
                    # Compare sample values for matching patterns
                    matching_values = 0
                    for s_val in source_vals[:50]:  # Limit sample size
                        for t_val in target_vals[:50]:
                            if s_val and t_val and s_val == t_val and len(s_val) > 1:
                                matching_values += 1
                                break
                    
                    # Calculate matching ratio
                    match_ratio = matching_values / min(len(source_vals[:50]), len(target_vals[:50])) if min(len(source_vals[:50]), len(target_vals[:50])) > 0 else 0
                    
                    if match_ratio > 0.3:  # If more than 30% of values match
                        connections.append({
                            'type': 'excel_value_overlap',
                            'source_column': str(source_col),
                            'target_column': str(target_col),
                            'matching_values': matching_values,
                            'match_ratio': float(match_ratio),
                            'confidence': float(match_ratio),
                            'connection_type': 'content'
                        })
            
            # Log results
            logging.info(f"Found {len(connections)} Excel field-level semantic connections between datasets")
        else:
            logging.warning("Could not find Excel dataframes for connection analysis")
            
    except Exception as e:
        logging.error(f"Excel content matching failed: {str(e)}")
        traceback.print_exc()
    
    return connections

def _find_tabular_connections(source_data, target_data, source_info, target_info):
    """Find connections between tabular datasets."""
    connections = []

    try:
        # Try to obtain column names and per-column values.
        # Prefer DataFrame in metadata; fallback to reading CSV if pandas is available.
        src_cols = None
        tgt_cols = None
        src_values = {}
        tgt_values = {}

        # Helper to load columns and sample values
        def _collect_columns_and_values(data, info):
            cols = None
            colvals = {}
            # 1) Check metadata for original dataframe or columns
            meta = _get_general_metadata(data)
            if meta:
                # metadata may include 'columns' or 'dataframe'
                if 'columns' in meta:
                    cols = list(meta['columns']) if isinstance(meta['columns'], (list, tuple)) else None
                if 'dataframe' in meta and cols is None:
                    try:
                        df = meta['dataframe']
                        cols = list(df.columns)
                        for c in cols:
                            try:
                                colvals[c] = df[c].dropna().unique().tolist()
                            except Exception:
                                colvals[c] = []
                    except Exception:
                        pass

            # 2) Look into info->file_info for columns
            if cols is None and isinstance(info, dict):
                cols = info.get('file_info', {}).get('columns') or info.get('columns')

            # 3) Attempt fast CSV load if pandas is available and file path present
            if cols is None:
                try:
                    import pandas as _pd
                    fp = info.get('file_info', {}).get('file_path') or info.get('file_path')
                    if fp and os.path.exists(fp):
                        try:
                            df = _pd.read_csv(fp, nrows=2000)
                            cols = list(df.columns)
                            for c in cols:
                                try:
                                    colvals[c] = df[c].dropna().unique().tolist()[:200]
                                except Exception:
                                    colvals[c] = []
                        except Exception:
                            cols = None
                except Exception:
                    # pandas not available or failed; leave cols as None
                    cols = cols

            # 4) If still no columns, attempt to infer from numpy 2D arrays as generic column indices
            if cols is None:
                try:
                    if hasattr(data, 'ndim') and data.ndim == 2:
                        ncols = data.shape[1]
                        cols = [f'col_{i}' for i in range(ncols)]
                        for i, c in enumerate(cols):
                            try:
                                colvals[c] = list(np.unique(data[:, i]).tolist()[:200])
                            except Exception:
                                colvals[c] = []
                except Exception:
                    cols = cols

            return cols or [], colvals

        src_cols, src_values = _collect_columns_and_values(source_data, source_info)
        tgt_cols, tgt_values = _collect_columns_and_values(target_data, target_info)

        logging.debug(f"Tabular connections: src_cols={src_cols}, tgt_cols={tgt_cols}")
        logging.debug(f"Tabular connections: src_values keys={list(src_values.keys())}, tgt_values keys={list(tgt_values.keys())}")

        # Compute header overlap
        header_overlap = 0.0
        common_cols = []
        try:
            set_src = set([c.lower() for c in src_cols]) if src_cols else set()
            set_tgt = set([c.lower() for c in tgt_cols]) if tgt_cols else set()
            common_cols = list(set_src.intersection(set_tgt))
            header_overlap = (len(common_cols) / max(1, min(len(set_src), len(set_tgt)))) if set_src and set_tgt else 0.0
        except Exception:
            header_overlap = 0.0

        logging.debug(f"Tabular connections: common_cols={common_cols}, header_overlap={header_overlap}")

        per_column_matches = []
        # For each common column name, compute value-overlap ratio
        for col in common_cols:
            # Find original-cased column keys in collected dicts
            src_key = next((k for k in src_values.keys() if k.lower() == col), None)
            tgt_key = next((k for k in tgt_values.keys() if k.lower() == col), None)
            src_set = set([str(v) for v in src_values.get(src_key, [])]) if src_key else set()
            tgt_set = set([str(v) for v in tgt_values.get(tgt_key, [])]) if tgt_key else set()
            if not src_set and not tgt_set:
                continue
            try:
                inter = src_set.intersection(tgt_set)
                union = src_set.union(tgt_set)
                jaccard = (len(inter) / len(union)) if union else 0.0
            except Exception:
                jaccard = 0.0
            per_column_matches.append((col, jaccard, len(inter), len(union)))

        # Create connections for strong per-column matches
        for col, score, inter_count, union_count in sorted(per_column_matches, key=lambda x: x[1], reverse=True):
            # small scores are still informative; include even low scores with low confidence
            conn = {
                'type': 'tabular_column_match',
                'column': col,
                'match_count': int(inter_count),
                'unique_union': int(union_count),
                'strength': float(score),
                'confidence': float(0.6 + (score * 0.4)),
                'relationship': 'column_value_overlap'
            }
            connections.append(conn)

        # Add table-level summary connection based on header overlap and median column strength
        median_col_strength = 0.0
        if per_column_matches:
            median_col_strength = float(np.median([p[1] for p in per_column_matches]))

        table_strength = float(0.6 * header_overlap + 0.4 * median_col_strength)
        # Add a summary connection if any signal exists
        if table_strength > 0.0:
            connections.insert(0, {
                'type': 'tabular_table_summary',
                'header_overlap': float(header_overlap),
                'median_column_strength': float(median_col_strength),
                'strength': table_strength,
                'confidence': float(0.5 + (table_strength * 0.5)),
                'relationship': 'table_level'
            })

    except Exception as e:
        logging.error(f"Error in tabular connection detection: {e}")

    logging.debug(f"Tabular connections: returning {len(connections)} connections")
    return connections


def _find_numerical_connections(source_data, target_data, source_info, target_info):
    """Find connections between generic numerical datasets."""
    connections = []
    
    try:
        # Calculate basic statistics for numerical comparison
        source_mean = np.mean(source_data) if hasattr(source_data, 'mean') else 0
        target_mean = np.mean(target_data) if hasattr(target_data, 'mean') else 0
        
        source_std = np.std(source_data) if hasattr(source_data, 'std') else 1
        target_std = np.std(target_data) if hasattr(target_data, 'std') else 1
        
        # Check for similar statistical properties
        mean_similarity = 1.0 / (1.0 + abs(source_mean - target_mean))
        std_similarity = 1.0 / (1.0 + abs(source_std - target_std))
        
        if mean_similarity > 0.7 or std_similarity > 0.7:
            connections.append({
                'type': 'numerical_similarity',
                'mean_similarity': float(mean_similarity),
                'std_similarity': float(std_similarity),
                'description': 'Numerical datasets show similar statistical properties',
                'confidence': float((mean_similarity + std_similarity) / 2.0),
                'relationship': 'statistical'
            })
            
    except Exception as e:
        logging.error(f"Error finding numerical connections: {str(e)}")
    
    return connections

def _find_contextual_bridges(metadata1, metadata2):
    """Find contextual bridges between datasets based on metadata."""
    bridges = []
    
    # Skip if either metadata is missing
    if not metadata1 or not metadata2:
        return bridges
    
    try:
        # Check for common entities
        entity_ids1 = metadata1.get('entity_ids', [])
        entity_ids2 = metadata2.get('entity_ids', [])
        
        common_entities = set(entity_ids1).intersection(set(entity_ids2))
        if common_entities:
            bridges.append({
                'bridge_type': 'common_entities',
                'bridge_name': f"Shared entities ({len(common_entities)})",
                'entities': list(common_entities)[:5],  # List up to 5 entities
                'confidence': 0.9
            })
        
        # Check for shared domain context
        domain1 = metadata1.get('domain_context', {})
        domain2 = metadata2.get('domain_context', {})
        
        for key in domain1:
            if key in domain2 and domain1[key] == domain2[key]:
                bridges.append({
                    'bridge_type': 'shared_domain_context',
                    'bridge_name': f"Shared {key}: {domain1[key]}",
                    'context_key': key,
                    'context_value': domain1[key],
                    'confidence': 0.8
                })
                
    except Exception as e:
        logging.error(f"Error finding contextual bridges: {str(e)}")
    
    return bridges

def _calculate_text_similarity(text1, text2):
    """Calculate similarity between two text strings using a simple approach."""
    if not text1 or not text2:
        return 0.0
    
    try:
        # Normalize texts
        text1 = str(text1).lower().strip()
        text2 = str(text2).lower().strip()
        
        # Quick exact match check - return highest possible score for exact matches
        if text1 == text2:
            return 1.0
        
        # Check for exact substring match (one is completely contained in the other)
        if text1 in text2:
            # If text1 is short enough compared to text2, treat as high similarity
            if len(text1) > 3 and len(text1) >= len(text2) * 0.5:
                return 0.95  # Very high but not perfect match
        
        if text2 in text1:
            # If text2 is short enough compared to text1, treat as high similarity
            if len(text2) > 3 and len(text2) >= len(text1) * 0.5:
                return 0.95  # Very high but not perfect match
            
        # Length-based initial filter
        len_ratio = min(len(text1), len(text2)) / max(len(text1), len(text2)) if max(len(text1), len(text2)) > 0 else 0
        if len_ratio < 0.3:  # Too different in length
            return 0.2 * len_ratio  # Still give a small score for length similarity
        
        # Calculate character overlap
        common_chars = set(text1) & set(text2)
        char_similarity = len(common_chars) / max(len(set(text1)), len(set(text2))) if max(len(set(text1)), len(set(text2))) > 0 else 0
        
        # Calculate word overlap for multi-word strings
        words1 = set(text1.split())
        words2 = set(text2.split())
        word_similarity = 0
        if words1 and words2:
            common_words = words1 & words2
            word_similarity = len(common_words) / max(len(words1), len(words2)) if max(len(words1), len(words2)) > 0 else 0
        
        # Calculate edit distance for short strings (avoid performance issues)
        edit_similarity = 0
        if len(text1) < 100 and len(text2) < 100:
            import difflib
            edit_similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        
        # Weighted combination of similarities
        if word_similarity > 0:
            # If we have words, weight word similarity higher
            return 0.1 * len_ratio + 0.2 * char_similarity + 0.5 * word_similarity + 0.2 * edit_similarity
        else:
            # For single tokens, use character and edit distance
            return 0.2 * len_ratio + 0.4 * char_similarity + 0.4 * edit_similarity
            
    except Exception as e:
        logging.warning(f"Error calculating text similarity: {str(e)}")
        return 0.0

def _calculate_semantic_distance(coords1, coords2):
    """Calculate semantic distance between two sets of coordinates."""
    if not coords1 or not coords2:
        return 1.0  # Maximum distance if no coordinates
    
    try:
        # Convert to arrays for vectorized operations
        coords1_arr = np.array(coords1) if isinstance(coords1, list) else coords1
        coords2_arr = np.array(coords2) if isinstance(coords2, list) else coords2
        
        # If coordinates are of different dimensionality, normalize
        if coords1_arr.shape[1] != coords2_arr.shape[1]:
            # Pad with zeros to match dimensions
            max_dim = max(coords1_arr.shape[1], coords2_arr.shape[1])
            if coords1_arr.shape[1] < max_dim:
                pad_width = ((0, 0), (0, max_dim - coords1_arr.shape[1]))
                coords1_arr = np.pad(coords1_arr, pad_width, 'constant')
            if coords2_arr.shape[1] < max_dim:
                pad_width = ((0, 0), (0, max_dim - coords2_arr.shape[1]))
                coords2_arr = np.pad(coords2_arr, pad_width, 'constant')
        
        # Calculate pairwise distances
        distances = []
        for coord1 in coords1_arr:
            for coord2 in coords2_arr:
                dist = np.linalg.norm(coord1 - coord2)
                distances.append(dist)
        
        # Return average distance, normalized to [0, 1]
        avg_distance = np.mean(distances) if distances else 1.0
        return min(1.0, avg_distance / 10.0)  # Normalize to [0, 1] with a scale factor
        
    except Exception as e:
        logging.error(f"Error calculating semantic distance: {str(e)}")
        return 1.0  # Return maximum distance on error

def _find_visual_connections(source_data, target_data, source_info, target_info):
    """Find connections between visual/image datasets."""
    connections = []
    
    # Look for similar dimensionality or structure
    if source_data.shape == target_data.shape:
        connections.append({
            'type': 'structural_similarity',
            'description': f'Both datasets have identical shape: {source_data.shape}',
            'similarity_score': 1.0
        })
    elif len(source_data.shape) == len(target_data.shape):
        connections.append({
            'type': 'dimensional_similarity',
            'description': f'Both datasets have {len(source_data.shape)} dimensions',
            'similarity_score': 0.8
        })
    
    return connections



# Enhanced _find_entity_matches_in_dataset with custom matcher support
def _find_entity_matches_in_dataset(dataset, search_entity, dataset_info):
    """
    Find matches for a search entity within a dataset using sequential application
    of all matching techniques for comprehensive coverage, including binary and image data.
    Enhanced with semantic search for JSON datasets.
    """
    matches = []
    dataset_name = dataset_info.get('file_path', 'unknown_dataset')
    
    logging.info(f"Starting comprehensive entity matching for '{search_entity}' in {dataset_name}")
    
    # NEW: Phase 1 - Semantic Search for JSON datasets
    semantic_matches = _search_semantic_index(dataset, search_entity, dataset_info)
    if semantic_matches:
        logging.info(f"Found {len(semantic_matches)} semantic matches for '{search_entity}'")
        matches.extend(semantic_matches)
    
    # Check if this is a binary or image dataset to prioritize appropriate matchers
    data_type = dataset_info.get('data_type', 'unknown')
    is_binary = data_type == 'binary'
    is_image = data_type == 'image'
    
    # 0. First check if the search entity is a registered entity ID
    logging.debug(f"Checking for entity ID match for '{search_entity}'")
    entity_by_id = _find_entity_by_id(search_entity)
    if entity_by_id:
        logging.info(f"Found exact entity ID match for '{search_entity}' in registry")
        matches.append({
            'type': 'entity_id_match',
            'value': search_entity,
            'entity_info': entity_by_id['info'],
            'confidence': 1.0,
            'context': f"Exact match for registered entity ID: {search_entity}",
            'match_type': 'entity_id',
            'matcher_type': 'registry'
        })
    
    # 0.1. Search through all registered entities for partial matches in entity info AND entity ID
    logging.debug(f"Searching all registered entities for '{search_entity}'")
    for entity_id, entity_data in _ENTITY_REGISTRY.items():
        entity_info = entity_data.get('info', {})
        
        # Check if search term appears in entity ID (partial match)
        if search_entity.lower() in entity_id.lower() and search_entity.lower() != entity_id.lower():
            logging.info(f"Found entity ID partial match for '{search_entity}' in entity '{entity_id}'")
            matches.append({
                'type': 'entity_id_partial_match',
                'value': search_entity,
                'entity_id': entity_id,
                'entity_info': entity_info,
                'confidence': 0.9,
                'context': f"Partial match in entity ID: {entity_id}",
                'match_type': 'entity_id_partial',
                'matcher_type': 'registry'
            })
        
        # Check if search term appears in any entity info field
        info_matches = []
        for key, value in entity_info.items():
            if value and search_entity.lower() in str(value).lower():
                info_matches.append(f"{key}: {value}")
        
        if info_matches:
            logging.info(f"Found entity info match for '{search_entity}' in entity '{entity_id}'")
            matches.append({
                'type': 'entity_info_match',
                'value': search_entity,
                'entity_id': entity_id,
                'entity_info': entity_info,
                'matched_fields': info_matches,
                'confidence': 0.85,
                'context': f"Found in entity '{entity_id}' fields: {', '.join(info_matches)}",
                'match_type': 'entity_info',
                'matcher_type': 'registry'
            })
    
    # 0.2. Check for entities mapped to matrix regions if this dataset has entity mappings
    existing_entities = _get_entities_in_matrix(dataset)
    if existing_entities:
        logging.debug(f"Found {len(existing_entities)} existing entities in matrix for {dataset_name}")
        for coord_key, entity_data in existing_entities.items():
            entity_id = entity_data['entity_id']
            entity_info = entity_data['info']
            
            # Check if search entity matches the entity ID or any info fields
            if (search_entity.lower() in entity_id.lower() or 
                any(search_entity.lower() in str(v).lower() for v in entity_info.values() if v)):
                
                logging.info(f"Found matrix region entity match for '{search_entity}' in {dataset_name}")
                matches.append({
                    'type': 'matrix_region_match',
                    'value': search_entity,
                    'entity_id': entity_id,
                    'entity_info': entity_info,
                    'coordinates': coord_key,
                    'confidence': 0.9,
                    'context': f"Found in matrix entity at coordinates {coord_key}",
                    'match_type': 'matrix_entity',
                    'matcher_type': 'spatial'
                })
    else:
        logging.debug(f"No entities mapped to matrix regions in {dataset_name}")
    # 1. Apply domain-specific matchers (user-registered via add-transform_command)
    logging.debug(f"Applying domain-specific matchers for {dataset_name}")
    domain_matches = _apply_domain_specific_matchers(dataset, search_entity, dataset_info)
    if domain_matches:
        matches.extend(domain_matches)
        logging.info(f"Domain-specific matchers found {len(domain_matches)} matches in {dataset_name}")
    else:
        logging.debug(f"No domain-specific matches found in {dataset_name}")
    
    # 2. For binary and image data, prioritize special content extraction
    if is_binary or is_image:
        logging.debug(f"Prioritizing binary/image extraction for {dataset_name}")
        
        # 2.1 First check OCR text if this is an image
        if is_image:
            try:
                # Look for OCR data in metadata
                metadata = _get_general_metadata(dataset)
                
                # Debug logging
                array_id = id(dataset)
                logging.info(f"Searching for metadata for array ID {array_id} in {dataset_name}")
                logging.info(f"Available metadata keys: {list(_GENERAL_METADATA.keys())}")
                logging.info(f"OCR registry keys: {list(_OCR_INDEX_REGISTRY.keys())}")
                
                ocr_enabled = metadata and (metadata.get('ocr_processed', False) or metadata.get('has_text', False))
                
                logging.info(f"Metadata found: {metadata is not None}, OCR enabled: {ocr_enabled}")
                if metadata:
                    logging.info(f"Metadata keys: {list(metadata.keys())}")
                
                # If OCR data not found but this is an image file, try to enable OCR and process it now
                if not ocr_enabled and search_entity:
                    logging.info(f"Auto-enabling OCR for image search for '{search_entity}'")
                    
                    # Configure OCR and reload the image with OCR enabled
                    from .ocr_integration import extract_text_from_image, create_ocr_index
                    raw_results, ocr_df = extract_text_from_image(dataset)
                    
                    if not ocr_df.empty:
                        ocr_index = create_ocr_index(ocr_df)
                        ocr_raw_text = ' '.join(row['text'] for _, row in ocr_df.iterrows())
                        
                        # Update metadata
                        if metadata is None:
                            metadata = {}
                        metadata.update({
                            'ocr_processed': True,
                            'ocr_raw_text': ocr_raw_text,
                            'has_text': len(ocr_df) > 0,
                            'text_count': len(ocr_df),
                            'ocr_index': ocr_index
                        })
                        
                        # Store the OCR data in the dataset metadata
                        _store_general_metadata(dataset_name, dataset, dataset, 'image', metadata)
                        
                        # Also store in the OCR index registry
                        _OCR_INDEX_REGISTRY[id(dataset)] = ocr_index
                        
                        logging.info(f"OCR processing completed: {len(ocr_df)} text items found")
                        ocr_enabled = True
                
                if ocr_enabled:
                    # Check if OCR data found text in the image
                    ocr_text = metadata.get('ocr_raw_text', '')
                    
                    logging.info(f"OCR text found in {dataset_name}: '{ocr_text[:200]}...' (showing first 200 chars)")
                    
                    if ocr_text and search_entity.lower() in ocr_text.lower():
                        logging.info(f"Found OCR text match in image for {dataset_name}")
                        
                        # Find context around the match
                        match_pos = ocr_text.lower().find(search_entity.lower())
                        context_start = max(0, match_pos - 30)
                        context_end = min(len(ocr_text), match_pos + len(search_entity) + 30)
                        context = ocr_text[context_start:context_end]
                        
                        matches.append({
                            'type': 'ocr_text_match',
                            'value': search_entity,
                            'confidence': 0.9,  # Higher confidence for OCR text
                            'context': f"Found in image OCR text: '...{context}...'",
                            'match_type': 'ocr_match',
                            'matcher_type': 'ocr_extraction',
                            'text_count': metadata.get('text_count', 0)
                        })
                    else:
                        logging.info(f"OCR text available but no match for '{search_entity}' in {dataset_name}")
                    
                    # Check OCR index for more specific matches
                    array_id = id(dataset)
                    if array_id in _OCR_INDEX_REGISTRY:
                        ocr_index = _OCR_INDEX_REGISTRY[array_id]
                        logging.info(f"OCR Index available for {dataset_name} with {len(ocr_index.get('string_entities', {}))} text entries")
                        
                        # Debug: Show all OCR text found
                        if logging.getLogger().level <= logging.INFO:
                            all_text_keys = list(ocr_index.get('string_entities', {}).keys())
                            logging.info(f"All OCR text detected in {dataset_name}: {all_text_keys[:10]}")  # Show first 10 entries
                        
                        # Look for exact matches in the OCR index
                        search_lower = search_entity.lower()
                        if 'string_entities' in ocr_index and search_lower in ocr_index['string_entities']:
                            # Get the specific text box IDs for this search term
                            text_box_ids = ocr_index['string_entities'][search_lower]
                            
                            for text_box_id in text_box_ids:
                                if text_box_id in ocr_index.get('value_mappings', {}):
                                    text_info = ocr_index['value_mappings'][text_box_id]
                                    
                                    matches.append({
                                        'type': 'ocr_indexed_match',
                                        'value': search_entity,
                                        'confidence': text_info.get('confidence', 0.85),
                                        'context': f"Found text '{text_info.get('text', search_entity)}' in image at box {text_info.get('box', 'unknown')}",
                                        'match_type': 'ocr_exact',
                                        'matcher_type': 'ocr_extraction',
                                        'box': text_info.get('box'),
                                        'frame': text_info.get('frame'),
                                        'text_box_id': text_box_id
                                    })
                        
                        # Look for partial matches in the OCR index
                        partial_matches = []
                        for text_key in ocr_index.get('string_entities', {}):
                            if search_lower in text_key.lower() and text_key.lower() != search_lower:
                                text_box_ids = ocr_index['string_entities'][text_key]
                                for text_box_id in text_box_ids:
                                    if text_box_id in ocr_index.get('value_mappings', {}):
                                        text_info = ocr_index['value_mappings'][text_box_id]
                                        partial_matches.append({
                                            'text': text_info.get('text', text_key),
                                            'info': text_info,
                                            'text_box_id': text_box_id
                                        })
                        
                        # Add partial matches
                        for match in partial_matches:
                            matches.append({
                                'type': 'ocr_partial_match',
                                'value': search_entity,
                                'matched_text': match['text'],
                                'confidence': match['info'].get('confidence', 0.75) * 0.9,  # Reduce confidence for partial match
                                'context': f"Found in OCR text '{match['text']}' at box {match['info'].get('box', 'unknown')}",
                                'match_type': 'ocr_partial',
                                'matcher_type': 'ocr_extraction',
                                'box': match['info'].get('box'),
                                'frame': match['info'].get('frame'),
                                'text_box_id': match['text_box_id']
                            })
            except Exception as e:
                logging.debug(f"OCR search failed: {str(e)}")
        
        # 2.2 Try the original binary/image content extraction
        try:
            # Import the text decoder function
            from ._decode_text_from_dataset import _decode_text_from_dataset
            
            # Extract text content from binary/image data
            extracted_text = _decode_text_from_dataset(dataset, dataset_info)
            
            if extracted_text and search_entity.lower() in extracted_text.lower():
                logging.info(f"Found match in extracted binary/image content for {dataset_name}")
                
                # Find context around the match
                match_pos = extracted_text.lower().find(search_entity.lower())
                context_start = max(0, match_pos - 30)
                context_end = min(len(extracted_text), match_pos + len(search_entity) + 30)
                context = extracted_text[context_start:context_end]
                
                matches.append({
                    'type': f"{data_type}_content_match",
                    'value': search_entity,
                    'confidence': 0.85,
                    'context': f"Found in {data_type} content: '...{context}...'",
                    'match_type': f"{data_type}_match",
                    'matcher_type': 'content_extraction'
                })
        except Exception as e:
            logging.debug(f"Binary/image content extraction failed: {str(e)}")
    
    # 3. Apply NLP-based matching (may still work on extracted text content)
    logging.debug(f"Applying NLP-based matching for {dataset_name}")
    nlp_matches = _apply_nlp_entity_matching(dataset, search_entity, dataset_info)
    if nlp_matches:
        matches.extend(nlp_matches)
        logging.info(f"NLP matchers found {len(nlp_matches)} matches in {dataset_name}")
    else:
        logging.debug(f"No NLP matches found in {dataset_name}")
    
    # 4. Apply semantic similarity matching
    logging.debug(f"Applying semantic similarity matching for {dataset_name}")
    semantic_matches = _apply_semantic_similarity_matching(dataset, search_entity, dataset_info)
    if semantic_matches:
        matches.extend(semantic_matches)
        logging.info(f"Semantic matchers found {len(semantic_matches)} matches in {dataset_name}")
    else:
        logging.debug(f"No semantic similarity matches found in {dataset_name}")
    
    # 5. Always apply basic pattern matching for comprehensive exact matches
    logging.debug(f"Applying basic pattern matching for {dataset_name}")
    basic_matches = _apply_basic_pattern_matching(dataset, search_entity, dataset_info)
    if basic_matches:
        matches.extend(basic_matches)
        logging.info(f"Basic pattern matching found {len(basic_matches)} matches in {dataset_name}")
    else:
        logging.debug(f"No basic pattern matches found in {dataset_name}")
    
    # Remove duplicates while preserving order and highest confidence
    unique_matches = []
    seen_locations = set()
    
    for match in sorted(matches, key=lambda x: x.get('confidence', 0), reverse=True):
        location_key = (match.get('location', ''), match.get('context', ''))
        if location_key not in seen_locations:
            unique_matches.append(match)
            seen_locations.add(location_key)
    
    matches = unique_matches
    
    # 6. Last resort: Direct string search in original data if no matches found
    if not matches:
        logging.debug(f"No matches found with standard methods, trying direct string search as last resort for {dataset_name}")
        # Get the original file path
        file_path = dataset_info.get('file_path', '')
        if file_path and os.path.exists(file_path):
            try:
                # For JSON files, use our specialized fast JSON search
                if file_path.lower().endswith('.json'):
                    try:
                        # First try using our specialized fast JSON search module
                        try:
                            from _fast_json_search import fast_search_json_file
                            json_matches = fast_search_json_file(file_path, search_entity, max_matches=5)
                            if json_matches:
                                logging.info(f"Fast JSON search found {len(json_matches)} matches for '{search_entity}' in {file_path}")
                                matches.extend(json_matches)
                        except ImportError:
                            logging.debug("Fast JSON search module not available, using fallback method")
                            # Fallback to simpler approach
                            with open(file_path, 'r', encoding='utf-8') as f:
                                # Read in reasonable size chunks to avoid memory issues
                                chunk_size = 5 * 1024 * 1024  # 5MB
                                position = 0
                                found_count = 0
                                
                                while found_count < 5:  # Limit to 5 matches
                                    chunk = f.read(chunk_size)
                                    if not chunk:  # End of file
                                        break
                                        
                                    search_pattern = re.compile(re.escape(search_entity), re.IGNORECASE)
                                    for match in search_pattern.finditer(chunk):
                                        # Get context around match
                                        start_pos = max(0, match.start() - 50)
                                        end_pos = min(len(chunk), match.end() + 50)
                                        context = chunk[start_pos:end_pos]
                                        
                                        matches.append({
                                            'type': 'direct_string_match',
                                            'value': search_entity,
                                            'confidence': 0.95,  # High confidence for direct matches
                                            'context': f"Found direct match in file: '...{context}...'",
                                            'match_type': 'direct_string',
                                            'matcher_type': 'last_resort',
                                            'file_position': position + match.start()
                                        })
                                        found_count += 1
                                        if found_count >= 5:
                                            break
                                            
                                    position += chunk_size
                                    
                    except Exception as e:
                        logging.debug(f"Direct JSON file search failed: {str(e)}")
            except Exception as e:
                logging.debug(f"Last resort direct search failed: {str(e)}")
                
    # Log comprehensive summary
    if matches:
        match_types = {}
        matcher_types = {}
        for match in matches:
            match_type = match.get('match_type', 'unknown')
            matcher_type = match.get('matcher_type', 'unknown')
            match_types[match_type] = match_types.get(match_type, 0) + 1
            matcher_types[matcher_type] = matcher_types.get(matcher_type, 0) + 1
        
        match_type_summary = ", ".join([f"{k}: {v}" for k, v in match_types.items()])
        matcher_summary = ", ".join([f"{k}: {v}" for k, v in matcher_types.items()])
        logging.info(f"Final comprehensive results for {dataset_name}: {len(matches)} total matches")
        logging.info(f"Match types: {match_type_summary}")
        logging.info(f"Matcher distribution: {matcher_summary}")
    else:
        logging.warning(f"No matches found with any method in {dataset_name}")
    
    return matches

def _apply_domain_specific_matchers(dataset, search_entity, dataset_info):
    """Apply domain-specific entity matchers from the transform registry sequentially."""
    matches = []
    
    try:
        # Get the data type and domain
        data_type = dataset_info.get('data_type', 'unknown')
        
        # Look for registered entity matchers for this data type
        entity_matchers = _get_registered_entity_matchers(data_type)
        
        if not entity_matchers:
            logging.debug(f"No domain-specific matchers registered for data type: {data_type}")
            return matches
        
        logging.debug(f"Found {len(entity_matchers)} domain-specific matchers for data type: {data_type}")
        
        for matcher_name, matcher_func in entity_matchers.items():
            try:
                logging.debug(f"Applying domain-specific entity matcher: {matcher_name}")
                domain_matches = matcher_func(dataset, search_entity, dataset_info)
                
                if domain_matches:
                    # Tag matches with the matcher that found them
                    for match in domain_matches:
                        match['matcher'] = matcher_name
                        match['matcher_type'] = 'domain_specific'
                    
                    matches.extend(domain_matches)
                    logging.info(f"Domain-specific matcher '{matcher_name}' found {len(domain_matches)} matches")
                else:
                    logging.debug(f"Domain-specific matcher '{matcher_name}' found no matches")
                
            except Exception as e:
                logging.warning(f"Domain-specific matcher '{matcher_name}' failed: {str(e)}")
                continue
        
        if matches:
            logging.info(f"Total domain-specific matches found: {len(matches)} from {len(entity_matchers)} matchers")
        
    except Exception as e:
        logging.warning(f"Domain-specific matching failed: {str(e)}")
    
    return matches

def _apply_nlp_entity_matching(dataset, search_entity, dataset_info):
    """Apply NLP-based entity matching techniques."""
    matches = []
    
    try:
        # Check if we have text-like data or metadata
        if dataset_info.get('data_type') == 'text' or 'text' in str(dataset_info):
            matches.extend(_nlp_text_entity_matching(dataset, search_entity, dataset_info))
        
        # Check for named entity recognition in any string-like data
        if hasattr(dataset, 'dtype') and dataset.dtype.kind in ['U', 'S', 'a']:
            matches.extend(_nlp_string_entity_matching(dataset, search_entity, dataset_info))
        
        # Use spaCy for advanced NLP if available
        try:
            import spacy
            matches.extend(_spacy_entity_matching(dataset, search_entity, dataset_info))
        except ImportError:
            pass
        
        # Use transformers for semantic search if available
        try:
            model = create_silent_sentence_transformer()
            matches.extend(_transformer_entity_matching(dataset, search_entity, dataset_info, model))
        except ImportError:
            pass
            
    except Exception as e:
        logging.debug(f"NLP entity matching failed: {str(e)}")
    
    return matches

def _apply_semantic_similarity_matching(dataset, search_entity, dataset_info):
    """Apply semantic similarity-based matching using embeddings."""
    matches = []
    
    try:
        # Convert search entity to embedding
        entity_embedding = _get_entity_embedding(search_entity)
        
        if entity_embedding is not None:
            # Look for semantically similar patterns in the dataset
            if dataset_info.get('data_type') == 'tabular':
                matches.extend(_semantic_tabular_matching(dataset, entity_embedding, search_entity, dataset_info))
            elif 'image' in dataset_info.get('data_type', ''):
                matches.extend(_semantic_image_matching(dataset, entity_embedding, search_entity, dataset_info))
            else:
                matches.extend(_semantic_general_matching(dataset, entity_embedding, search_entity, dataset_info))
                
    except Exception as e:
        logging.debug(f"Semantic similarity matching failed: {str(e)}")
    
    return matches

def _apply_basic_pattern_matching(dataset, search_entity, dataset_info):
    """
    Apply basic pattern matching for entity searches with enhanced support for 
    binary data and image content.
    """
    matches = []
    dataset_name = dataset_info.get('file_path', 'unknown_dataset')
    
    logging.debug(f"Starting basic pattern matching for '{search_entity}' in {dataset_name}")
    
    try:
        # Get original metadata
        metadata = _get_general_metadata(dataset)
        
        if metadata and metadata.get('is_tabular'):
            logging.debug(f"Processing tabular data in {dataset_name}")
            # Search in DataFrame content
            df = metadata['dataframe']
            logging.debug(f"Searching across {len(df.columns)} columns: {list(df.columns)}")
            
            for col in df.columns:
                if df[col].dtype == object:  # String columns
                    logging.debug(f"Searching in string column '{col}'")
                    matches_in_col = df[df[col].str.contains(search_entity, case=False, na=False)]
                    if len(matches_in_col) > 0:
                        logging.info(f"Found {len(matches_in_col)} exact matches in column '{col}' of {dataset_name}")
                        for idx, row in matches_in_col.iterrows():
                            matches.append({
                                'type': 'exact_match',
                                'value': row[col],
                                'column': col,
                                'row_index': idx,
                                'confidence': 1.0,
                                'context': f"Found in column '{col}' at row {idx}",
                                'match_type': 'exact_match',
                                'matcher_type': 'basic'
                            })
                    else:
                        logging.debug(f"No matches found in column '{col}'")
                else:
                    logging.debug(f" Skipping non-string column '{col}' (dtype: {df[col].dtype})")
        
        elif metadata and metadata.get('is_text'):
            logging.debug(f"Processing text data in {dataset_name}")
            # Search in text content
            text = metadata.get('text_preview', str(metadata.get('original_data', '')))
            if search_entity.lower() in text.lower():
                logging.info(f"Found text match in {dataset_name}")
                matches.append({
                    'type': 'text_match',
                    'value': search_entity,
                    'confidence': 0.8,
                    'context': f"Found in text content",
                    'match_type': 'text_match',
                    'matcher_type': 'basic'
                })
            else:
                logging.debug(f"No text matches found in {dataset_name}")
        
        elif metadata and metadata.get('is_dict'):
            logging.debug(f"Processing dictionary data in {dataset_name}")
            # Search in dictionary keys and values
            original_data = metadata.get('original_data', {})
            for key, value in original_data.items():
                if search_entity.lower() in str(key).lower():
                    logging.info(f"Found key match in {dataset_name}: '{key}'")
                    matches.append({
                        'type': 'key_match',
                        'value': key,
                        'confidence': 0.9,
                        'context': f"Found as dictionary key",
                        'match_type': 'key_match',
                        'matcher_type': 'basic'
                    })
                elif search_entity.lower() in str(value).lower():
                    logging.info(f"Found value match in {dataset_name}")
                    matches.append({
                        'type': 'value_match',
                        'value': value,
                        'key': key,
                        'confidence': 0.7,
                        'context': f"Found in value for key '{key}'",
                        'match_type': 'value_match',
                        'matcher_type': 'basic'
                    })
        
        # NEW: Handle binary data
        elif metadata and metadata.get('data_type') == 'binary':
            logging.debug(f"Processing binary data in {dataset_name}")
            
            # Import the text decoder function
            from ._decode_text_from_dataset import _decode_text_from_dataset, _extract_text_from_binary_data
            
            # Get extracted text from binary data
            extracted_text = _decode_text_from_dataset(dataset, metadata)
            
            # Search for entity in extracted text
            if search_entity.lower() in extracted_text.lower():
                logging.info(f"Found binary data match in {dataset_name}")
                # Find context around the match
                match_pos = extracted_text.lower().find(search_entity.lower())
                context_start = max(0, match_pos - 30)
                context_end = min(len(extracted_text), match_pos + len(search_entity) + 30)
                context = extracted_text[context_start:context_end]
                
                matches.append({
                    'type': 'binary_data_match',
                    'value': search_entity,
                    'confidence': 0.7,
                    'context': f"Found in binary data: '...{context}...'",
                    'match_type': 'binary_match',
                    'matcher_type': 'basic'
                })
            else:
                logging.debug(f"No binary matches found in {dataset_name}")
                
        # NEW: Handle image data
        elif metadata and metadata.get('data_type') == 'image':
            logging.debug(f"Processing image data in {dataset_name}")
            
            # Import the text decoder function
            from ._decode_text_from_dataset import _decode_text_from_dataset, _extract_text_from_image_data
            
            # Get extracted text from image data
            extracted_text = _decode_text_from_dataset(dataset, metadata)
            
            # Search for entity in extracted text
            if search_entity.lower() in extracted_text.lower():
                logging.info(f"Found image data match in {dataset_name}")
                
                # Find context around the match
                match_pos = extracted_text.lower().find(search_entity.lower())
                context_start = max(0, match_pos - 30)
                context_end = min(len(extracted_text), match_pos + len(search_entity) + 30)
                context = extracted_text[context_start:context_end]
                
                matches.append({
                    'type': 'image_data_match',
                    'value': search_entity,
                    'confidence': 0.6,
                    'context': f"Found in image data: '...{context}...'",
                    'match_type': 'image_match',
                    'matcher_type': 'basic'
                })
            else:
                logging.debug(f"No image matches found in {dataset_name}")
        
        # NEW: General fallback for any other data type
        else:
            logging.debug(f"Using general text extraction for {dataset_name}")
            
            # Import the text decoder function if not already imported
            try:
                from ._decode_text_from_dataset import _decode_text_from_dataset
            except ImportError:
                logging.warning("Could not import _decode_text_from_dataset function")
                return matches
            
            # Try to extract any text content from the dataset
            try:
                extracted_text = _decode_text_from_dataset(dataset, metadata)
                
                if extracted_text and search_entity.lower() in extracted_text.lower():
                    logging.info(f"Found general data match in {dataset_name}")
                    
                    # Find context around the match
                    match_pos = extracted_text.lower().find(search_entity.lower())
                    context_start = max(0, match_pos - 30)
                    context_end = min(len(extracted_text), match_pos + len(search_entity) + 30)
                    context = extracted_text[context_start:context_end]
                    
                    matches.append({
                        'type': 'general_data_match',
                        'value': search_entity,
                        'confidence': 0.5,
                        'context': f"Found in data content: '...{context}...'",
                        'match_type': 'general_match',
                        'matcher_type': 'basic'
                    })
            except Exception as e:
                logging.debug(f"General text extraction failed: {e}")
    
    except Exception as e:
        logging.debug(f"Pattern matching failed: {e}")
    
    return matches

def _interpret_semantic_coordinates(coords, dataset_info, metadata):
    """Interpret 16D semantic coordinates with meaningful labels."""
    if len(coords) < 16:
        return {}
    
    interpretations = {
        'structural_complexity': coords[0],
        'sparsity_ratio': coords[1], 
        'symmetry_score': coords[2],
        'value_distribution': coords[3],
        'temporal_patterns': coords[4],
        'hierarchical_structure': coords[5],
        'clustering_tendency': coords[6],
        'contextual_coherence': coords[7],
        'data_density': coords[8],
        'pattern_regularity': coords[9],
        'semantic_richness': coords[10],
        'cross_references': coords[11],
        'entity_diversity': coords[12],
        'relationship_strength': coords[13],
        'domain_specificity': coords[14],
        'information_entropy': coords[15]
    }
    
    # Add context-specific interpretations
    if metadata:
        if metadata.get('is_tabular'):
            interpretations['column_diversity'] = coords[8]
            interpretations['row_patterns'] = coords[9]
        elif metadata.get('is_text'):
            interpretations['vocabulary_richness'] = coords[10]
            interpretations['linguistic_complexity'] = coords[11]
        elif metadata.get('data_type') == 'image':
            interpretations['visual_complexity'] = coords[6]
            interpretations['color_distribution'] = coords[7]
    
    return interpretations

def _extract_contextual_info(metadata, search_entity):
    """Extract rich contextual information about the dataset and search entity."""
    context = {
        'data_source': metadata.get('file_path', 'Unknown') if metadata else 'Unknown',
        'data_format': metadata.get('file_format', 'Unknown') if metadata else 'Unknown',
        'data_type': metadata.get('data_type', 'Unknown') if metadata else 'Unknown',
        'search_entity': search_entity if search_entity else 'None specified'
    }
    
    if not metadata:
        return context
    
    # Get basic shape and size information
    shape = metadata.get('shape', ())
    context.update({
        'array_shape': shape,
        'total_elements': np.prod(shape) if shape else 0,
        'dimensionality': len(shape) if shape else 0,
        'file_size_bytes': metadata.get('file_size', 0)
    })
    
    # Extract type-specific contextual information
    data_type = metadata.get('data_type', 'unknown')
    file_format = metadata.get('file_format', 'unknown')
    
    # Tabular data (CSV, TSV, Excel, etc.)
    if metadata.get('is_tabular') or data_type == 'tabular':
        context.update({
            'content_type': 'tabular_data',
            'total_columns': len(metadata.get('columns', [])),
            'column_names': metadata.get('columns', []),
            'table_shape': metadata.get('shape', (0, 0)),
            'delimiter': metadata.get('delimiter', 'Unknown'),
            'has_dataframe': 'dataframe' in metadata
        })
        
        # Add column type analysis if dataframe is available
        if 'dataframe' in metadata:
            df = metadata['dataframe']
            context.update({
                'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
                'text_columns': len(df.select_dtypes(include=['object']).columns),
                'unique_values_per_column': {col: df[col].nunique() for col in df.columns[:10]}
            })
    
    # Text data
    elif metadata.get('is_text') or data_type == 'text':
        context.update({
            'content_type': 'text_data',
            'text_length': metadata.get('text_length', 0),
            'encoding': metadata.get('text_encoding', 'Unknown'),
            'text_preview': metadata.get('text_preview', '')[:200],
            'is_structured_text': metadata.get('is_structured', False)
        })
    
    # Dictionary/JSON data
    elif metadata.get('is_dict') or data_type == 'json':
        original_data = metadata.get('original_data', {})
        context.update({
            'content_type': 'structured_data',
            'dict_keys': list(metadata.get('keys', []))[:20],  # First 20 keys
            'total_keys': len(metadata.get('keys', [])),
            'json_type': metadata.get('json_type', 'Unknown'),
            'nested_structure': _analyze_json_structure(original_data) if isinstance(original_data, dict) else None
        })
    
    # NumPy arrays
    elif file_format == 'numpy' or data_type == 'numpy':
        context.update({
            'content_type': 'numpy_array',
            'array_dtype': metadata.get('original_dtype', 'Unknown'),
            'is_sparse': _check_sparsity(shape),
            'memory_layout': 'contiguous' if metadata.get('is_contiguous') else 'strided'
        })
    
    # PyTorch tensors
    elif file_format == 'pytorch' or data_type == 'pytorch':
        context.update({
            'content_type': 'pytorch_tensor',
            'tensor_device': metadata.get('tensor_device', 'Unknown'),
            'tensor_dtype': metadata.get('tensor_dtype', 'Unknown'),
            'requires_grad': metadata.get('requires_grad', False),
            'is_cuda_tensor': 'cuda' in str(metadata.get('tensor_device', ''))
        })
    
    # HDF5 files
    elif file_format == 'hdf5' or data_type == 'hdf5':
        context.update({
            'content_type': 'hdf5_dataset',
            'datasets': metadata.get('datasets', []),
            'total_datasets': len(metadata.get('datasets', [])),
            'hierarchical_structure': True
        })
    
    # MATLAB files
    elif file_format == 'matlab' or data_type == 'matlab':
        context.update({
            'content_type': 'matlab_data',
            'variables': metadata.get('variables', []),
            'total_variables': len(metadata.get('variables', [])),
            'matlab_version': metadata.get('matlab_version', 'Unknown')
        })
    
    # NetCDF files
    elif file_format == 'netcdf' or data_type == 'netcdf':
        context.update({
            'content_type': 'netcdf_dataset',
            'variables': metadata.get('variables', []),
            'global_attributes': metadata.get('global_attributes', {}),
            'is_scientific_data': True,
            'coordinate_system': _extract_coordinate_info(metadata.get('variables', {}))
        })
    
    # Image data (TIFF, NIfTI, etc.)
    elif file_format in ['tiff', 'nifti'] or 'image' in data_type:
        context.update({
            'content_type': 'image_data',
            'image_dimensions': len(shape),
            'is_medical_image': file_format == 'nifti',
            'header_info': metadata.get('header_info', {}),
            'color_channels': shape[-1] if len(shape) >= 3 and shape[-1] <= 4 else 1
        })
    
    # Zarr arrays
    elif file_format in ['zarr', 'zarr_group'] or data_type == 'zarr':
        context.update({
            'content_type': 'zarr_array',
            'chunks': metadata.get('chunks', 'Unknown'),
            'compressor': metadata.get('compressor', 'None'),
            'is_chunked': metadata.get('chunks') is not None,
            'arrays': metadata.get('arrays', []) if file_format == 'zarr_group' else []
        })
    
    # Pickle files
    elif file_format == 'pickle' or data_type == 'pickle':
        context.update({
            'content_type': 'pickled_object',
            'original_type': metadata.get('original_type', 'Unknown'),
            'is_serialized_model': 'model' in str(metadata.get('original_type', '')).lower()
        })
    
    # Binary data
    elif data_type == 'binary':
        context.update({
            'content_type': 'binary_data',
            'binary_size': metadata.get('binary_size', 0),
            'detected_encoding': _detect_binary_type(metadata.get('original_data', b''))
        })
    
    # Unknown or mixed types
    else:
        context.update({
            'content_type': 'unknown_data',
            'detected_as': metadata.get('detected_as', 'unknown'),
            'original_extension': metadata.get('original_extension', ''),
            'fallback_interpretation': _suggest_data_interpretation(metadata)
        })
    
    # Add search entity context if provided
    if search_entity:
        context['entity_analysis'] = {
            'entity_length': len(search_entity),
            'entity_type': _classify_entity_type(search_entity),
            'is_numeric': search_entity.replace('.', '').replace('-', '').isdigit(),
            'contains_special_chars': bool(re.search(r'[^a-zA-Z0-9\s]', search_entity))
        }
    
    # Add data quality indicators
    context['quality_indicators'] = {
        'has_metadata': bool(metadata),
        'metadata_completeness': _calculate_metadata_completeness(metadata),
        'interpretability_score': _calculate_interpretability_score(context, metadata)
    }
    
    return context

def _find_local_contextual_relationships(dataset, search_entity, metadata, dataset_info):
    """Find local relationships with contextual entity names instead of numbers across all file types."""
    relationships = {
        'significant_elements': [],
        'contextual_connections': [],
        'semantic_clusters': [],
        'data_characteristics': {}
    }
    
    if not metadata:
        # Add summary even when no metadata is provided
        relationships['summary'] = {
            'total_elements_found': 0,
            'total_connections': 0,
            'search_entity': search_entity,
            'data_type_searched': 'unknown'
        }
        return relationships

    try:
        data_type = metadata.get('data_type', 'unknown')
        file_format = metadata.get('file_format', 'unknown')
        
        # NEW: Check if we should use registered entities
        matrix_entities = _get_entities_in_matrix(dataset)
        use_general_analysis = search_entity in ["general_analysis", "connection_analysis", "entity_extraction"]
        
        # If using general analysis or no specific entity found, extract representative elements
        if use_general_analysis or not any(search_entity.lower() in str(entity_info.get('name', '')).lower() 
                                         for entity_info in matrix_entities.values()):
            logging.debug(f"Using general analysis approach for dataset with {len(matrix_entities)} registered entities")
            
            # Use registered entities if available
            if matrix_entities:
                for entity_key, entity_data in list(matrix_entities.items())[:10]:  # Limit to 10 entities
                    entity_info = entity_data.get('info', {})
                    relationships['significant_elements'].append({
                        'entity_name': entity_info.get('name', entity_key),
                        'entity_id': entity_key,
                        'entity_type': entity_info.get('type', 'unknown'),
                        'source_file': entity_info.get('source_file', ''),
                        'extraction_method': entity_info.get('extraction_method', 'registered'),
                        'match_type': 'registered_entity',
                        'coordinates': entity_data.get('coordinates', 'not_specified')
                    })
                    
                    # Create contextual connections between entities
                    for other_key, other_data in matrix_entities.items():
                        if entity_key != other_key:
                            other_info = other_data.get('info', {})
                            relationships['contextual_connections'].append({
                                'primary_entity': entity_info.get('name', entity_key),
                                'connected_entity': other_info.get('name', other_key),
                                'connection_type': 'entity_co_occurrence',
                                'relationship_context': f"Both entities registered in same dataset"
                            })
                            
                            # Limit connections to avoid excessive data
                            if len(relationships['contextual_connections']) >= 20:
                                break
                    
                    if len(relationships['contextual_connections']) >= 20:
                        break
        
        # Tabular data (CSV, TSV, Excel, etc.)
        if metadata.get('is_tabular') or data_type == 'tabular':
            df = metadata.get('dataframe')
            if df is not None:
                relationships['data_characteristics'] = {
                    'type': 'tabular',
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns)
                }
                
                logging.debug(f"Searching for '{search_entity}' in tabular data with {len(df)} rows and {len(df.columns)} columns")
                
                # Find rows/columns related to the search entity
                found_matches = False
                for col_idx, col in enumerate(df.columns):
                    # Check if column is string type (object) AND doesn't contain non-string values
                    if df[col].dtype == object:
                        try:
                            # Safely check if column can use str accessor
                            if not df[col].dropna().map(lambda x: not isinstance(x, str)).any():
                                matches = df[df[col].str.contains(search_entity, case=False, na=False)]
                                
                                if len(matches) > 0:
                                    found_matches = True
                                    logging.debug(f"Found {len(matches)} matches in column '{col}'")
                                    
                                    for row_idx, row in matches.iterrows():
                                        element = {
                                            'entity_name': str(row[col]),
                                            'source_column': col,
                                            'row_index': int(row_idx),
                                            'match_type': 'exact_string_match',
                                            'related_data': {}
                                        }
                                    
                                        # Add related data from the same row
                                        for other_col in df.columns:
                                            if other_col != col:
                                                try:
                                                    val = row[other_col]
                                                    # Convert to string if it's not already
                                                    element['related_data'][other_col] = str(val) if val is not None else ""
                                                except:
                                                    element['related_data'][other_col] = "N/A"
                                    
                                        relationships['significant_elements'].append(element)
                                        
                                        # Find contextual connections
                                        for other_col in df.columns:
                                            if other_col != col and df[other_col].dtype == object:
                                                try:
                                                    related_value = row[other_col]
                                                    if pd.notna(related_value) and str(related_value).strip():
                                                        relationships['contextual_connections'].append({
                                                            'primary_entity': str(row[col]),
                                                            'connected_entity': str(related_value),
                                                            'connection_type': f"{col} → {other_col}",
                                                            'relationship_context': f"Co-occurring in row {row_idx}"
                                                        })
                                                except:
                                                    pass
                                    
                                        # Limit the number of matches to avoid excessive data
                                        if len(relationships['significant_elements']) >= 50:
                                            break
                        except Exception as e:
                            logging.debug(f"Error searching in column '{col}': {str(e)}")
                            continue
                
                # If no direct matches found, try partial matches in key columns
                if not found_matches:
                    logging.debug(f"No direct matches found for '{search_entity}', trying partial matches")
                    
                    # Look for similar entities or meaningful data in first few columns
                    for col_idx, col in enumerate(df.columns[:5]):  # Check first 5 columns
                        if df[col].dtype == object:  # String columns
                            try:
                                # Check if column contains only string values before processing
                                if not df[col].dropna().map(lambda x: not isinstance(x, str)).any():
                                    # Get unique values and find similar ones
                                    unique_values = df[col].dropna().unique()
                                    for val in unique_values[:20]:  # Limit to first 20 unique values
                                        val_str = str(val)
                                        if len(val_str) > 2:  # Skip very short values
                                            element = {
                                                'entity_name': val_str,
                                                'source_column': col,
                                                'row_index': 'multiple',
                                                'match_type': 'representative_value',
                                                'occurrences': int(sum(df[col] == val)),
                                                'related_data': {}
                                            }
                                            
                                            # Get a sample row with this value
                                            sample_row = df[df[col] == val].iloc[0]
                                            for other_col in df.columns:
                                                if other_col != col:
                                                    try:
                                                        element['related_data'][other_col] = str(sample_row[other_col])
                                                    except:
                                                        element['related_data'][other_col] = "N/A"
                                            
                                            relationships['significant_elements'].append(element)
                                            
                                            if len(relationships['significant_elements']) >= 20:
                                                break
                            except Exception as e:
                                logging.debug(f"Error getting representative values from column '{col}': {str(e)}")
                                continue
                
                logging.debug(f"Found {len(relationships['significant_elements'])} significant elements")
        
        # Text data
        elif metadata.get('is_text') or data_type == 'text':
            text = str(metadata.get('original_data', ''))
            if not text:
                text = metadata.get('text_preview', '')
            
            relationships['data_characteristics'] = {
                'type': 'text',
                'length': len(text),
                'lines': len(text.split('\n')),
                'encoding': metadata.get('text_encoding', 'Unknown')
            }
            
            lines = text.split('\n')
            for line_idx, line in enumerate(lines):
                if search_entity.lower() in line.lower():
                    # Find word boundaries around the entity
                    words = line.split()
                    entity_positions = []
                    for word_idx, word in enumerate(words):
                        if search_entity.lower() in word.lower():
                            entity_positions.append(word_idx)
                    
                    relationships['significant_elements'].append({
                        'entity_name': search_entity,
                        'context_line': line.strip(),
                        'line_number': line_idx,
                        'word_positions': entity_positions,
                        'surrounding_context': lines[max(0, line_idx-2):line_idx+3],
                        'match_type': 'text_substring'
                    })
                    
                    # Find contextual connections (nearby meaningful words)
                    for pos in entity_positions:
                        context_words = words[max(0, pos-3):pos+4]
                        relationships['contextual_connections'].append({
                            'primary_entity': search_entity,
                            'context_words': context_words,
                            'line_number': line_idx,
                            'connection_type': 'contextual_proximity'
                        })
        
        # Dictionary/JSON data
        elif metadata.get('is_dict') or data_type == 'json':
            original_data = metadata.get('original_data', {})
            
            relationships['data_characteristics'] = {
                'type': 'structured_json',
                'total_keys': len(original_data) if isinstance(original_data, dict) else 0,
                'json_type': metadata.get('json_type', 'Unknown'),
                'nested_structure': metadata.get('nested_structure', {})
            }
            
            def search_nested_dict(data, path="root"):
                """Recursively search nested dictionary structures."""
                if isinstance(data, dict):
                    for key, value in data.items():
                        current_path = f"{path}.{key}"
                        
                        # Check key match
                        if search_entity.lower() in str(key).lower():
                            relationships['significant_elements'].append({
                                'entity_name': search_entity,
                                'found_in': 'dictionary_key',
                                'key_path': current_path,
                                'key_value': key,
                                'associated_value': value,
                                'match_type': 'key_match'
                            })
                        
                        # Check value match
                        if search_entity.lower() in str(value).lower():
                            relationships['significant_elements'].append({
                                'entity_name': search_entity,
                                'found_in': 'dictionary_value',
                                'key_path': current_path,
                                'key_name': key,
                                'matching_value': value,
                                'match_type': 'value_match'
                            })
                        
                        # Recurse for nested structures
                        if isinstance(value, (dict, list)):
                            search_nested_dict(value, current_path)
                
                elif isinstance(data, list):
                    for idx, item in enumerate(data):
                        if search_entity.lower() in str(item).lower():
                            relationships['significant_elements'].append({
                                'entity_name': search_entity,
                                'found_in': 'list_item',
                                'list_path': f"{path}[{idx}]",
                                'list_index': idx,
                                'matching_item': item,
                                'match_type': 'list_item_match'
                            })
                        
                        # Recurse for nested structures
                        if isinstance(item, (dict, list)):
                            search_nested_dict(item, f"{path}[{idx}]")
            
            search_nested_dict(original_data)
        
        # NumPy arrays
        elif file_format == 'numpy' or data_type == 'numpy':
            relationships['data_characteristics'] = {
                'type': 'numpy_array',
                'shape': metadata.get('shape', ()),
                'dtype': metadata.get('original_dtype', 'Unknown'),
                'total_elements': np.prod(metadata.get('shape', (0,)))
            }
            
            # For numpy arrays, look for numerical patterns if search_entity is numeric
            if search_entity.replace('.', '').replace('-', '').isdigit():
                search_value = float(search_entity)
                # Find approximate matches in the array
                if hasattr(dataset, 'shape') and dataset.size < 1000000:  # Limit for performance
                    matches = np.where(np.abs(dataset - search_value) < 0.001)
                    if len(matches[0]) > 0:
                        for i in range(min(10, len(matches[0]))):  # Limit to first 10 matches
                            coord = tuple(m[i] for m in matches)
                            relationships['significant_elements'].append({
                                'entity_name': search_entity,
                                'found_at_coordinates': coord,
                                'actual_value': float(dataset[coord]),
                                'match_type': 'numerical_approximation',
                                'difference': abs(float(dataset[coord]) - search_value)
                            })
        
        # PyTorch tensors
        elif file_format == 'pytorch' or data_type == 'pytorch':
            relationships['data_characteristics'] = {
                'type': 'pytorch_tensor',
                'shape': metadata.get('shape', ()),
                'device': metadata.get('tensor_device', 'Unknown'),
                'dtype': metadata.get('tensor_dtype', 'Unknown'),
                'requires_grad': metadata.get('requires_grad', False)
            }
            
            # Similar to NumPy for numerical searches
            if search_entity.replace('.', '').replace('-', '').isdigit():
                search_value = float(search_entity)
                relationships['significant_elements'].append({
                    'entity_name': search_entity,
                    'search_note': f'Searched for numerical value {search_value} in PyTorch tensor',
                    'tensor_info': f"Shape: {metadata.get('shape', '')}, Device: {metadata.get('tensor_device', 'Unknown')}",
                    'match_type': 'tensor_numerical_search'
                })
        
        # HDF5 files
        elif file_format == 'hdf5' or data_type == 'hdf5':
            datasets_info = metadata.get('datasets', [])
            relationships['data_characteristics'] = {
                'type': 'hdf5_dataset',
                'total_datasets': len(datasets_info),
                'dataset_names': datasets_info
            }
            
            # Search in dataset names
            for dataset_name in datasets_info:
                if search_entity.lower() in dataset_name.lower():
                    relationships['significant_elements'].append({
                        'entity_name': search_entity,
                        'found_in': 'hdf5_dataset_name',
                        'dataset_name': dataset_name,
                        'match_type': 'dataset_name_match'
                    })
        
        # MATLAB files
        elif file_format == 'matlab' or data_type == 'matlab':
            variables = metadata.get('variables', [])
            relationships['data_characteristics'] = {
                'type': 'matlab_data',
                'total_variables': len(variables),
                'variable_names': variables
            }
            
            # Search in variable names
            for var_name in variables:
                if search_entity.lower() in var_name.lower():
                    relationships['significant_elements'].append({
                        'entity_name': search_entity,
                        'found_in': 'matlab_variable_name',
                        'variable_name': var_name,
                        'match_type': 'variable_name_match'
                    })
        
        # NetCDF files
        elif file_format == 'netcdf' or data_type == 'netcdf':
            variables = metadata.get('variables', {})
            global_attrs = metadata.get('global_attributes', {})
            
            relationships['data_characteristics'] = {
                'type': 'netcdf_dataset',
                'total_variables': len(variables),
                'variable_names': list(variables.keys()),
                'has_global_attributes': len(global_attrs) > 0
            }
            
            # Search in variable names and attributes
            for var_name, var_info in variables.items():
                if search_entity.lower() in var_name.lower():
                    relationships['significant_elements'].append({
                        'entity_name': search_entity,
                        'found_in': 'netcdf_variable_name',
                        'variable_name': var_name,
                        'variable_info': var_info,
                        'match_type': 'variable_name_match'
                    })
            
            # Search in global attributes
            for attr_name, attr_value in global_attrs.items():
                if search_entity.lower() in str(attr_name).lower() or search_entity.lower() in str(attr_value).lower():
                    relationships['significant_elements'].append({
                        'entity_name': search_entity,
                        'found_in': 'netcdf_global_attribute',
                        'attribute_name': attr_name,
                        'attribute_value': attr_value,
                        'match_type': 'attribute_match'
                    })
        
        # Image data
        elif file_format in ['tiff', 'nifti'] or 'image' in data_type:
            relationships['data_characteristics'] = {
                'type': 'image_data',
                'image_shape': metadata.get('shape', ()),
                'is_medical_image': file_format == 'nifti',
                'color_channels': metadata.get('color_channels', 1),
                'header_available': bool(metadata.get('header_info'))
            }
            
            # For image data, search in header information if available
            header_info = metadata.get('header_info', {})
            for key, value in header_info.items():
                if search_entity.lower() in str(key).lower() or search_entity.lower() in str(value).lower():
                    relationships['significant_elements'].append({
                        'entity_name': search_entity,
                        'found_in': 'image_header',
                        'header_field': key,
                        'header_value': value,
                        'match_type': 'header_metadata_match'
                    })
        
        # Zarr arrays
        elif file_format in ['zarr', 'zarr_group'] or data_type == 'zarr':
            relationships['data_characteristics'] = {
                'type': 'zarr_array',
                'is_chunked': metadata.get('chunks') is not None,
                'compressor': metadata.get('compressor', 'None'),
                'array_names': metadata.get('arrays', []) if file_format == 'zarr_group' else []
            }
            
            # Search in array names for zarr groups
            array_names = metadata.get('arrays', [])
            for array_name in array_names:
                if search_entity.lower() in array_name.lower():
                    relationships['significant_elements'].append({
                        'entity_name': search_entity,
                        'found_in': 'zarr_array_name',
                        'array_name': array_name,
                        'match_type': 'array_name_match'
                    })
        
        # Pickle files
        elif file_format == 'pickle' or data_type == 'pickle':
            relationships['data_characteristics'] = {
                'type': 'pickled_object',
                'original_type': metadata.get('original_type', 'Unknown'),
                'is_model': metadata.get('is_serialized_model', False)
            }
            
            # Limited search capabilities for pickle files
            relationships['significant_elements'].append({
                'entity_name': search_entity,
                'search_note': f'Limited search capability for pickled {metadata.get("original_type", "object")}',
                'match_type': 'pickle_limited_search'
            })
        
        # Binary data
        elif data_type == 'binary':
            binary_size = metadata.get('binary_size', 0)
            detected_type = metadata.get('detected_encoding', 'unknown')
            
            relationships['data_characteristics'] = {
                'type': 'binary_data',
                'size_bytes': binary_size,
                'detected_type': detected_type
            }
            
            # Very limited search for binary data
            if search_entity.encode() in metadata.get('original_data', b'')[:10000]:  # Search first 10KB
                relationships['significant_elements'].append({
                    'entity_name': search_entity,
                    'found_in': 'binary_content',
                    'detected_type': detected_type,
                    'match_type': 'binary_byte_sequence'
                })
        
        # Unknown or unsupported types
        else:
            relationships['data_characteristics'] = {
                'type': 'unknown_or_unsupported',
                'detected_as': metadata.get('detected_as', 'unknown'),
                'file_format': file_format,
                'data_type': data_type
            }
            
            relationships['significant_elements'].append({
                'entity_name': search_entity,
                'search_note': f'Search not fully supported for {data_type}/{file_format}',
                'suggestions': metadata.get('fallback_interpretation', ['Consider manual inspection']),
                'match_type': 'unsupported_format'
            })
    
    except Exception as e:
        logging.debug(f"Error finding local relationships: {e}")
        relationships['error'] = str(e)
    
    # Add summary statistics including registered entity information
    registered_entities_count = len(matrix_entities) if 'matrix_entities' in locals() else 0
    
    relationships['summary'] = {
        'total_elements_found': len(relationships['significant_elements']),
        'total_connections': len(relationships['contextual_connections']),
        'registered_entities_count': registered_entities_count,
        'search_entity': search_entity,
        'data_type_searched': relationships['data_characteristics'].get('type', 'unknown'),
        'used_general_analysis': use_general_analysis if 'use_general_analysis' in locals() else False
    }
    
    return relationships
  

def _analyze_json_structure(data, max_depth=3, current_depth=0):
    """Analyze the structure of JSON data."""
    if current_depth >= max_depth:
        return {'truncated': True, 'max_depth_reached': max_depth}
    
    structure = {}
    
    if isinstance(data, dict):
        structure['type'] = 'object'
        structure['keys_count'] = len(data)
        structure['keys_sample'] = list(data.keys())[:10]
        
        # Analyze value types
        value_types = {}
        for key, value in list(data.items())[:10]:
            value_type = type(value).__name__
            if value_type in value_types:
                value_types[value_type] += 1
            else:
                value_types[value_type] = 1
        structure['value_types'] = value_types
        
        # Recursively analyze nested structures
        if current_depth < max_depth - 1:
            nested_analysis = {}
            for key, value in list(data.items())[:5]:  # Limit to first 5 for performance
                if isinstance(value, (dict, list)):
                    nested_analysis[key] = _analyze_json_structure(value, max_depth, current_depth + 1)
            if nested_analysis:
                structure['nested_structures'] = nested_analysis
    
    elif isinstance(data, list):
        structure['type'] = 'array'
        structure['length'] = len(data)
        
        if data:
            # Analyze element types
            element_types = {}
            for item in data[:20]:  # Sample first 20 items
                item_type = type(item).__name__
                if item_type in element_types:
                    element_types[item_type] += 1
                else:
                    element_types[item_type] = 1
            structure['element_types'] = element_types
            
            # Analyze first element if it's complex
            if isinstance(data[0], (dict, list)) and current_depth < max_depth - 1:
                structure['element_structure'] = _analyze_json_structure(data[0], max_depth, current_depth + 1)
    
    else:
        structure['type'] = 'primitive'
        structure['value_type'] = type(data).__name__
    
    return structure

def _check_sparsity(shape):
    """Check if array dimensions suggest sparsity."""
    if not shape or len(shape) < 2:
        return False
    
    # Large arrays with many dimensions might be sparse
    total_elements = np.prod(shape)
    return total_elements > 100000 and len(shape) >= 2

def _extract_coordinate_info(variables):
    """Extract coordinate system information from NetCDF variables."""
    coord_info = {}
    
    common_coords = ['lat', 'lon', 'latitude', 'longitude', 'time', 'x', 'y', 'z']
    
    for var_name, var_info in variables.items():
        if any(coord in var_name.lower() for coord in common_coords):
            coord_info[var_name] = {
                'dimensions': var_info.get('dimensions', []),
                'shape': var_info.get('shape', ()),
                'is_coordinate': True
            }
    
    return coord_info

def _detect_binary_type(binary_data):
    """Detect the type of binary data based on magic numbers."""
    if not binary_data or len(binary_data) < 4:
        return 'unknown'
    
    # Check common binary file signatures
    header = binary_data[:8]
    
    if header.startswith(b'\x89PNG'):
        return 'PNG image'
    elif header.startswith(b'\xff\xd8'):
        return 'JPEG image'
    elif header.startswith(b'GIF8'):
        return 'GIF image'
    elif header.startswith(b'BM'):
        return 'BMP image'
    elif header.startswith(b'PK'):
        return 'ZIP/Office document'
    elif header.startswith(b'\x50\x4b'):
        return 'ZIP archive'
    elif b'PDF' in header[:10]:
        return 'PDF document'
    else:
        return 'unknown binary'

def _suggest_data_interpretation(metadata):
    """Suggest how unknown data might be interpreted."""
    suggestions = []
    
    file_path = metadata.get('file_path', '')
    file_ext = os.path.splitext(file_path)[1].lower()
    shape = metadata.get('shape', ())
    
    # Based on file extension
    if file_ext in ['.dat', '.bin']:
        suggestions.append('Raw binary data - may need custom parser')
    elif file_ext in ['.log', '.out']:
        suggestions.append('Log file - consider text processing')
    elif not file_ext:
        suggestions.append('No extension - examine content manually')
    
    # Based on shape
    if len(shape) == 2 and shape[0] > shape[1]:
        suggestions.append('Tabular data with more rows than columns')
    elif len(shape) == 3:
        suggestions.append('3D data - could be image stack or volumetric data')
    elif len(shape) > 3:
        suggestions.append('High-dimensional data - consider dimensionality reduction')
    
    return suggestions

def _classify_entity_type(entity):
    """Classify the type of search entity."""
    if entity.replace('.', '').replace('-', '').isdigit():
        return 'numeric'
    elif entity.isupper():
        return 'acronym_or_code'
    elif any(char.isdigit() for char in entity) and any(char.isalpha() for char in entity):
        return 'alphanumeric_code'
    elif ' ' in entity:
        return 'phrase'
    elif entity.isalpha():
        return 'word'
    else:
        return 'complex_pattern'

def _calculate_metadata_completeness(metadata):
    """Calculate how complete the metadata is (0.0 to 1.0)."""
    if not metadata:
        return 0.0
    
    essential_fields = ['file_path', 'data_type', 'shape', 'file_format']
    present_fields = sum(1 for field in essential_fields if metadata.get(field))
    
    completeness = present_fields / len(essential_fields)
    
    # Bonus for having original data preserved
    if 'original_data' in metadata:
        completeness += 0.1
    
    # Bonus for type-specific metadata
    if metadata.get('is_tabular') and 'columns' in metadata:
        completeness += 0.1
    elif metadata.get('is_text') and 'text_length' in metadata:
        completeness += 0.1
    
    return min(1.0, completeness)

def _calculate_interpretability_score(context, metadata):
    """Calculate how interpretable the data is (0.0 to 1.0)."""
    score = 0.0
    
    # Base score for having context
    if context.get('content_type') != 'unknown_data':
        score += 0.3
    
    # Bonus for structured data
    if context.get('content_type') in ['tabular_data', 'structured_data']:
        score += 0.3
    
    # Bonus for having column names or keys
    if context.get('column_names') or context.get('dict_keys'):
        score += 0.2
    
    # Bonus for text data with preview
    if context.get('content_type') == 'text_data' and context.get('text_preview'):
        score += 0.2
    
    # Penalty for binary or unknown data
    if context.get('content_type') in ['binary_data', 'unknown_data']:
        score -= 0.2
    
    return max(0.0, min(1.0, score))


# Registry management functions for entity matchers

def _get_registered_entity_matchers(data_type):
    """Get all registered entity matchers for a specific data type."""
    entity_matchers = {}
    
    try:
        from pathlib import Path
        import json
        
        registry_dir = Path.home() / '.tensorpack' / 'transforms' / data_type
        
        if not registry_dir.exists():
            return entity_matchers
        
        # Load all entity matching transformations
        for metadata_file in registry_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Check if this is an entity matching transformation
                if metadata.get('source_info', {}).get('operation_type') == 'entity_matching':
                    matcher_name = metadata['name']
                    
                    # Load the actual function
                    if metadata['source_info']['type'] == 'python':
                        source_file = registry_dir / f"{matcher_name}.py"
                        if source_file.exists():
                            try:
                                matcher_func = _load_entity_matcher_function(
                                    str(source_file), 
                                    metadata['source_info'].get('function_name')
                                )
                                entity_matchers[matcher_name] = matcher_func
                                logging.debug(f"Loaded entity matcher: {matcher_name}")
                            except Exception as e:
                                logging.warning(f"Failed to load entity matcher {matcher_name}: {e}")
                
            except Exception as e:
                logging.warning(f"Failed to read metadata from {metadata_file}: {e}")
    
    except Exception as e:
        logging.warning(f"Failed to load entity matchers: {e}")
    
    return entity_matchers

def _load_entity_matcher_function(file_path, function_name=None):
    """Load an entity matcher function from a Python file."""
    import importlib.util
    import inspect
    
    # Load the module
    spec = importlib.util.spec_from_file_location("entity_matcher", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Get the matcher function
    if function_name:
        if not hasattr(module, function_name):
            raise AttributeError(f"Function {function_name} not found in {file_path}")
        matcher_func = getattr(module, function_name)
    else:
        # Look for common entity matcher function names
        common_names = ['match_entities', 'find_entities', 'entity_matcher', 'match']
        matcher_func = None
        for name in common_names:
            if hasattr(module, name):
                matcher_func = getattr(module, name)
                break
        
        if matcher_func is None:
            raise AttributeError(f"No entity matcher function found in {file_path}")
    
    # Validate function signature
    sig = inspect.signature(matcher_func)
    if len(sig.parameters) < 3:
        raise ValueError("Entity matcher function must accept at least 3 parameters: (dataset, search_entity, dataset_info)")
    
    return matcher_func

# Helper functions for advanced matching techniques

def _nlp_text_entity_matching(dataset, search_entity, dataset_info):
    """Use NLP techniques to find entities in text data."""
    matches = []
    
    try:
        # If dataset is text-based, use text processing
        if hasattr(dataset, 'shape') and len(dataset.shape) == 2:
            # Assume text is encoded in the dataset
            text_data = _decode_text_from_dataset(dataset)
            
            # Simple regex matching
            import re
            pattern = re.compile(re.escape(search_entity), re.IGNORECASE)
            
            for i, text in enumerate(text_data):
                if isinstance(text, str) and pattern.search(text):
                    matches.append({
                        'type': 'text_match',
                        'location': f'text_row_{i}',
                        'confidence': 0.8,
                        'description': f'Found exact text match for "{search_entity}"',
                        'matcher': 'nlp_text',
                        'matcher_type': 'nlp'
                    })
    
    except Exception as e:
        logging.debug(f"NLP text matching failed: {str(e)}")
    
    return matches

def _spacy_entity_matching(dataset, search_entity, dataset_info):
    """Use spaCy for named entity recognition and matching."""
    matches = []
    
    try:
        import spacy
        
        # Try to load English model
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback to basic model if not available
            return matches
        
        # Extract text data from dataset
        text_data = _extract_text_for_nlp(dataset, dataset_info)
        
        for i, text in enumerate(text_data):
            if isinstance(text, str) and len(text.strip()) > 0:
                doc = nlp(text)
                
                # Look for entity matches
                for ent in doc.ents:
                    if search_entity.lower() in ent.text.lower():
                        matches.append({
                            'type': 'named_entity',
                            'location': f'text_position_{i}',
                            'confidence': 0.9,
                            'description': f'Found named entity match: {ent.text} ({ent.label_})',
                            'entity_type': ent.label_,
                            'matcher': 'spacy_ner',
                            'matcher_type': 'nlp'
                        })
    
    except Exception as e:
        logging.debug(f"spaCy entity matching failed: {str(e)}")
    
    return matches

def _get_entity_embedding(search_entity):
    """Get semantic embedding for the search entity."""
    try:
        # Try sentence transformers first
        try:
            model = create_silent_sentence_transformer()
            embedding = model.encode([search_entity], show_progress_bar=False)
            return embedding[0]
        except ImportError:
            pass
        
        # Fallback to simple word embedding
        import hashlib
        import numpy as np
        
        # Create a deterministic embedding from the entity
        hash_bytes = hashlib.sha256(search_entity.encode()).digest()
        embedding = np.frombuffer(hash_bytes, dtype=np.uint8)[:64].astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
        
    except Exception as e:
        logging.debug(f"Entity embedding generation failed: {str(e)}")
        return None


def _nlp_string_entity_matching(dataset, search_entity, dataset_info):
    """Use NLP techniques to find entities in string-like data arrays."""
    matches = []
    
    try:
        # Convert dataset to string format if it contains string-like data
        if hasattr(dataset, 'dtype') and dataset.dtype.kind in ['U', 'S', 'a']:
            # Handle different array shapes
            if dataset.ndim == 1:
                string_data = dataset.astype(str)
            elif dataset.ndim == 2:
                # Flatten 2D string arrays
                string_data = dataset.flatten().astype(str)
            else:
                # For higher dimensions, flatten completely
                string_data = dataset.flatten().astype(str)
            
            import re
            # Create case-insensitive pattern
            pattern = re.compile(re.escape(search_entity), re.IGNORECASE)
            
            for i, text_item in enumerate(string_data):
                if isinstance(text_item, (str, bytes)):
                    # Convert bytes to string if necessary
                    if isinstance(text_item, bytes):
                        try:
                            text_item = text_item.decode('utf-8', errors='ignore')
                        except:
                            continue
                    
                    # Search for exact matches
                    if pattern.search(text_item):
                        matches.append({
                            'type': 'string_exact_match',
                            'location': f'string_index_{i}',
                            'confidence': 0.95,
                            'description': f'Found exact string match for "{search_entity}" in: "{text_item[:50]}..."',
                            'matched_text': text_item,
                            'matcher': 'nlp_string',
                            'matcher_type': 'nlp'
                        })
                    
                    # Search for partial matches (word boundaries)
                    word_pattern = re.compile(r'\b' + re.escape(search_entity.lower()) + r'\b', re.IGNORECASE)
                    if word_pattern.search(text_item.lower()):
                        matches.append({
                            'type': 'string_word_match',
                            'location': f'string_index_{i}',
                            'confidence': 0.85,
                            'description': f'Found word boundary match for "{search_entity}" in: "{text_item[:50]}..."',
                            'matched_text': text_item,
                            'matcher': 'nlp_string_word',
                            'matcher_type': 'nlp'
                        })
                    
                    # Fuzzy matching for similar strings
                    try:
                        from difflib import SequenceMatcher
                        similarity = SequenceMatcher(None, search_entity.lower(), text_item.lower()).ratio()
                        if similarity > 0.7:  # 70% similarity threshold
                            matches.append({
                                'type': 'string_fuzzy_match',
                                'location': f'string_index_{i}',
                                'confidence': similarity * 0.8,  # Scale down confidence for fuzzy matches
                                'description': f'Found fuzzy match for "{search_entity}" (similarity: {similarity:.2f}) in: "{text_item[:50]}..."',
                                'matched_text': text_item,
                                'similarity_score': similarity,
                                'matcher': 'nlp_string_fuzzy',
                                'matcher_type': 'nlp'
                            })
                    except ImportError:
                        pass  # difflib not available
    
    except Exception as e:
        logging.debug(f"NLP string matching failed: {str(e)}")
    
    return matches


def _transformer_entity_matching(dataset, search_entity, dataset_info, model=None):
    """Use transformer models for advanced semantic entity matching."""
    matches = []
    
    try:
        # Use provided model or create a silent one
        if model is None:
            model = create_silent_sentence_transformer()
        
        # Extract text data from the dataset
        text_data = _extract_text_for_nlp(dataset, dataset_info)
        
        if not text_data:
            return matches
        
        # Generate embedding for search entity
        search_embedding = model.encode([search_entity], show_progress_bar=False)
        
        # Generate embeddings for text data (in batches to avoid memory issues)
        batch_size = 32
        for i in range(0, len(text_data), batch_size):
            batch_texts = text_data[i:i+batch_size]
            
            # Filter out empty or very short texts
            valid_texts = []
            valid_indices = []
            for j, text in enumerate(batch_texts):
                if isinstance(text, str) and len(text.strip()) > 2:
                    valid_texts.append(text.strip())
                    valid_indices.append(i + j)
            
            if not valid_texts:
                continue
            
            # Generate embeddings for valid texts
            try:
                text_embeddings = model.encode(valid_texts, show_progress_bar=False)
                
                # Calculate semantic similarity
                from sklearn.metrics.pairwise import cosine_similarity
                similarities = cosine_similarity(search_embedding, text_embeddings)[0]
                
                # Find high-similarity matches
                for j, similarity in enumerate(similarities):
                    if similarity > 0.6:  # 60% semantic similarity threshold
                        text_idx = valid_indices[j]
                        matched_text = valid_texts[j]
                        
                        matches.append({
                            'type': 'semantic_similarity',
                            'location': f'text_position_{text_idx}',
                            'confidence': float(similarity),
                            'description': f'Found semantic similarity for "{search_entity}" (similarity: {similarity:.3f})',
                            'matched_text': matched_text[:100] + "..." if len(matched_text) > 100 else matched_text,
                            'similarity_score': float(similarity),
                            'matcher': 'transformer_semantic',
                            'matcher_type': 'nlp'
                        })
                        
            except Exception as e:
                logging.debug(f"Batch processing failed for batch {i//batch_size}: {str(e)}")
                continue
    
    except ImportError:
        logging.debug("sentence-transformers not available for transformer entity matching")
    except Exception as e:
        logging.debug(f"Transformer entity matching failed: {str(e)}")
    
    return matches


def _semantic_tabular_matching(dataset, entity_embedding, search_entity, dataset_info):
    """Apply semantic matching to tabular data using embeddings."""
    matches = []
    
    try:
        # For tabular data, look for patterns in column names, values, and structure
        if dataset.ndim == 2:
            rows, cols = dataset.shape
            
            # Get actual column names from dataset_info if available
            column_names = []
            contextual_info = dataset_info.get('contextual_info', {})
            if contextual_info and contextual_info.get('column_names'):
                column_names = contextual_info.get('column_names', [])
            
            # Try to extract meaningful patterns from numerical data
            # Look for columns that might correspond to the search entity
            
            # Method 1: Statistical pattern matching
            # Create a signature from the search entity
            entity_signature = sum(ord(c) for c in search_entity if c.isalnum()) % 1000
            
            for col_idx in range(cols):
                column_data = dataset[:, col_idx]
                
                # Skip columns with too many zeros or NaNs
                if np.count_nonzero(column_data) < len(column_data) * 0.1:
                    continue
                
                # Get the actual column name or use generic if not available
                if col_idx < len(column_names):
                    column_name = column_names[col_idx]
                    location_id = column_name
                    description_text = f'Found statistical pattern related to "{search_entity}" in column "{column_name}"'
                else:
                    column_name = f'column_{col_idx}'
                    location_id = f'column_{col_idx}'
                    description_text = f'Found statistical pattern related to "{search_entity}" in column {col_idx}'
                
                # Calculate column statistics
                col_mean = np.mean(column_data)
                col_std = np.std(column_data)
                col_signature = int(abs(col_mean + col_std)) % 1000
                
                # Check if signatures are related
                signature_similarity = 1.0 / (1.0 + abs(entity_signature - col_signature) / 1000.0)
                
                if signature_similarity > 0.7:
                    matches.append({
                        'type': 'tabular_statistical_pattern',
                        'location': location_id,
                        'confidence': signature_similarity * 0.6,  # Lower confidence for statistical matching
                        'description': description_text,
                        'column_name': column_name,  # Add explicit column name field
                        'column_stats': {
                            'mean': float(col_mean),
                            'std': float(col_std),
                            'signature_similarity': float(signature_similarity)
                        },
                        'matcher': 'semantic_tabular_stats',
                        'matcher_type': 'semantic'
                    })
            
            # Method 2: Embedding-based pattern detection
            if entity_embedding is not None and len(entity_embedding) >= 8:
                # Create dataset embeddings from column statistics
                for col_idx in range(min(cols, 50)):  # Limit to first 50 columns
                    column_data = dataset[:, col_idx]
                    
                    # Create a feature vector from column statistics
                    if np.all(np.isfinite(column_data)):
                        col_features = [
                            np.mean(column_data),
                            np.std(column_data),
                            np.min(column_data),
                            np.max(column_data),
                            np.median(column_data),
                            np.percentile(column_data, 25),
                            np.percentile(column_data, 75),
                            len(np.unique(column_data)) / len(column_data)  # uniqueness ratio
                        ]
                        
                        # Normalize features
                        col_features = np.array(col_features)
                        col_features = col_features / (np.linalg.norm(col_features) + 1e-8)
                        
                        # Compare with entity embedding (use first 8 dimensions)
                        entity_features = entity_embedding[:8] / (np.linalg.norm(entity_embedding[:8]) + 1e-8)
                        
                        # Calculate similarity
                        similarity = np.dot(col_features, entity_features)
                        
                        if similarity > 0.5:
                            # Get the actual column name or use generic if not available
                            if col_idx < len(column_names):
                                column_name = column_names[col_idx]
                                location_id = column_name
                                description_text = f'Found embedding similarity for "{search_entity}" in column "{column_name}"'
                            else:
                                column_name = f'column_{col_idx}'
                                location_id = f'column_{col_idx}'
                                description_text = f'Found embedding similarity for "{search_entity}" in column {col_idx}'
                            
                            matches.append({
                                'type': 'tabular_embedding_similarity',
                                'location': location_id,
                                'confidence': float(similarity) * 0.7,
                                'description': description_text,
                                'column_name': column_name,  # Add explicit column name field
                                'embedding_similarity': float(similarity),
                                'matcher': 'semantic_tabular_embedding',
                                'matcher_type': 'semantic'
                            })
    
    except Exception as e:
        logging.debug(f"Semantic tabular matching failed: {str(e)}")
    
    return matches


def _semantic_image_matching(dataset, entity_embedding, search_entity, dataset_info):
    """Apply semantic matching to image data using embeddings."""
    matches = []
    
    try:
        # For image data, look for visual patterns that might relate to the search entity
        if len(dataset.shape) >= 2:
            # Method 1: Spatial pattern analysis
            # Create spatial signatures based on the entity
            entity_hash = hash(search_entity)
            target_patterns = [
                (entity_hash % dataset.shape[0], entity_hash % dataset.shape[1]),
                ((entity_hash * 2) % dataset.shape[0], (entity_hash * 3) % dataset.shape[1]),
                ((entity_hash * 5) % dataset.shape[0], (entity_hash * 7) % dataset.shape[1])
            ]
            
            for i, (row, col) in enumerate(target_patterns):
                if row < dataset.shape[0] and col < dataset.shape[1]:
                    # Extract local region around the target point
                    region_size = min(32, dataset.shape[0] // 4, dataset.shape[1] // 4)
                    row_start = max(0, row - region_size // 2)
                    row_end = min(dataset.shape[0], row + region_size // 2)
                    col_start = max(0, col - region_size // 2)
                    col_end = min(dataset.shape[1], col + region_size // 2)
                    
                    region = dataset[row_start:row_end, col_start:col_end]
                    
                    # Calculate region statistics
                    region_stats = [
                        np.mean(region),
                        np.std(region),
                        np.mean(np.gradient(region.astype(np.float64))),
                        np.std(np.gradient(region.astype(np.float64)))
                    ]
                    
                    # Create a similarity score based on entity characteristics
                    entity_chars = [ord(c) for c in search_entity if c.isalnum()]
                    if entity_chars:
                        char_stats = [
                            np.mean(entity_chars) / 128.0,  # Normalize to 0-1
                            np.std(entity_chars) / 128.0,
                            len(entity_chars) / 20.0,  # Assume max 20 chars
                            len(set(entity_chars)) / len(entity_chars)  # uniqueness
                        ]
                        
                        # Calculate similarity between region stats and character stats
                        region_norm = np.linalg.norm(region_stats)
                        char_norm = np.linalg.norm(char_stats)
                        
                        if region_norm > 1e-8 and char_norm > 1e-8:
                            similarity = np.dot(
                                np.array(region_stats) / region_norm,
                                np.array(char_stats) / char_norm
                            )
                            
                            if similarity > 0.3:
                                matches.append({
                                    'type': 'image_spatial_pattern',
                                    'location': f'region_{row}_{col}',
                                    'confidence': float(similarity) * 0.5,  # Lower confidence for spatial matching
                                    'description': f'Found spatial pattern for "{search_entity}" at region ({row}, {col})',
                                    'region_bounds': (row_start, row_end, col_start, col_end),
                                    'spatial_similarity': float(similarity),
                                    'matcher': 'semantic_image_spatial',
                                    'matcher_type': 'semantic'
                                })
            
            # Method 2: Frequency domain analysis
            if dataset.shape[0] > 8 and dataset.shape[1] > 8:
                try:
                    # Take FFT of the image
                    fft_data = np.fft.fft2(dataset.astype(np.float64))
                    fft_magnitude = np.abs(fft_data)
                    
                    # Create entity-based frequency signature
                    entity_freq_signature = []
                    for i, char in enumerate(search_entity[:8]):  # Use first 8 characters
                        freq_x = (ord(char) % dataset.shape[0]) // 2
                        freq_y = (ord(char) % dataset.shape[1]) // 2
                        if freq_x < fft_magnitude.shape[0] and freq_y < fft_magnitude.shape[1]:
                            entity_freq_signature.append(fft_magnitude[freq_x, freq_y])
                    
                    if entity_freq_signature:
                        # Compare with actual frequency content
                        avg_magnitude = np.mean(entity_freq_signature)
                        total_magnitude = np.sum(fft_magnitude)
                        
                        if total_magnitude > 1e-8:
                            frequency_similarity = avg_magnitude / (total_magnitude / fft_magnitude.size)
                            
                            if frequency_similarity > 0.01:  # Very low threshold for frequency analysis
                                matches.append({
                                    'type': 'image_frequency_pattern',
                                    'location': 'frequency_domain',
                                    'confidence': min(float(frequency_similarity) * 0.3, 0.8),
                                    'description': f'Found frequency domain pattern for "{search_entity}"',
                                    'frequency_similarity': float(frequency_similarity),
                                    'matcher': 'semantic_image_frequency',
                                    'matcher_type': 'semantic'
                                })
                
                except Exception as e:
                    logging.debug(f"FFT analysis failed: {str(e)}")
    
    except Exception as e:
        logging.debug(f"Semantic image matching failed: {str(e)}")
    
    return matches


def _semantic_general_matching(dataset, entity_embedding, search_entity, dataset_info):
    """Apply general semantic matching for any dataset type."""
    matches = []
    
    try:
        # Method 1: Dimensionality-based matching
        if entity_embedding is not None:
            # Create dataset embedding from global statistics
            dataset_flat = dataset.flatten()
            
            # Remove infinite and NaN values
            dataset_clean = dataset_flat[np.isfinite(dataset_flat)]
            
            if len(dataset_clean) > 0:
                # Create statistical signature
                dataset_signature = [
                    np.mean(dataset_clean),
                    np.std(dataset_clean),
                    np.min(dataset_clean),
                    np.max(dataset_clean),
                    np.median(dataset_clean),
                    len(np.unique(dataset_clean)) / len(dataset_clean),  # uniqueness
                    np.sum(dataset_clean > 0) / len(dataset_clean),  # positive ratio
                    np.sum(dataset_clean < 0) / len(dataset_clean)   # negative ratio
                ]
                
                # Extend to match entity embedding length
                while len(dataset_signature) < len(entity_embedding):
                    dataset_signature.append(np.percentile(dataset_clean, 
                                                          (len(dataset_signature) * 10) % 100))
                
                dataset_signature = np.array(dataset_signature[:len(entity_embedding)])
                
                # Normalize both embeddings
                entity_norm = entity_embedding / (np.linalg.norm(entity_embedding) + 1e-8)
                dataset_norm = dataset_signature / (np.linalg.norm(dataset_signature) + 1e-8)
                
                # Calculate similarity
                similarity = np.dot(entity_norm, dataset_norm)
                
                if similarity > 0.3:
                    matches.append({
                        'type': 'general_statistical_similarity',
                        'location': 'global_statistics',
                        'confidence': float(similarity) * 0.6,
                        'description': f'Found statistical similarity for "{search_entity}" in dataset global properties',
                        'statistical_similarity': float(similarity),
                        'matcher': 'semantic_general_stats',
                        'matcher_type': 'semantic'
                    })
        
        # Method 2: Shape-based semantic matching
        shape_signature = list(dataset.shape) + [dataset.size, dataset.ndim]
        entity_shape_signature = [
            len(search_entity),
            sum(ord(c) for c in search_entity) % 10000,
            len(set(search_entity)),
            search_entity.count(' ') + 1  # word count approximation
        ]
        
        # Normalize and compare shape signatures
        if len(shape_signature) > 0 and len(entity_shape_signature) > 0:
            max_len = max(len(shape_signature), len(entity_shape_signature))
            
            # Pad shorter signature
            while len(shape_signature) < max_len:
                shape_signature.append(shape_signature[-1] if shape_signature else 1)
            while len(entity_shape_signature) < max_len:
                entity_shape_signature.append(entity_shape_signature[-1] if entity_shape_signature else 1)
            
            shape_signature = np.array(shape_signature[:max_len], dtype=np.float64)
            entity_shape_signature = np.array(entity_shape_signature[:max_len], dtype=np.float64)
            
            # Normalize
            shape_norm = shape_signature / (np.linalg.norm(shape_signature) + 1e-8)
            entity_norm = entity_shape_signature / (np.linalg.norm(entity_shape_signature) + 1e-8)
            
            shape_similarity = np.dot(shape_norm, entity_norm)
            
            if shape_similarity > 0.4:
                matches.append({
                    'type': 'general_shape_similarity',
                    'location': 'dataset_structure',
                    'confidence': float(shape_similarity) * 0.5,
                    'description': f'Found structural similarity for "{search_entity}" in dataset shape/organization',
                    'shape_similarity': float(shape_similarity),
                    'matcher': 'semantic_general_shape',
                    'matcher_type': 'semantic'
                })
    
    except Exception as e:
        logging.debug(f"General semantic matching failed: {str(e)}")
    
    return matches


def _decode_text_from_dataset(dataset):
    """Decode text data from a dataset array."""
    text_data = []
    
    try:
        if hasattr(dataset, 'dtype'):
            if dataset.dtype.kind in ['U', 'S']:  # Unicode or byte strings
                # Handle different shapes
                if dataset.ndim == 1:
                    text_data = [str(item) for item in dataset]
                elif dataset.ndim == 2:
                    # Assume each row is a text entry
                    for row in dataset:
                        if hasattr(row, '__iter__'):
                            # Join array elements into a single string
                            text_data.append(' '.join(str(item) for item in row))
                        else:
                            text_data.append(str(row))
                else:
                    # Flatten higher dimensional arrays
                    flattened = dataset.flatten()
                    text_data = [str(item) for item in flattened]
            
            elif dataset.dtype.kind in ['i', 'u', 'f']:  # Numeric data
                # Try to interpret as character codes
                if dataset.ndim == 1:
                    # Assume it's a sequence of character codes
                    try:
                        # Filter out invalid character codes
                        valid_codes = [int(x) for x in dataset if 0 <= x <= 1114111]
                        if valid_codes:
                            decoded_text = ''.join(chr(code) for code in valid_codes 
                                                 if 32 <= code <= 126 or code in [9, 10, 13])  # Printable + whitespace
                            if len(decoded_text.strip()) > 0:
                                text_data = [decoded_text]
                    except:
                        pass
                
                elif dataset.ndim == 2:
                    # Each row might be a text entry encoded as numbers
                    for row in dataset:
                        try:
                            valid_codes = [int(x) for x in row if 0 <= x <= 1114111]
                            if valid_codes:
                                decoded_text = ''.join(chr(code) for code in valid_codes 
                                                     if 32 <= code <= 126 or code in [9, 10, 13])
                                if len(decoded_text.strip()) > 0:
                                    text_data.append(decoded_text)
                        except:
                            continue
        
        # If we still don't have text data, try to extract from string representation
        if not text_data:
            dataset_str = str(dataset)
            if len(dataset_str) > 10:  # Avoid very short strings
                text_data = [dataset_str]
    
    except Exception as e:
        logging.debug(f"Text decoding failed: {str(e)}")
        # Fallback: convert to string
        try:
            text_data = [str(dataset)]
        except:
            text_data = []
    
    return text_data


def _extract_json_content_as_text(json_data):
    """Extract meaningful text content from JSON data for entity extraction.
    Works with any JSON structure, extracting all text values and field names.
    """
    text_content = []
    max_unique_content = 1000  # Increased from 100 to capture more entities
    
    try:
        if isinstance(json_data, list):
            # For very large lists, use adaptive sampling to ensure coverage
            total_items = len(json_data)
            
            # Process the entire list if reasonable size, otherwise sample strategically
            if total_items <= 5000:  # Process all items for smaller lists
                items_to_process = json_data
            else:
                # For large arrays, use strategic sampling from beginning, middle, and throughout
                # Distribute samples across the entire dataset
                sample_count = min(5000, total_items // 10)  # Cap at 5000, or 10% of total
                
                # Create a distribution that samples more at beginning, some in middle, and some at end
                # but also samples throughout the dataset
                begin_size = sample_count // 3  # 1/3 from beginning
                end_size = sample_count // 3    # 1/3 from end
                middle_samples = sample_count - begin_size - end_size  # Remainder distributed throughout
                
                # Get indices strategically
                begin_indices = list(range(0, min(begin_size, total_items)))
                
                # Distributed middle indices
                step_size = max(1, (total_items - begin_size - end_size) // middle_samples)
                middle_indices = list(range(begin_size, total_items - end_size, step_size))[:middle_samples]
                
                # End indices
                end_indices = list(range(max(0, total_items - end_size), total_items))
                
                # Combine and deduplicate
                all_indices = sorted(set(begin_indices + middle_indices + end_indices))
                items_to_process = [json_data[i] for i in all_indices]
            
            # Process all the selected items
            for item in items_to_process:
                # For dictionaries in the list
                if isinstance(item, dict):
                    # Extract all field values
                    for key, value in item.items():
                        # Include all field names as potential entities
                        text_content.append(key)
                        
                        # Process string values
                        if isinstance(value, str) and value:
                            clean_value = value.strip()
                            if clean_value:  # Any non-empty string
                                text_content.append(clean_value)
                        
                        # Handle nested structures
                        elif isinstance(value, (dict, list)) and value:
                            text_content.extend(_extract_json_content_as_text(value))
                
                # For strings in the list
                elif isinstance(item, str) and item:
                    clean_item = item.strip()
                    if clean_item:
                        text_content.append(clean_item)
                
                # For numbers or other primitives, convert if they might be meaningful
                elif item is not None:
                    str_val = str(item).strip()
                    if len(str_val) > 1:  # Skip single digits or characters
                        text_content.append(str_val)
                    
        elif isinstance(json_data, dict):
            # Process dictionary
            for key, value in json_data.items():
                # Include all field names
                text_content.append(key)
                
                # Process string values
                if isinstance(value, str) and value:
                    clean_value = value.strip()
                    if clean_value:
                        text_content.append(clean_value)
                
                # Handle nested structures recursively
                elif isinstance(value, (dict, list)) and value:
                    nested_content = _extract_json_content_as_text(value)
                    text_content.extend(nested_content)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_content = []
        for item in text_content:
            if isinstance(item, str) and item not in seen:
                clean_item = item.strip()
                if clean_item and clean_item not in seen:
                    seen.add(clean_item)
                    unique_content.append(clean_item)
                    
                    # Stop if we reach the maximum to prevent memory issues
                    if len(unique_content) >= max_unique_content:
                        break
        
        return unique_content  # Return all unique items, up to max_unique_content
        
    except Exception as e:
        logging.warning(f"JSON content extraction failed: {str(e)}")
        # Try a simplified approach as fallback
        try:
            # Convert to string and extract any text that looks meaningful
            json_str = str(json_data)
            # Extract words that look like they might be entities (alphanumeric with some symbols)
            import re
            potential_entities = re.findall(r'[A-Za-z0-9_\-]{2,50}', json_str)
            # Filter and deduplicate
            seen = set()
            result = []
            for entity in potential_entities:
                if entity not in seen and not entity.isdigit() and len(entity) >= 2:
                    seen.add(entity)
                    result.append(entity)
            return result[:1000]  # Limit to 1000 items
        except:
            # Last resort fallback
            return []


def _extract_excel_content_as_text(df):
    """Extract meaningful text content from Excel/DataFrame data for entity extraction."""
    text_content = []
    
    try:
        if df is None or not hasattr(df, 'columns'):
            return []
            
        # Extract column names as they are important entities
        for col in df.columns:
            if isinstance(col, str) and col:
                text_content.append(col)
                
        # Extract cell values that look like meaningful text
        for col in df.columns:
            # For each column, sample up to 100 non-null values
            sample_values = df[col].dropna().astype(str).sample(min(100, len(df))).tolist() if len(df) > 0 else []
            
            for value in sample_values:
                if isinstance(value, str) and value and len(value.strip()) > 1:
                    # Skip very common metadata fields and focus on content
                    clean_value = value.strip()
                    if 1 < len(clean_value) < 100:  # Reasonable length
                        text_content.append(clean_value)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_content = []
        for item in text_content:
            if isinstance(item, str) and item not in seen and len(item.strip()) > 1:
                seen.add(item)
                unique_content.append(item)
        
        return unique_content[:100]  # Return top 100 unique items
        
    except Exception as e:
        logging.debug(f"Excel content extraction failed: {str(e)}")
        return []


def _extract_text_for_nlp(dataset, dataset_info):
    """Extract text data from dataset for NLP processing."""
    text_data = []
    
    try:
        data_type = dataset_info.get('data_type', 'unknown')
        file_path = dataset_info.get('file_path', '')
        
        # PRIORITY: For JSON data, extract actual content from stored JSON
        if data_type == 'json' and file_path:
            temp_data_key = f"temp_json_data_{hash(file_path)}"
            json_data = _GENERAL_METADATA.get(temp_data_key)
            
            if json_data:
                text_data.extend(_extract_json_content_as_text(json_data))
                if text_data:  # If we successfully extracted JSON content, return it
                    return text_data  # Return all extracted content without limiting
        
        # PRIORITY: For Excel data, extract actual content from stored DataFrame
        elif data_type in ['excel', 'tabular'] and file_path:
            # First, try the direct Excel data key
            excel_data_key = f"excel_data_{hash(file_path)}"
            if excel_data_key in _GENERAL_METADATA:
                df = _GENERAL_METADATA.get(excel_data_key)
                if df is not None:
                    text_data.extend(_extract_excel_content_as_text(df))
                    if text_data:  # If we successfully extracted Excel content, return it
                        return text_data
            
            # Fallback: Check all metadata for the DataFrame
            for meta_key, meta_value in _GENERAL_METADATA.items():
                if isinstance(meta_value, dict) and 'file_path' in meta_value and meta_value['file_path'] == file_path:
                    if 'dataframe' in meta_value:
                        df = meta_value['dataframe']
                        text_data.extend(_extract_excel_content_as_text(df))
                        if text_data:  # If we successfully extracted Excel content, return it
                            return text_data
        
        # Method 1: Direct text extraction based on data type
        if data_type == 'text':
            text_data = _decode_text_from_dataset(dataset)
        
        # Method 2: Extract from string-like arrays
        elif hasattr(dataset, 'dtype') and dataset.dtype.kind in ['U', 'S', 'a']:
            text_data = _decode_text_from_dataset(dataset)
        
        # Method 3: Try to extract metadata or embedded text
        elif data_type in ['json', 'tabular']:
            # For structured data, look for text-like patterns
            if dataset.ndim <= 2:
                # Try to find text patterns in the data
                if hasattr(dataset, 'flatten'):
                    flat_data = dataset.flatten()
                    
                    # Look for patterns that might represent text
                    for item in flat_data:  # Limit to first 100 items
                        try:
                            item_str = str(item)
                            # Check if it looks like meaningful text
                            if (len(item_str) > 3 and 
                                any(c.isalpha() for c in item_str) and
                                len(item_str) < 1000):  # Reasonable text length
                                text_data.append(item_str)
                        except:
                            continue
        
        # Method 4: Extract from file path and metadata
        file_info = dataset_info.get('file_path', '')
        if file_info:
            # Extract meaningful text from file path
            import os
            filename = os.path.basename(file_info)
            filename_parts = filename.replace('_', ' ').replace('-', ' ').replace('.', ' ')
            text_data.append(f"File: {filename_parts}")
        
        # Add dataset shape and type information as text
        shape_info = f"Dataset shape {dataset_info.get('shape', 'unknown')} type {data_type}"
        text_data.append(shape_info)
        
        # Method 5: Generate descriptive text from dataset statistics
        if hasattr(dataset, 'shape') and dataset.size > 0:
            try:
                if np.issubdtype(dataset.dtype, np.number):
                    # Extract numerical statistics as text
                    flat_data = dataset.flatten()
                    clean_data = flat_data[np.isfinite(flat_data)]
                    
                    if len(clean_data) > 0:
                        stats_text = (
                            f"Numerical dataset with {len(clean_data)} values "
                            f"ranging from {np.min(clean_data):.3f} to {np.max(clean_data):.3f} "
                            f"with mean {np.mean(clean_data):.3f} and standard deviation {np.std(clean_data):.3f}"
                        )
                        text_data.append(stats_text)
                        
                        # Add distribution characteristics
                        positive_ratio = np.sum(clean_data > 0) / len(clean_data)
                        zero_ratio = np.sum(clean_data == 0) / len(clean_data)
                        
                        distribution_text = (
                            f"Distribution characteristics: {positive_ratio:.1%} positive values, "
                            f"{zero_ratio:.1%} zero values, "
                            f"{len(np.unique(clean_data))} unique values"
                        )
                        text_data.append(distribution_text)
            except Exception as e:
                logging.debug(f"Statistics extraction failed: {str(e)}")
        
        # Method 6: Extract text from matrix type
        matrix_type = dataset_info.get('matrix_type', 'unknown')
        if matrix_type != 'unknown':
            type_text = f"Matrix type {matrix_type} with structural properties"
            text_data.append(type_text)
        
        # Clean and filter text data
        cleaned_text_data = []
        for text in text_data:
            if isinstance(text, str) and len(text.strip()) > 0:
                # Remove very long strings that might be noise
                if len(text) < 2000:
                    cleaned_text_data.append(text.strip())
        
        text_data = cleaned_text_data
    
    except Exception as e:
        logging.debug(f"Text extraction for NLP failed: {str(e)}")
        # Fallback: create basic descriptive text
        try:
            fallback_text = f"Dataset with shape {getattr(dataset, 'shape', 'unknown')} and type {type(dataset).__name__}"
            text_data = [fallback_text]
        except:
            text_data = ["Unknown dataset"]
    
    return text_data


def _calculate_pathway_confidence(attention_scores, structural_data=None):
    """Calculate pathway confidence combining attention focus and structural validity.

    Args:
        attention_scores: Array/dict of attention weights (legacy behavior preserved)
        structural_data: Optional dict with pathway structure metrics:
            - 'shared_entities': count of entities in both datasets
            - 'total_entities': total unique entities across datasets
            - 'semantic_connections': list of semantic connections found
            - 'contextual_bridges': list of contextual bridges
            - 'entity_coverage': dict with coverage ratios per dataset
            - 'direct_pathways': count of direct transformation paths

    Returns:
        Float in [0, 1] representing pathway confidence
    """
    # Calculate attention focus score (original logic with floor)
    attention_focus = _calculate_attention_focus(attention_scores)
    
    # If no structural data provided, use attention-only (backward compatibility)
    if structural_data is None:
        return attention_focus
    
    # Calculate structural validity score
    structural_validity = _calculate_structural_validity(structural_data)
    
    # Composite confidence: weighted blend favoring structural evidence
    # α=0.8 (structural), β=0.1 (attention), γ=0.1 (synergy)
    confidence = (0.8 * structural_validity + 
                 0.1 * attention_focus + 
                 0.1 * (structural_validity * attention_focus))
    
    # Apply stronger minimum confidence floor when structural evidence is strong
    if structural_validity > 0.8:
        confidence = max(0.6, confidence)
    elif structural_validity > 0.6:
        confidence = max(0.4, confidence)
    
    return float(np.clip(confidence, 0.0, 1.0))


def _calculate_attention_focus(attention_scores):
    """Calculate attention focus score (original algorithm with entropy floor).
    
    Returns value in [0, 1] measuring how concentrated the attention distribution is.
    """
    if not attention_scores:
        return 0.0

    # Convert to a 1D numpy array of finite floats
    if isinstance(attention_scores, dict):
        scores = np.array(list(attention_scores.values()), dtype=float)
    elif isinstance(attention_scores, (list, tuple, np.ndarray)):
        scores = np.array(attention_scores, dtype=float).reshape(-1)
    else:
        return 0.0

    scores = scores[np.isfinite(scores)]
    if scores.size == 0:
        return 0.0

    # Normalize to a probability distribution if possible
    total = float(scores.sum())
    if total <= 0:
        return 0.0
    p = scores / total

    n = p.size
    if n == 1:
        return float(np.clip(p[0], 0.0, 1.0))

    # Peak mass and top-k concentration
    peak = float(p.max())
    k = min(3, n)
    topk = float(np.sort(p)[-k:].sum())

    # Entropy-based flatness measure with floor to prevent zero-ing
    entropy = float(-(p * np.log(p + 1e-12)).sum())
    entropy_norm = entropy / float(np.log(n)) if n > 1 else 0.0
    entropy_component = max(0.2, 1.0 - entropy_norm)  # Floor at 0.2

    # Combine: emphasize peak, then concentration, then entropy penalty
    confidence = 0.6 * peak + 0.25 * (topk - peak) + 0.15 * entropy_component
    return float(np.clip(confidence, 0.0, 1.0))


def _calculate_structural_validity(structural_data):
    """Calculate structural validity score based on pathway evidence.
    
    Args:
        structural_data: Dict containing structural metrics
        
    Returns:
        Float in [0, 1] representing structural pathway strength
    """
    if not isinstance(structural_data, dict):
        return 0.0
    
    score_components = []
    
    # Entity overlap strength (40% weight)
    shared_entities = structural_data.get('shared_entities', 0)
    total_entities = structural_data.get('total_entities', 1)
    entity_overlap = min(1.0, shared_entities / max(1, total_entities))
    score_components.append(('entity_overlap', entity_overlap, 0.4))
    
    # Entity coverage ratios (30% weight)
    entity_coverage = structural_data.get('entity_coverage', {})
    if entity_coverage:
        coverage_values = [v for v in entity_coverage.values() if isinstance(v, (int, float))]
        avg_coverage = np.mean(coverage_values) if coverage_values else 0.0
        score_components.append(('coverage', min(1.0, avg_coverage), 0.3))
    else:
        score_components.append(('coverage', 0.0, 0.3))
    
    # Semantic connection strength (20% weight)  
    semantic_connections = structural_data.get('semantic_connections', [])
    if semantic_connections:
        # Use connection count with reasonable scoring thresholds
        connection_count = len(semantic_connections)
        # Simple tiered scoring: 1+ = 0.3, 5+ = 0.6, 10+ = 0.8, 20+ = 1.0
        if connection_count >= 20:
            connection_strength = 1.0
        elif connection_count >= 10:
            connection_strength = 0.8
        elif connection_count >= 5:
            connection_strength = 0.6
        elif connection_count >= 1:
            connection_strength = 0.3
        else:
            connection_strength = 0.0

        
        score_components.append(('semantic', connection_strength, 0.2))
    else:
        score_components.append(('semantic', 0.0, 0.2))
    
    # Contextual bridge quality (10% weight)
    contextual_bridges = structural_data.get('contextual_bridges', [])
    if contextual_bridges:
        bridge_count = len(contextual_bridges)
        # Tiered scoring for contextual bridges: 1+ = 0.4, 10+ = 0.7, 50+ = 1.0
        if bridge_count >= 50:
            bridge_strength = 1.0
        elif bridge_count >= 10:
            bridge_strength = 0.7
        elif bridge_count >= 1:
            bridge_strength = 0.4
        else:
            bridge_strength = 0.0
    else:
        bridge_strength = 0.0
    score_components.append(('bridges', bridge_strength, 0.1))
    
    # Calculate weighted average
    total_score = sum(score * weight for _, score, weight in score_components)
    
    # Boost for direct pathways (multiplicative factor)
    direct_pathways = structural_data.get('direct_pathways', 0)
    if direct_pathways > 0:
        pathway_boost = min(1.2, 1.0 + (direct_pathways * 0.1))
        total_score *= pathway_boost
    
    return float(np.clip(total_score, 0.0, 1.0))


def _build_confidence(attention_scores, structural_data=None):
    """Compute canonical pathway confidence plus a breakdown dict.

    Returns (confidence_float, breakdown_dict).
    """
    attention_focus = _calculate_attention_focus(attention_scores)
    structural_validity = _calculate_structural_validity(structural_data) if structural_data is not None else 0.0

    confidence = _calculate_pathway_confidence(attention_scores, structural_data)

    breakdown = {
        'structural_validity': float(structural_validity),
        'attention_focus': float(attention_focus),
        'weights': {'structural': 0.8, 'attention': 0.1, 'synergy': 0.1},
        'composite_confidence': float(confidence)
    }

    return float(confidence), breakdown

def _calculate_semantic_distance(coords1, coords2):
    """Calculate semantic distance between two coordinate sets."""
    try:
        coords1 = np.array(coords1)
        coords2 = np.array(coords2)
        return float(np.linalg.norm(coords1 - coords2))
    except:
        return float('inf')



def _print_exploration_summary(exploration_results, total_datasets, elapsed_time):
    """Log a concise exploration summary. Keep console output minimal.

    Avoid printing the large banner; emit INFO-level summaries and
    DEBUG-level details when appropriate.
    """
    try:
        logging.info(f"Exploration completed: datasets={int(total_datasets)}, time={float(elapsed_time):.2f}s")

        pathway_type = exploration_results.get('pathway_type')
        if pathway_type == 'direct_exploration':
            src = exploration_results.get('source_dataset', {}).get('file_name', '<unknown>')
            tgt = exploration_results.get('target_dataset', {}).get('file_name', '<unknown>')
            logging.info(f"Direct pathway: {src} -> {tgt}")
            

        elif pathway_type == 'entity_search':
            matches = exploration_results.get('matches_found', 0)
            query = exploration_results.get('search_query', '<unknown>')
            logging.info(f"Entity search '{query}': {int(matches)} matches found")
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                for i, result in enumerate(exploration_results.get('results', [])[:5]):
                    ds = result.get('dataset', {}).get('file_name', '<unknown>')
                    cnt = len(result.get('entity_matches', []))
                    logging.debug(f"  Match {i+1}: {ds} - {cnt} matches")

        elif pathway_type == 'semantic_bridges':
            bridges = exploration_results.get('bridge_datasets', [])
            logging.info(f"Found {len(bridges)} semantic bridge datasets")
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                for i, bridge in enumerate(bridges[:3]):
                    name = bridge.get('bridge_dataset', {}).get('file_name', '<unknown>')
                    score = bridge.get('bridge_score', 0.0)
                    connections = bridge.get('connectivity_count', 0)
                    logging.debug(f"Bridge {i+1}: {name} score={score:.3f} connections={connections}")

    except Exception:
        logging.debug("_print_exploration_summary failed to emit summary", exc_info=True)









  
    
def create_parser():
    """Create the argument parser for TensorPack."""
    parser = argparse.ArgumentParser(
        description="TensorPack: CLI tool for tensor-matrix conversions and transformations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Global convenience flag to activate license without subcommand
    parser.add_argument('--activate-license', dest='activate_license', help='Activate a license key (paste the key here)', default=None)
    return parser

def parse_args() -> argparse.Namespace:
    """Update the argument parser with matrix transformation commands."""
    
    parser = create_parser()
    
    # Common arguments
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--output', '-o', type=str, help='Output file path')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--log', type=str, help='Log to file')
    

    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # tensor_to_matrix command
    t2m_parser = subparsers.add_parser('tensor_to_matrix', help='Convert tensor to matrix')
    t2m_parser.add_argument('input', type=str, help='Input tensor file path')
    t2m_parser.add_argument('--output', type=str, help='Output matrix file path')
    t2m_parser.add_argument('--normalize', type=str, choices=['none', 'frobenius', 'max', 'l1', 'l2'], 
                           default='none', help='Normalization method')
    t2m_parser.add_argument('--dtype', type=str, 
                           choices=['float32', 'float64', 'complex64', 'complex128'], 
                           help='Output data type')
    t2m_parser.add_argument('--flatten-mode', type=str, 
                           choices=['raw', 'semantic', 'structure-preserving'],
                           default='structure-preserving', help='Flattening algorithm mode')
    t2m_parser.add_argument('--meta-file', type=str, help='Save metadata to JSON file')
    t2m_parser.add_argument('--encoding', type=str, 
                           choices=['grid', 'slice', 'projection'], 
                           default='grid', help='Encoding algorithm for higher dimensions')
    t2m_parser.add_argument('--preserve-sparsity', action='store_true', 
                           help='Special handling for sparse tensors')
    t2m_parser.add_argument('--estimate-error', action='store_true',
                           help='Estimate reconstruction error')
    
    # matrix_to_tensor command
    m2t_parser = subparsers.add_parser('matrix_to_tensor', help='Convert matrix to tensor')
    m2t_parser.add_argument('input', type=str, help='Input matrix file path')
    m2t_parser.add_argument('--output', type=str, help='Output tensor file path')
    m2t_parser.add_argument('--metadata', type=str, help='Path to metadata JSON file')
    m2t_parser.add_argument('--verify', action='store_true', 
                           help='Perform round-trip error checking')
    m2t_parser.add_argument('--inspect', action='store_true', 
                           help='Display metadata without performing conversion')
    m2t_parser.add_argument('--target-shape', type=str, 
                           help='Target tensor shape as comma-separated values (e.g., "3,224,224")')
    m2t_parser.add_argument('--target-dtype', type=str, 
                           choices=['float32', 'float64', 'complex64', 'complex128'], 
                           help='Output tensor data type')
    m2t_parser.add_argument('--error-threshold', type=float, 
                           help='Maximum acceptable error for verification')
    m2t_parser.add_argument('--fill-mode', type=str, 
                           choices=['zeros', 'extrapolate', 'repeat'], 
                           default='zeros', help='How to handle missing data')
    m2t_parser.add_argument('--force-reconstruction', action='store_true', 
                           help='Attempt reconstruction even with incomplete metadata')

    # combine command removed

    # discover-connections command
    discover_parser = subparsers.add_parser('discover-connections', 
        help='Discover hidden connections between matrices/tensors with multiple export formats')
    discover_parser.add_argument('--inputs', type=str, nargs='+', required=True,
                           help='Input files to analyze for connections')
    discover_parser.add_argument('--num-dims', type=int, default=8,
                           help='Dimensionality of the hyperdimensional space')
    discover_parser.add_argument('--output', type=str,
                           help='Path to save connection data')
    discover_parser.add_argument('--visualize', type=str,
                           help='Directory to save visualizations')
    discover_parser.add_argument('--save-npy', action='store_true',
                           help='Automatically save companion .npy binaries for each loaded matrix (and simple metadata JSON)')
    discover_parser.add_argument('--threshold', type=float, default=0.5,
                           help='Minimum connection strength to include (0.0-1.0)')
    discover_parser.add_argument('--max-connections', type=int, default=5,
                           help='Maximum number of connections to keep per tensor')
    discover_parser.add_argument('--export-formats', type=str, nargs='*', 
                           choices=['csv', 'xlsx', 'parquet', 'html', 'md', 'sqlite', 'all'],
                           default=['json'],
                           help='Additional export formats (beyond JSON) using convertto.py capabilities')
    discover_parser.add_argument('--clustering', type=str, default=None,
                           choices=['auto', '2', '3', '4', '5', '8', '10'],
                           help='Clustering method to group similar tensors')
    discover_parser.add_argument('--plot-method', type=str, default='graph',
                           choices=['graph', 'matrix', '3d'],
                           help='How to visualize connections')
    discover_parser.add_argument('--format', type=str, default='json',
                           choices=['json', 'edge-list', 'adjacency'],
                           help='Format for the connection graph output')
    discover_parser.add_argument('--distance-metric', type=str, default='cosine',
                           choices=['cosine', 'euclidean', 'angular'],
                           help='Distance metric to use')
    discover_parser.add_argument('--skip-errors', action='store_true',
                           help='Skip files that cause loading errors')
    discover_parser.add_argument('--graph-analysis', action='store_true',
                           help='Include graph traversal paths in connection analysis')
    discover_parser.add_argument('--use-coordinates', action='store_true',
                           help='Use 16D coordinates for enhanced connection scoring')
    discover_parser.add_argument('--verbose', '-v', action='store_true',
                           help='Enable verbose logging')
    discover_parser.add_argument('--apply-transform', type=str,
                           help='Apply a registered transform before analysis (use transform name)')

    # traverse-graph command
    traverse_parser = subparsers.add_parser('traverse-graph',
        help='Discover semantic connections between datasets using three focused exploration modes with multiple export formats')
    traverse_parser.add_argument('--inputs', type=str, nargs='+', required=True,
                                help='Input files or directories to analyze (supports wildcards)')
    traverse_parser.add_argument('--output', type=str, default='graph_roadmap',
                                help='Base name for output files (without extension)')
    traverse_parser.add_argument('--export-formats', type=str, nargs='*', 
                                choices=['csv', 'xlsx', 'parquet', 'html', 'md', 'sqlite', 'all'],
                                default=[],
                                help='Additional export formats (beyond JSON) using convertto.py capabilities')
    traverse_parser.add_argument('--save-npy', action='store_true',
                                help='Save main numeric results (e.g., similarity matrix, cluster labels) as .npy files alongside JSON output.')
    traverse_parser.add_argument('--save-npz', action='store_true',
                                help='Save all main numeric results in a single .npz file alongside JSON output.')
    traverse_parser.add_argument('--verbose', '-v', action='store_true', 
                                help='Enable verbose logging')
    
    # === THREE CORE EXPLORATION MODES ===
    traverse_parser.add_argument('--source-dataset', type=str,
                                help='Source dataset for direct path finding (filename or index)')
    traverse_parser.add_argument('--target-dataset', type=str,
                                help='Target dataset for direct path finding (filename or index)')
    traverse_parser.add_argument('--search-entity', type=str,
                                help='Entity to search for across all datasets')
    traverse_parser.add_argument('--generate-viz', action='store_true',
                                help='Generate interactive HTML visualization for search results')
    traverse_parser.add_argument('--find-bridges', action='store_true',
                                help='Find datasets that act as semantic bridges between others')
    
    # === OPTIONAL ENHANCEMENTS ===
    traverse_parser.add_argument('--visualize', type=str, nargs='?', const='graph_viz',
                                help='Generate visualization outputs (PNG, PDF, and interactive HTML)')
    traverse_parser.add_argument('--include-metadata', action='store_true',
                                help='Include detailed metadata in output files')
    traverse_parser.add_argument('--viz-initial-depth', type=int, default=3,
                                help='Initial expansion depth for visualization tree (default: 3)')
    traverse_parser.add_argument('--viz-no-collapse', action='store_true',
                                help='Expand all nodes initially (warning: may be slow on large datasets)')
    traverse_parser.add_argument('--log', type=str, help='Log file path')
    traverse_parser.add_argument('--apply-transform', type=str,
                                help='Apply a registered transform before analysis (use transform name)')
    
    # add-transform command
    add_transform_parser = subparsers.add_parser('add-transform', 
        help='Add a custom transformation to TensorPack')
    add_transform_parser.add_argument('--name', type=str, required=True,
                                   help='Name of the transformation')
    add_transform_parser.add_argument('--data-type', type=str, required=True,
                                   choices=['matrix', 'json', 'graph', 'timeseries', 'image', 'audio', 
                                           'genomics', 'finance', 'text', 'custom'],
                                   help='Data type the transformation operates on')
    add_transform_parser.add_argument('--source-type', type=str, required=True,
                                   choices=['python', 'executable', 'inline', 'config'],
                                   help='Type of transformation source')
    add_transform_parser.add_argument('--source', type=str, required=True,
                                   help='Path to source file or inline definition')
    add_transform_parser.add_argument('--function-name', type=str,
                                   help='Function name (for Python sources)')
    add_transform_parser.add_argument('--properties', type=str,
                                   help='Properties as JSON string or key=value,key=value')
    add_transform_parser.add_argument('--neighbors', type=str,
                                   help='Neighboring transformation types (comma-separated)')
    add_transform_parser.add_argument('--description', type=str,
                                   help='Description of the transformation')
    add_transform_parser.add_argument('--version', type=str, default='1.0',
                                   help='Version of the transformation')
    add_transform_parser.add_argument('--dependencies', type=str,
                                   help='Required dependencies (comma-separated)')
    add_transform_parser.add_argument('--test-data', type=str,
                                   help='Test data file to validate transformation')
    add_transform_parser.add_argument('--test-output', type=str,
                                   help='Save test output to file')
    add_transform_parser.add_argument('--force', action='store_true',
                                   help='Force registration even if tests fail')
    # Embedding options (opt-in)
    add_transform_parser.add_argument('--embed', action='store_true',
                                   help='Embed the source file into the local transform registry (opt-in)')
    add_transform_parser.add_argument('--embed-unrestricted', action='store_true',
                                   help='Allow unrestricted embedding (no size checks). Use with caution.')
    add_transform_parser.add_argument('--embed-max-mb', type=int, default=100,
                                   help='Maximum embed size in MB when --embed is used (default: 100)')
    
    # list-transforms command
    list_transforms_parser = subparsers.add_parser('list-transforms', 
        help='List available transformations')
    list_transforms_parser.add_argument('--data-type', type=str,
                                     choices=['matrix', 'json', 'graph', 'timeseries', 'image', 'audio', 
                                             'genomics', 'finance', 'text', 'custom'],
                                     help='Filter by data type')
    list_transforms_parser.add_argument('--detailed', action='store_true',
                                     help='Show detailed information')
    
    # describe-transform command
    describe_transform_parser = subparsers.add_parser('describe-transform', 
        help='Describe a specific transformation')
    describe_transform_parser.add_argument('name', type=str,
                                        help='Name of the transformation to describe')
    describe_transform_parser.add_argument('--show-source', action='store_true',
                                        help='Show source code (for Python transformations)')
    
    # remove-transform command
    remove_transform_parser = subparsers.add_parser('remove-transform', 
        help='Remove a transformation from the registry')
    remove_transform_parser.add_argument('name', type=str,
                                      help='Name of the transformation to remove')
    remove_transform_parser.add_argument('--force', action='store_true',
                                      help='Force removal without confirmation')

    # License management commands
    # activate-license command
    activate_parser = subparsers.add_parser('activate-license', 
        help='Activate a license key')
    activate_parser.add_argument('license_key', type=str,
                               help='License key to activate')
    
    # license-info command
    license_info_parser = subparsers.add_parser('license-info', 
        help='Show current license information')
    license_info_parser.add_argument('--detailed', action='store_true',
                                   help='Show detailed license information')
    
    # usage-status command
    usage_parser = subparsers.add_parser('usage-status', 
        help='Show daily usage statistics (free tier)')
    
    # upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', 
        help='Show upgrade information and open upgrade page')
    upgrade_parser.add_argument('--open-browser', action='store_true',
                              help='Open upgrade page in browser')
    
    return parser.parse_args()



def main() -> int:
    """Main entry point for the CLI tool."""
    args = parse_args()
    
    # Process any QVM configuration from command line args
    if hasattr(args, 'disable_qvm') and args.disable_qvm:
        # If QVM is disabled, set the threshold to an impossibly high value
        configure_qvm(large_file_threshold=sys.maxsize)
    elif hasattr(args, 'qvm_threshold') and args.qvm_threshold is not None:
        threshold_bytes = int(args.qvm_threshold * 1024 * 1024)  # Convert MB to bytes
        configure_qvm(large_file_threshold=threshold_bytes)
    
    # OCR configuration is now handled within the individual command functions
    
    # QVM integration removed; configure_qvm is a compatibility no-op
    
    if args.command == 'tensor_to_matrix':
        return tensor_to_matrix_command(args)
    elif args.command == 'matrix_to_tensor':
        return matrix_to_tensor_command(args)
    elif args.command == 'discover-connections':
        return discover_connections_command(args)
    elif args.command == 'traverse-graph':
        return traverse_graph_command(args)
    elif args.command == 'add-transform':
        return add_transform_command(args)
    elif args.command == 'list-transforms':
        return list_transforms_command(args)
    elif args.command == 'describe-transform':
        return describe_transform_command(args)
    elif args.command == 'remove-transform':
        return remove_transform_command(args)
    elif args.command == 'activate-license':
        return activate_license_command(args)
    elif args.command == 'license-info':
        return license_info_command(args)
    elif args.command == 'usage-status':
        return usage_status_command(args)
    elif args.command == 'upgrade':
        return upgrade_command(args)
    else:
        print("Please specify a command. Use --help for more information.")
        return 1


def activate_license_command(args) -> int:
    """Handle license activation command."""
    try:
        license_manager = LicenseManager()
        success, message = license_manager.activate_license(args.license_key)
        
        if success:
            print(f"✓ {message}")
            
            # Show license info after successful activation. Be defensive:
            if hasattr(license_manager, 'get_license_info'):
                license_info = license_manager.get_license_info()
            else:
                # Fallback to internal cached structure
                license_info = getattr(license_manager, '_license_data', {}) or {}

            print("\nLicense Details:")
            print(f"  Type: {str(license_info.get('license_type', 'unknown')).title()}")
            status = license_info.get('status') or ('Activated' if license_info.get('activated') else 'Inactive')
            print(f"  Status: {status}")
            if license_info.get('expires'):
                print(f"  Expires: {license_info.get('expires')}")
            else:
                print("  Expires: Never (Premium)")
            
            return 0
        else:
            print(f"✗ {message}")
            return 1
            
    except Exception as e:
        print(f"Error activating license: {e}")
        return 1


def license_info_command(args) -> int:
    """Handle license info command."""
    try:
        license_manager = LicenseManager()
        license_info = license_manager.get_license_info()
        
        print("TensorPack License Information")
        print("=" * 40)
        print(f"License Type: {license_info['license_type'].title()}")
        print(f"Status: {license_info['status']}")
        print(f"Activated: {'Yes' if license_info['activated'] else 'No'}")
        
        if license_info.get('activation_date'):
            activation_date = license_info['activation_date'][:10]  # Just the date part
            print(f"Activation Date: {activation_date}")
        
        if license_info.get('expires'):
            print(f"Expires: {license_info['expires'][:10]}")
        else:
            print("Expires: Never")
        
        if args.detailed and license_info.get('metadata'):
            metadata = license_info['metadata']
            print(f"\nDetailed Information:")
            if metadata.get('customer_email'):
                print(f"  Email: {metadata['customer_email']}")
            if metadata.get('customer_name'):
                print(f"  Name: {metadata['customer_name']}")
            if metadata.get('product_name'):
                print(f"  Product: {metadata['product_name']}")
        
        # Show current features
        features = license_info.get('features', {})
        print(f"\nFeature Access:")
        print(f"  Advanced Features: {'✓' if features.get('traverse_graph') else '✗'}")
        print(f"  Custom Transforms: {'✓' if features.get('custom_transformations') else '✗'}")
        print(f"  Export Formats: {', '.join(features.get('export_formats', ['json']))}")
        print(f"  Max File Size: {features.get('max_file_size_mb', 'unlimited')} MB")
        print(f"  Max Datasets: {features.get('max_datasets', 'unlimited')}")
        
        # Show usage info for free tier
        if license_info['license_type'] == 'free':
            usage_info = license_manager.get_remaining_daily_usage()
            if usage_info.get('limited'):
                ops = usage_info['advanced_operations']
                print(f"\nDaily Usage (Free Tier):")
                print(f"  Advanced Operations: {ops['used']}/{ops['limit']} (remaining: {ops['remaining']})")
                print(f"  Resets: {usage_info['resets_at']}")
        
        return 0
        
    except Exception as e:
        print(f"Error getting license info: {e}")
        return 1


def usage_status_command(args) -> int:
    """Handle usage status command."""
    try:
        license_manager = LicenseManager()
        usage_info = license_manager.get_remaining_daily_usage()
        
        if not usage_info.get('limited'):
            print("No usage limits for your license tier.")
            return 0
        
        print("TensorPack Daily Usage Status")
        print("=" * 35)
        print(f"Date: {usage_info['date']}")
        
        ops = usage_info['advanced_operations']
        print(f"Advanced Operations: {ops['used']}/{ops['limit']} (remaining: {ops['remaining']})")
        
        calls = usage_info['api_calls']
        print(f"API Calls: {calls['used']}/{calls['limit']} (remaining: {calls['remaining']})")
        
        print(f"Resets: {usage_info['resets_at']}")
        
        # Show feature-specific usage
        feature_usage = usage_info.get('feature_usage', {})
        if feature_usage:
            print(f"\nFeature Usage Today:")
            for feature, count in feature_usage.items():
                print(f"  {feature}: {count}")
        
        return 0
        
    except Exception as e:
        print(f"Error getting usage status: {e}")
        return 1


def upgrade_command(args) -> int:
    """Handle upgrade command."""
    try:
        license_manager = LicenseManager()
        
        # Show upgrade information
        upgrade_info = license_manager.show_upgrade_info()
        print(upgrade_info)
        
        # Open browser if requested
        if args.open_browser:
            success = license_manager.open_upgrade_page()
            if not success:
                print(f"\nCould not open browser automatically.")
                print(f"Please visit: {license_manager.UPGRADE_URL}")
        
        return 0
        
    except Exception as e:
        print(f"Error showing upgrade info: {e}")
        return 1


def _analyze_semantic_transformation_compatibility(source_info, target_type, contextual_info):
    """
    Analyze the semantic compatibility of transforming a matrix to a target type.
    
    Args:
        source_info: Dictionary containing information about source matrix
        target_type: Target matrix type for transformation
        contextual_info: Additional contextual information
        
    Returns:
        Dictionary with compatibility score and recommendations
    """
    compatibility = {
        'compatibility_score': 1.0,
        'semantic_warning': None,
        'recommendations': None,
        'preservation_metrics': {}
    }
    
    source_type = source_info['matrix_type']
    data_type = source_info['data_type']
    shape = source_info['shape']
    
    # Basic matrix type compatibility rules
    type_compatibility = {
        # Source types that work well with target types
        'dense': {'sparse': 0.8, 'orthogonal': 0.9, 'symmetric': 0.9, 'triangular': 0.7},
        'sparse': {'dense': 0.6, 'triangular': 0.8, 'block': 0.7},
        'symmetric': {'dense': 0.9, 'orthogonal': 0.6, 'triangular': 0.5},
        'triangular': {'dense': 0.8, 'sparse': 0.7},
        'diagonal': {'dense': 0.9, 'sparse': 0.9, 'symmetric': 0.7},
        'orthogonal': {'dense': 0.8, 'symmetric': 0.6}
    }
    
    # Data type specific compatibility adjustments
    data_type_adjustments = {
        'tabular': {'sparse': 0.2, 'orthogonal': -0.3},  # Tabular data works well with sparse, poorly with orthogonal
        'image': {'block': 0.2, 'sparse': -0.4},  # Images preserve better in block matrices than sparse
        'text': {'sparse': 0.3, 'dense': -0.1},  # Text often works better with sparse representations
        'json': {'nested': 0.3, 'dense': -0.2},  # JSON structure preserves better in nested formats
        'matrix': {}  # No specific adjustments for generic matrices
    }
    
    # Calculate base compatibility score
    if source_type in type_compatibility and target_type in type_compatibility[source_type]:
        base_score = type_compatibility[source_type][target_type]
    else:
        base_score = 0.5  # Default medium compatibility
    
    # Apply data type adjustments
    adjustment = 0
    if data_type in data_type_adjustments and target_type in data_type_adjustments[data_type]:
        adjustment = data_type_adjustments[data_type][target_type]
    
    compatibility['compatibility_score'] = min(1.0, max(0.1, base_score + adjustment))
    
    # Generate semantic warnings based on compatibility
    if compatibility['compatibility_score'] < 0.5:
        compatibility['semantic_warning'] = f"Converting from {source_type} to {target_type} may lose important {data_type} structural properties"
    
    # Generate recommendations
    if compatibility['compatibility_score'] < 0.7:
        # Find better alternatives
        better_alternatives = []
        if source_type in type_compatibility:
            better_alternatives = [t for t, score in type_compatibility[source_type].items() 
                                if score > compatibility['compatibility_score']]
        
        if better_alternatives:
            compatibility['recommendations'] = f"Consider {', '.join(better_alternatives)} format instead for better semantic preservation"
    
    # Calculate preservation metrics
    compatibility['preservation_metrics'] = {
        'structure_preservation': compatibility['compatibility_score'],
        'information_density': _calculate_information_density(shape, source_type, target_type),
        'interpretability': _calculate_interpretability(data_type, source_type, target_type)
    }
    
    return compatibility

def _calculate_information_density(shape, source_type, target_type):
    """Calculate how well information density is preserved in the transformation."""
    # Simple model based on typical information preservation patterns
    if source_type == 'dense' and target_type == 'sparse':
        # Dense to sparse may lose information unless data is naturally sparse
        return 0.7
    elif source_type == 'sparse' and target_type == 'dense':
        # Sparse to dense preserves information but adds redundancy
        return 0.9
    elif source_type == target_type:
        # Same type transformations generally preserve information density
        return 1.0
    else:
        # Default moderate preservation
        return 0.8

def _calculate_interpretability(data_type, source_type, target_type):
    """Calculate how interpretable the data remains after transformation."""
    # Different data types have different interpretability requirements
    if data_type == 'image':
        if target_type in ['dense', 'block']:
            return 0.9
        else:
            return 0.6
    elif data_type == 'tabular':
        if target_type in ['sparse', 'dense']:
            return 0.9
        else:
            return 0.5
    elif data_type == 'text':
        if target_type in ['sparse', 'nested']:
            return 0.8
        else:
            return 0.6
    else:
        # Default moderate interpretability
        return 0.7


def _interpret_connection_meaning(source_info, target_info, bridges, semantic_links, semantic_compatibility):
    """Interpret the meaning of connections between datasets with rich context."""
    connection_meanings = []
    
    # Analyze based on contextual bridges
    if bridges:
        bridge_types = [b.get('bridge_type') for b in bridges]
        
        if 'common_column' in bridge_types:
            common_columns = [b.get('bridge_name') for b in bridges if b.get('bridge_type') == 'common_column']
            connection_meanings.append({
                'type': 'column_overlap',
                'description': f"Datasets share {len(common_columns)} common columns: {', '.join(common_columns[:3])}{'...' if len(common_columns) > 3 else ''}",
                'importance': 'high',
                'confidence': 0.9
            })
            
        if 'data_type_match' in bridge_types:
            connection_meanings.append({
                'type': 'data_type_compatibility',
                'description': f"Datasets share compatible data types",
                'importance': 'medium',
                'confidence': 0.7
            })
    
    # Analyze based on semantic links
    if semantic_links:
        link_types = [link.get('type') for link in semantic_links]
        
        if 'statistical_similarity' in link_types:
            stats_links = [link for link in semantic_links if link.get('type') == 'statistical_similarity']
            if stats_links and stats_links[0].get('mean_similarity') > 0.5:
                connection_meanings.append({
                    'type': 'statistical_patterns',
                    'description': "Datasets show similar statistical distributions and patterns",
                    'importance': 'medium',
                    'confidence': 0.8
                })
    
    # Analyze based on semantic compatibility
    if semantic_compatibility > 0.8:
        connection_meanings.append({
            'type': 'semantic_similarity',
            'description': f"Datasets have high semantic compatibility ({semantic_compatibility:.2f})",
            'importance': 'high',
            'confidence': semantic_compatibility
        })
    
    # If no specific meanings were found, provide a general interpretation
    if not connection_meanings:
        if semantic_compatibility > 0.5:
            connection_meanings.append({
                'type': 'general_similarity',
                'description': "Datasets show general structural similarities",
                'importance': 'low',
                'confidence': semantic_compatibility
            })
    
    return connection_meanings


def _assess_data_flow_potential(source_info, target_info):
    """Assess potential data flow and transformation paths between datasets."""
    flow_potential = {
        'compatibility': 0.0,
        'transformation_difficulty': 0.0,
        'recommended_steps': [],
        'expected_quality': 0.0
    }
    
    # Check basic compatibility
    same_data_type = source_info['data_type'] == target_info['data_type']
    flow_potential['compatibility'] = 0.8 if same_data_type else 0.4
    
    # Assess transformation difficulty
    if same_data_type:
        flow_potential['transformation_difficulty'] = 0.2  # Easy
        flow_potential['expected_quality'] = 0.9
        flow_potential['recommended_steps'] = [{
            'step': 'direct_mapping',
            'description': f"Direct column mapping between {source_info['file_name']} and {target_info['file_name']}"
        }]
    else:
        # More complex transformation required
        flow_potential['transformation_difficulty'] = 0.6  # Medium
        flow_potential['expected_quality'] = 0.7
        flow_potential['recommended_steps'] = [
            {
                'step': 'type_conversion',
                'description': f"Convert from {source_info['data_type']} to intermediate format"
            },
            {
                'step': 'structural_mapping',
                'description': "Map data structure between formats"
            },
            {
                'step': 'target_conversion',
                'description': f"Convert to target {target_info['data_type']} format"
            }
        ]
    
    return flow_potential


def _extract_key_entities_from_dataset(dataset, metadata):
    """
    Extract key entities from a dataset for contextual analysis using sophisticated methods.
    
    This function leverages the existing entity matching and extraction infrastructure
    already implemented in tensorpack for comprehensive entity discovery.
    """
    entities = []
    
    try:
        # Create dataset info structure for compatibility with existing methods
        dataset_info = {
            'data_type': metadata.get('data_type', 'unknown') if metadata else 'unknown',
            'matrix_type': metadata.get('matrix_type', 'unknown') if metadata else 'unknown',
            'shape': dataset.shape if hasattr(dataset, 'shape') else (),
            'file_name': metadata.get('file_path', 'unknown') if metadata else 'unknown',
            'file_path': metadata.get('file_path', '') if metadata else ''
        }
        
        # Method 1: Extract text-based entities using existing NLP methods
        text_entities = _extract_text_for_nlp(dataset, dataset_info)
        for text in text_entities:
            if isinstance(text, str) and len(text.strip()) > 0:
                # Extract meaningful terms from text
                words = re.findall(r'\b\w+\b', text.lower())
                # Filter out common stop words and keep meaningful entities
                meaningful_words = [w for w in words if len(w) > 2 and w not in {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'}]
                entities.extend(meaningful_words[:10])  # Take top 10 meaningful words
        
        # Method 2: Use existing contextual information extraction
        contextual_info = _extract_contextual_info(metadata, None)
        
        # Extract entities from column names (tabular data)
        if contextual_info.get('column_names'):
            entities.extend(contextual_info['column_names'][:15])  # Limit to 15 columns
        
        # Extract entities from dictionary keys (JSON/structured data)
        if contextual_info.get('dict_keys'):
            entities.extend(contextual_info['dict_keys'][:15])  # Limit to 15 keys
        
        # Extract entities from file path components
        if contextual_info.get('data_source'):
            file_path = contextual_info['data_source']
            # Extract filename components as entities
            filename = os.path.basename(file_path)
            name_parts = re.split(r'[._\-\s]+', os.path.splitext(filename)[0])
            entities.extend([part for part in name_parts if len(part) > 1])
        
        # Method 3: Use existing local relationship finder for deeper entity extraction
        if metadata:
            # Use the sophisticated local relationship finder
            local_relationships = _find_local_contextual_relationships(
                dataset, "entity_extraction", metadata, dataset_info
            )
            
            # Extract entities from significant elements found
            if 'significant_elements' in local_relationships:
                for element in local_relationships['significant_elements']:
                    entity_name = element.get('entity_name', '')
                    if entity_name and len(entity_name) > 1:
                        entities.append(entity_name)
            
            # Extract entities from contextual connections
            if 'contextual_connections' in local_relationships:
                for connection in local_relationships['contextual_connections']:
                    connection_entity = connection.get('connection_entity', '')
                    if connection_entity and len(connection_entity) > 1:
                        entities.append(connection_entity)
        
        # Method 4: Extract domain-specific entities using existing matchers
        data_type = dataset_info.get('data_type', 'unknown')
        try:
            domain_entities = _apply_domain_specific_matchers(dataset, "auto_extract", dataset_info)
            for match in domain_entities:
                entity = match.get('entity', '')
                if entity and len(entity) > 1:
                    entities.append(entity)
        except Exception as e:
            # If domain-specific matching fails, continue with other methods
            pass
        
        # Method 5: Use semantic similarity matching for pattern-based entity extraction
        try:
            semantic_entities = _apply_semantic_similarity_matching(dataset, "pattern_discovery", dataset_info)
            for match in semantic_entities:
                entity = match.get('entity', '')
                if entity and len(entity) > 1:
                    entities.append(entity)
        except Exception as e:
            # If semantic matching fails, continue with other methods
            pass
        
        # Method 6: Content-type specific entity extraction
        content_type = contextual_info.get('content_type', 'unknown')
        
        if content_type == 'tabular_data':
            # Extract statistical entities from numeric columns
            if contextual_info.get('numeric_columns', 0) > 0:
                entities.extend([f"numeric_col_{i}" for i in range(min(5, contextual_info.get('numeric_columns', 0)))])
            
            # Extract unique value entities
            unique_values = contextual_info.get('unique_values_per_column', {})
            for col, count in list(unique_values.items())[:5]:
                entities.append(f"{col}_unique_{count}")
        
        elif content_type == 'text_data':
            # Extract text-specific entities
            text_length = contextual_info.get('text_length', 0)
            if text_length > 0:
                entities.append(f"text_length_{text_length}")
            
            # Extract encoding information as entity
            encoding = contextual_info.get('encoding', '')
            if encoding:
                entities.append(f"encoding_{encoding}")
        
        elif content_type == 'image_data':
            # Extract image-specific entities
            image_shape = contextual_info.get('image_dimensions', 0)
            if image_shape > 0:
                entities.append(f"image_{image_shape}d")
            
            color_channels = contextual_info.get('color_channels', 0)
            if color_channels > 0:
                entities.append(f"channels_{color_channels}")
        
        elif content_type == 'structured_data':
            # Extract nested structure entities
            nested_structure = contextual_info.get('nested_structure', {})
            if nested_structure and isinstance(nested_structure, dict):
                for key, value in list(nested_structure.items())[:5]:
                    if isinstance(value, dict) and 'type' in value:
                        entities.append(f"{key}_{value['type']}")
        
        # Method 7: Extract matrix-type specific entities
        matrix_type = dataset_info.get('matrix_type', 'unknown')
        if matrix_type != 'unknown':
            entities.append(f"matrix_{matrix_type}")
            
            # Add complexity and efficiency as entities
            shape = dataset_info.get('shape', ())
            if shape:
                complexity = get_complexity(matrix_type, shape)
                efficiency = get_memory_efficiency(matrix_type)
                entities.extend([
                    f"complexity_{int(complexity/1000)}k",
                    f"efficiency_{int(efficiency*100)}pct"
                ])
        
        # Clean and deduplicate entities
        cleaned_entities = []
        seen_entities = set()
        
        for entity in entities:
            if isinstance(entity, str):
                # Clean the entity string
                cleaned_entity = re.sub(r'[^\w\s-]', '', str(entity).strip().lower())

                # Skip very short or empty entities
                if len(cleaned_entity) < 2:
                    continue
                
                # Skip duplicates
                if cleaned_entity in seen_entities:
                    continue
                
                seen_entities.add(cleaned_entity)
                cleaned_entities.append(cleaned_entity)
        
        # Limit total entities to prevent overwhelming output
        final_entities = cleaned_entities[:25]  # Top 25 entities
        
        return final_entities
        
    except Exception as e:
        # Fallback to basic extraction if sophisticated methods fail
        fallback_entities = []
        
        # Basic fallback: extract from metadata
        if metadata:
            if metadata.get('is_tabular') and 'columns' in metadata:
                fallback_entities.extend(metadata['columns'][:10])
            elif metadata.get('is_dict') and 'keys' in metadata:
                fallback_entities.extend(metadata['keys'][:10])
            elif metadata.get('data_type'):
                fallback_entities.append(metadata['data_type'])
        
        # Basic fallback: extract from dataset properties
        if isinstance(dataset, np.ndarray):
            if dataset.ndim == 2 and dataset.shape[0] > 0 and dataset.shape[1] > 0:
                fallback_entities.append(f"array_shape_{dataset.shape[0]}x{dataset.shape[1]}")
            fallback_entities.append(f"dtype_{dataset.dtype}")
            fallback_entities.append(f"ndim_{dataset.ndim}")
        
        return fallback_entities[:10]  # Limit fallback entities


def _compute_shared_entity_confidence(entity: dict, source_info: dict = None, target_info: dict = None) -> float:
    """Compute a numeric confidence score for a shared entity.

    Uses occurrence counts, uniqueness (generic token penalty), key-entity flags,
    and optional semantic name similarity (if present) to produce a score in [0,1].
    """
    try:
        name = (entity.get('entity_name') or '').lower()
        # Occurrence counts (fallback to 1 if not available)
        s_count = float(entity.get('source_count', 1))
        t_count = float(entity.get('target_count', 1))

        # Occurrence score: prefer presence in both and balanced counts
        if s_count > 0 and t_count > 0:
            occ_ratio = min(s_count, t_count) / max(1.0, max(s_count, t_count))
            occurrence_score = 0.5 + 0.5 * occ_ratio  # range [0.5,1.0]
        else:
            occurrence_score = 0.0

        # Uniqueness: penalize generic metadata tokens
        generic_entities = {'file', 'tsv', 'csv', 'dataset', 'shape', 'type', 'data', 'format', 'path'}
        uniqueness_score = 0.0 if name in generic_entities or name.strip() == '' else 1.0

        # Key entity boost / importance proxy
        importance = entity.get('importance')
        if entity.get('is_key', False):
            key_score = 1.0
        elif importance == 'high':
            key_score = 0.9
        elif importance == 'medium':
            key_score = 0.6
        elif importance == 'low':
            key_score = 0.3
        else:
            key_score = 0.4

        # Optional semantic name similarity (0.0-1.0)
        sem_sim = float(entity.get('name_similarity', 0.0)) if entity.get('name_similarity') is not None else 0.0

        # Weighted combination
        score = (0.4 * occurrence_score +
                 0.25 * uniqueness_score +
                 0.2 * key_score +
                 0.15 * sem_sim)

        return max(0.0, min(1.0, float(score)))
    except Exception:
        return 0.0


# ============================================================================
# Rich CLI Visualization Functions for traverse_graph_command
# ============================================================================

def _display_pathway_table(exploration_results, source_dataset, target_dataset, args):
    """Display connection exploration results as a rich table."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich import box
        
        console = Console()
        
        # Check if there was an error in pathway exploration
        if exploration_results.get('error'):
            console.print(f"Error in pathway exploration: {exploration_results['error']}", style="red")
            return
            
        # Extract pathway information from exploration results
        # The actual structure uses different keys - check for actual pathways
        pathways = exploration_results.get('pathways', [])
        contextual_connections = exploration_results.get('contextual_connections', [])
        semantic_connections = exploration_results.get('semantic_connections', [])
        shared_entities = exploration_results.get('shared_entities', [])
        confidence = exploration_results.get('confidence', 0.0)
        
        # Check if we have any meaningful pathway data
        has_connections = (pathways or contextual_connections or semantic_connections or 
                          shared_entities or confidence > 0.0)
        
        if not has_connections:
            console.print("No connections found between datasets", style="yellow")
            return
            
        # Create main connection table
        table = Table(
            title=f"Connection from `{source_dataset}` → `{target_dataset}`",
            box=box.HEAVY_HEAD,
            show_header=True,
            header_style="bold blue"
        )
        
        table.add_column("Connection Type", style="cyan", width=18)
        table.add_column("Entity/Source", style="green", width=20)
        table.add_column("Relation", style="yellow", width=18)
        table.add_column("Target", style="magenta", width=20)
        table.add_column("Confidence", style="red", width=12)
        
        # Display contextual connections (the actual pathway data)
        if contextual_connections:
            console.print(f"\nFound {len(contextual_connections)} contextual connections:", style="bold green")
            for i, connection in enumerate(contextual_connections[:10]):  # Show top 10
                # Get the entity name - prefer column_name over entity_name, fall back to location
                display_entity = (connection.get('column_name') or 
                                connection.get('entity_name') or 
                                connection.get('location', 'Unknown'))[:18]
                
                source = connection.get('source', 'Unknown')[:18]
                target = connection.get('target', 'Unknown')[:18]
                conn_type = connection.get('connection_type', 'cross_entity')[:16]
                confidence = connection.get('confidence', 0.0)
                
                # Create more informative description
                description = connection.get('description', '')
                if 'column' in description and '"' in description:
                    # Extract actual semantic meaning from description
                    description = description[:18]
                else:
                    description = display_entity[:18]
                
                table.add_row(
                    conn_type,
                    display_entity,
                    f"{source} → {target}",
                    description,
                    f"{confidence:.3f}"
                )
        
        # Display semantic connections
        if semantic_connections:
            console.print(f"\nFound {len(semantic_connections)} semantic connections:", style="bold blue")
            for connection in semantic_connections[:5]:
                conn_type = connection.get('connection_type', 'semantic')[:16]
                source_field = connection.get('source_field', 'Unknown')[:18]
                target_field = connection.get('target_field', 'Unknown')[:18]
                strength = connection.get('strength', 0.0)
                
                table.add_row(
                    conn_type,
                    source_field,
                    "semantic_link",
                    target_field,
                    f"{strength:.3f}"
                )
        
        # Display shared entities (filter out generic metadata)
        if shared_entities:
            # Filter out generic metadata entities that aren't semantically meaningful
            generic_entities = {'file', 'tsv', 'csv', 'dataset', 'shape', 'type', 'data', 'format', 'path'}
            meaningful_entities = [e for e in shared_entities 
                                 if e.get('entity_name', '').lower() not in generic_entities]
            
            if meaningful_entities:
                console.print(f"\nFound {len(meaningful_entities)} shared entities:", style="bold magenta")
                for entity in meaningful_entities[:5]:
                    entity_name = entity.get('entity_name', 'Unknown')[:18]
                    # Prefer numeric confidence if present; otherwise compute a score
                    confidence = entity.get('confidence')
                    if confidence is None:
                        confidence = _compute_shared_entity_confidence(entity)

                    table.add_row(
                        "shared_entity",
                        entity_name,
                        "appears_in_both",
                        "both_datasets",
                        f"{float(confidence):.3f}"
                    )
            else:
                console.print(f"\nFound {len(shared_entities)} shared entities (all metadata):", style="dim")
                # Optionally show a few metadata entities with low emphasis
                for entity in shared_entities[:2]:
                    entity_name = entity.get('entity_name', 'Unknown')[:18]
                    # compute fallback confidence
                    confidence = entity.get('confidence')
                    if confidence is None:
                        confidence = _compute_shared_entity_confidence(entity)

                    table.add_row(
                        "metadata",
                        entity_name,
                        "technical_shared",
                        "both_datasets",
                        f"{float(confidence):.3f}"
                    )
        
        # Add connection steps from standard connections if they exist
        for i, pathway in enumerate(pathways[:5]):  # Show top 5 connections
            steps = pathway.get('steps', [])
            if steps:
                console.print(f"\nConnection {i+1}:", style="bold")
                for j, step in enumerate(steps):
                    source = step.get('source', 'Unknown')[:18]
                    target = step.get('target', 'Unknown')[:18] 
                    relation = step.get('relation', 'connects_to')[:16]
                    score = step.get('score', 0.0)
                    
                    table.add_row(
                        f"pathway_{i+1}",
                        source,
                        relation,
                        target,
                        f"{score:.3f}"
                    )
        
        console.print(table)
        
        # Display summary statistics
        console.print(f"\nConnection Analysis Summary:", style="bold")
        
        # Enhanced confidence reporting with component breakdown  
        # Always use the top-level confidence from exploration_results for consistency
        console.print(f"  • Pathway confidence: {confidence:.3f} ({confidence*100:.1f}%)")
        
        # Show confidence breakdown if verbose mode or high confidence
        if hasattr(args, 'verbose') and args.verbose and confidence > 0.3:
            # Show structural components for display (not recalculated confidence)
            shared_entities = exploration_results.get('shared_entities', [])
            semantic_connections = exploration_results.get('semantic_connections', [])
            contextual_bridges = exploration_results.get('contextual_bridges', [])
            
            if len(shared_entities) > 0 or len(semantic_connections) > 0:
                console.print("    ┣━ Confidence breakdown:", style="dim")
                
                # Show actual structural component strengths using tier system
                # Entity overlap strength
                entity_count = len(shared_entities)
                if entity_count >= 10:
                    entity_strength = 1.0
                elif entity_count >= 5:
                    entity_strength = 0.8
                elif entity_count >= 1:
                    entity_strength = 0.6
                else:
                    entity_strength = 0.0
                
                # Semantic connection strength  
                semantic_count = len(semantic_connections)
                if semantic_count >= 20:
                    semantic_strength = 1.0
                elif semantic_count >= 10:
                    semantic_strength = 0.8
                elif semantic_count >= 5:
                    semantic_strength = 0.6
                elif semantic_count >= 1:
                    semantic_strength = 0.3
                else:
                    semantic_strength = 0.0
                
                # Contextual bridge strength
                bridge_count = len(contextual_bridges)
                if bridge_count >= 50:
                    bridge_strength = 1.0
                elif bridge_count >= 10:
                    bridge_strength = 0.7
                elif bridge_count >= 1:
                    bridge_strength = 0.4
                else:
                    bridge_strength = 0.0
                
                console.print(f"    ┣━ Entity overlap: {entity_strength:.2f} ({len(shared_entities)} shared)", style="dim")
                console.print(f"    ┣━ Semantic links: {semantic_strength:.2f} ({len(semantic_connections)} connections)", style="dim")
                console.print(f"    ┗━ Contextual bridges: {bridge_strength:.2f} ({len(contextual_bridges)} bridges)", style="dim")
        
        # Show average connection quality as additional context (not primary confidence)
        if contextual_connections and hasattr(args, 'verbose') and args.verbose:
            avg_connection_conf = sum(c.get('confidence', 0) for c in contextual_connections) / len(contextual_connections)
            console.print(f"    ┗━ Average connection quality: {avg_connection_conf:.3f}", style="dim")
                
        console.print(f"  • Contextual connections: {len(contextual_connections)}")
        console.print(f"  • Semantic connections: {len(semantic_connections)}")
        
        # More accurate shared entity reporting
        if shared_entities:
            generic_entities = {'file', 'tsv', 'csv', 'dataset', 'shape', 'type', 'data', 'format', 'path'}
            meaningful_count = len([e for e in shared_entities 
                                  if e.get('entity_name', '').lower() not in generic_entities])
            console.print(f"  • Shared data entities: {meaningful_count}")
            console.print(f"  • Shared system entities: {len(shared_entities) - meaningful_count}")
        else:
            console.print(f"  • Shared entities: {len(shared_entities)}")
            
        console.print(f"  • Direct connections: {len(pathways)}")
        
        # Show confidence interpretation with updated thresholds for dual-component scoring
        # Always use the top-level confidence for status assessment for consistency
        if confidence > 0.6:
            console.print(f"  • Status: Strong connection detected", style="green")
        elif confidence > 0.35:
            console.print(f"  • Status: Moderate connection detected", style="yellow")
        elif confidence > 0.15:
            console.print(f"  • Status: Weak connection detected", style="blue")
        else:
            console.print(f"  • Status: No significant connection", style="red")
            
        # Display summary from exploration results if available
        summary = exploration_results.get('summary', {})
        if summary:
            console.print(f"  • Additional info: {summary.get('total_pathways', 'N/A')} total connections")
            console.print(f"  • Average connection length: {summary.get('avg_pathway_length', 'N/A')}")
            console.print(f"  • Strongest connection: {summary.get('strongest_score', 'N/A')}")
            
    except ImportError:
        # Fallback to simple text display
        print(f"\nPathway from {source_dataset} → {target_dataset}")
        print("=" * 60)
        
        # Check for error
        if exploration_results.get('error'):
            print(f"Error: {exploration_results['error']}")
            return
            
        # Display available pathway data
        contextual_connections = exploration_results.get('contextual_connections', [])
        semantic_connections = exploration_results.get('semantic_connections', [])
        shared_entities = exploration_results.get('shared_entities', [])
        confidence = exploration_results.get('confidence', 0.0)
        pathways = exploration_results.get('pathways', [])
        
        print(f"Overall Confidence: {confidence:.3f} ({confidence*100:.1f}%)")
        
        if contextual_connections:
            print(f"\nContextual Connections ({len(contextual_connections)}):")
            for i, conn in enumerate(contextual_connections[:5]):
                entity = conn.get('entity_name', 'Unknown')
                conf = conn.get('confidence', 0.0)
                desc = conn.get('description', '')
                print(f"  {i+1}. {entity} (confidence: {conf:.3f}) - {desc}")
        
        if semantic_connections:
            print(f"\nSemantic Connections ({len(semantic_connections)}):")
            for i, conn in enumerate(semantic_connections[:3]):
                conn_type = conn.get('connection_type', 'semantic')
                strength = conn.get('strength', 0.0)
                print(f"  {i+1}. {conn_type} (strength: {strength:.3f})")
        
        if shared_entities:
            print(f"\nShared Entities ({len(shared_entities)}):")
            for i, entity in enumerate(shared_entities[:3]):
                name = entity.get('entity_name', 'Unknown')
                importance = entity.get('importance', 'medium')
                print(f"  {i+1}. {name} (importance: {importance})")
        
        if pathways:
            print(f"\nDirect Connections ({len(pathways)}):")
            for i, pathway in enumerate(pathways[:3]):
                print(f"\nConnection {i+1}:")
                steps = pathway.get('steps', [])
                for j, step in enumerate(steps):
                    source = step.get('source', 'Unknown')
                    target = step.get('target', 'Unknown')
                    relation = step.get('relation', 'connects_to')
                    score = step.get('score', 0.0)
                    print(f"  {j+1}. {source} --[{relation}]--> {target} (score: {score:.3f})")
        
        if not (contextual_connections or semantic_connections or shared_entities or pathways):
            print("No connection data found in results")
        else:
            status = "Strong" if confidence > 0.05 else "Moderate" if confidence > 0.01 else "Weak"
            print(f"\nStatus: {status} connection detected")


def _display_bridge_finder_summary(exploration_results):
    """Display bridge finder results as a bar chart."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.progress import Progress, BarColumn, TextColumn
        from rich import box
        
        console = Console()
        
        # Extract bridge information - check for both 'bridges' and 'bridge_datasets' keys
        bridges = exploration_results.get('bridges', [])
        if not bridges:
            bridges = exploration_results.get('bridge_datasets', [])
        
        if not bridges:
            console.print("No bridge datasets found", style="yellow")
            return
            
        # Create bridge summary table
        table = Table(
            title="Bridge Datasets",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Dataset", style="green", width=25)
        table.add_column("Bridge Score", style="yellow", width=15)
        table.add_column("Connections", style="blue", width=15)
        table.add_column("Visualization", style="red", width=25)
        
        # Sort bridges by score
        sorted_bridges = sorted(bridges, key=lambda x: x.get('bridge_score', 0), reverse=True)
        
        # Add bridge data with bar visualization
        for bridge in sorted_bridges[:10]:  # Top 10 bridges
            # Extract dataset name from bridge_dataset info (correct structure)
            bridge_dataset = bridge.get('bridge_dataset', {})
            dataset_name = (
                bridge_dataset.get('file_name') or 
                bridge_dataset.get('dataset_name') or 
                bridge.get('dataset_name') or 
                bridge.get('file_name') or 
                'Unknown'
            )[:23]
            
            score = bridge.get('bridge_score', 0.0)
            connections = bridge.get('connectivity_count', bridge.get('connection_count', 0))
            
            # Create visual bar using block characters
            bar_length = int(score * 20)  # Scale to 20 characters max
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            table.add_row(
                dataset_name,
                f"{score:.2f}",
                str(connections),
                f"{bar} {score:.1%}"
            )
        
        console.print(table)
        
        # Display bridge analysis summary
        summary = exploration_results.get('summary', {})
        if summary:
            console.print(f"\nBridge Analysis:", style="bold")
            console.print(f"  • Total datasets analyzed: {summary.get('total_datasets', 'N/A')}")
            console.print(f"  • Bridge datasets found: {len(bridges)}")
            console.print(f"  • Top bridge score: {max([b.get('bridge_score', 0) for b in bridges]) if bridges else 'N/A':.2f}")
            
    except ImportError:
        # Fallback to simple text display
        print("\nBridge Datasets")
        print("=" * 50)
        bridges = exploration_results.get('bridges', [])
        if not bridges:
            bridges = exploration_results.get('bridge_datasets', [])
            
        sorted_bridges = sorted(bridges, key=lambda x: x.get('bridge_score', 0), reverse=True)
        
        for bridge in sorted_bridges[:10]:
            # Handle different possible field names for dataset name
            dataset_name = (bridge.get('dataset_name') or 
                          bridge.get('bridge_dataset', {}).get('file_name') or
                          bridge.get('file_name') or 
                          'Unknown')
            score = bridge.get('bridge_score', 0.0)
            connections = bridge.get('connection_count', bridge.get('connectivity_count', 0))
            
            # Simple bar using asterisks
            bar_length = int(score * 20)
            bar = "*" * bar_length
            print(f"  {dataset_name:<25} {bar:<20} {score:.2f} ({connections} connections)")


def _display_pathway_tree(exploration_results, search_entity):
    """Display entity search results as a connection tree using actual data structure."""
    try:
        from rich.console import Console
        from rich.tree import Tree
        from rich.text import Text
        
        console = Console()
        
        # Check if we have results in the expected format
        results = exploration_results.get('results', [])
        
        if not results:
            console.print(f"No results found for entity: '{search_entity}'", style="yellow")
            return
            
        # Create main tree
        tree = Tree(
            Text(f"Entity Search: \"{search_entity}\"", style="bold blue"),
            style="tree"
        )
        
        # Process each dataset result
        for result in results:
            dataset_name = result.get('dataset_name', 'Unknown Dataset')
            entity_matches = result.get('entity_matches', [])
            relevance_score = result.get('relevance_score', 0.0)
            
            # Create dataset branch
            dataset_label = f"{dataset_name}"
            if relevance_score > 0:
                dataset_label += f" (relevance: {relevance_score:.1%})"
                
            dataset_branch = tree.add(
                Text(dataset_label, style="green bold"),
                style="tree"
            )
            
            # Add entity matches
            if entity_matches:
                matches_shown = 0
                for match in entity_matches:
                    if matches_shown >= 8:  # Limit display to avoid clutter
                        remaining = len(entity_matches) - matches_shown
                        dataset_branch.add(Text(f"... and {remaining} more matches", style="dim"))
                        break
                        
                    match_type = match.get('type', 'unknown')
                    value = match.get('value', search_entity)
                    confidence = match.get('confidence', 0.0)
                    context = match.get('context', '')
                    
                    # Format match display
                    match_text = f"└── {match_type}: {value}"
                    if confidence > 0:
                        match_text += f" (conf: {confidence:.1%})"
                    if context:
                        # Truncate long context
                        short_context = context[:60] + "..." if len(context) > 60 else context
                        match_text += f" - {short_context}"
                    
                    # Color code by match type
                    if match_type == 'exact_match':
                        style = "bright_green"
                    elif 'semantic' in match_type:
                        style = "cyan"
                    elif 'pattern' in match_type:
                        style = "yellow"
                    else:
                        style = "white"
                        
                    dataset_branch.add(Text(match_text, style=style))
                    matches_shown += 1
            else:
                dataset_branch.add(Text("└── No direct matches found", style="dim"))
                
        console.print(tree)
        
        # Display summary statistics
        total_matches = sum(len(r.get('entity_matches', [])) for r in results)
        datasets_with_matches = sum(1 for r in results if r.get('entity_matches'))
        
        console.print(f"\nSearch Summary:", style="bold")
        console.print(f"  • Datasets searched: {len(results)}")
        console.print(f"  • Datasets with matches: {datasets_with_matches}")
        console.print(f"  • Total matches found: {total_matches}")
        
        # Show top matches by relevance
        top_results = sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)[:3]
        if top_results:
            console.print(f"\nTop Results:", style="bold")
            for i, result in enumerate(top_results, 1):
                dataset_name = result.get('dataset_name', 'Unknown')
                score = result.get('relevance_score', 0.0)
                match_count = len(result.get('entity_matches', []))
                console.print(f"  {i}. {dataset_name}: {match_count} matches (score: {score:.2f})")
            
    except ImportError:
        # Fallback to simple text display
        print(f"\nEntity Search: \"{search_entity}\"")
        print("=" * 60)
        
        results = exploration_results.get('results', [])
        
        if not results:
            print("No matches found")
            return
            
        for result in results:
            dataset_name = result.get('dataset_name', 'Unknown Dataset')
            entity_matches = result.get('entity_matches', [])
            relevance_score = result.get('relevance_score', 0.0)
            
            print(f"\n{dataset_name} (relevance: {relevance_score:.1%})")
            
            if entity_matches:
                for i, match in enumerate(entity_matches[:5]):  # Show top 5
                    match_type = match.get('type', 'unknown')
                    value = match.get('value', search_entity)
                    confidence = match.get('confidence', 0.0)
                    context = match.get('context', '')[:50]
                    
                    print(f"  └── {match_type}: {value} (conf: {confidence:.1%})")
                    if context:
                        print(f"      {context}...")
                        
                if len(entity_matches) > 5:
                    print(f"  ... and {len(entity_matches) - 5} more matches")
            else:
                print("  └── No direct matches found")
                
          # Summary
        total_matches = sum(len(r.get('entity_matches', [])) for r in results)
        print(f"\nTotal: {total_matches} matches across {len(results)} datasets")

    except ImportError:
        # Fallback to simple text display
        print(f"\nEntity Search: \"{search_entity}\"")
        print("=" * 60)
        
        findings = exploration_results.get('entity_findings', {})
        datasets = findings.get('datasets', {})
        
        for dataset_name, dataset_info in datasets.items():
            print(f"\n{dataset_name}")
            occurrences = dataset_info.get('occurrences', [])
            
            if occurrences:
                for occurrence in occurrences[:5]:
                    location = occurrence.get('location', 'Unknown')
                    context = occurrence.get('context', '')[:50]
                    print(f"  └── {location}: {context}...")
            else:
                print("  └── No direct matches found")
                
        # Show related entities
        related = findings.get('related_entities', [])
        if related:
            print(f"\nRelated Entities:")
            for entity in related[:5]:
                name = entity.get('name', 'Unknown')
                relation = entity.get('relation', 'related_to')
                score = entity.get('score', 0.0)
                print(f"  └── {name} ({relation}, score: {score:.2f})")

if __name__ == '__main__':
    sys.exit(main())