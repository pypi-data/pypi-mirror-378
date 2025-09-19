def _extract_key_entities_from_dataset(dataset, metadata):
    """
    Extract key entities (names, identifiers) from a dataset based on its metadata.
    
    This function analyzes dataset metadata to identify key entities like:
    - Column names in tabular data
    - Unique identifiers/keys
    - Important string values
    - Headers from text data
    
    Args:
        dataset: The dataset array
        metadata: Dataset metadata from _get_general_metadata
        
    Returns:
        List of key entity strings
    """
    key_entities = []
    
    try:
        if not metadata:
            return key_entities
        
        # For tabular data
        if metadata.get('is_tabular'):
            df = metadata.get('dataframe')
            if df is not None:
                # Add column names as entities
                key_entities.extend(list(df.columns))
                
                # Add values from categorical columns (limit to avoid explosion)
                for col in df.columns:
                    if df[col].dtype == 'object':  # String columns
                        # Get most frequent values
                        try:
                            value_counts = df[col].value_counts()
                            if len(value_counts) > 0:
                                # Add top values if they appear multiple times
                                for val, count in value_counts.items():
                                    if count > 1 and isinstance(val, str) and val:
                                        if len(val) > 3:  # Skip very short values
                                            key_entities.append(val)
                                            if len(key_entities) > 20:
                                                break
                        except:
                            pass
                
                # Add column names from common ID columns
                id_columns = [col for col in df.columns if 'id' in col.lower()]
                key_entities.extend(id_columns)
                
        # For text data
        elif metadata.get('data_type') == 'text':
            text_content = metadata.get('text_content', '')
            if text_content:
                # Extract potential headers (lines with all caps or followed by newlines)
                lines = text_content.split('\n')
                for line in lines:  # Only check first 30 lines
                    line = line.strip()
                    if line and (line.isupper() or len(line) < 50):
                        key_entities.append(line)
        
        # Add dataset name components
        if 'file_path' in metadata:
            import os
            filename = os.path.basename(metadata['file_path'])
            name_parts = os.path.splitext(filename)[0].split('_')
            for part in name_parts:
                if len(part) > 2:  # Skip very short parts
                    key_entities.append(part)
            
            # Also add file extension as entity
            ext = os.path.splitext(filename)[1][1:]  # Remove the dot
            if ext:
                key_entities.append(ext)
        
        # Add domain context if available
        if 'domain_context' in metadata:
            domain = metadata['domain_context'].get('domain', '')
            if domain:
                key_entities.append(domain)
            
            # Add domain-specific entities
            domain_entities = metadata['domain_context'].get('entities', [])
            if domain_entities:
                key_entities.extend(domain_entities)  # Limit to top 10
        
        # For JSON data
        if metadata.get('data_type') == 'json':
            json_keys = metadata.get('json_keys', [])
            if json_keys:
                key_entities.extend(json_keys)  # Limit to first 20 keys
        
        # For general metadata, extract entity names
        if 'entity_map' in metadata:
            entity_ids = metadata.get('entity_ids', [])
            key_entities.extend(entity_ids)
        
        # Deduplicate and clean
        clean_entities = []
        seen = set()
        for entity in key_entities:
            if not isinstance(entity, str):
                continue
                
            entity = str(entity).strip()
            if entity and entity not in seen and len(entity) > 1:
                clean_entities.append(entity)
                seen.add(entity)
                
                # Limit to reasonable number
                if len(clean_entities) >= 30:
                    break
        
        return clean_entities
        
    except Exception as e:
        import logging
        logging.warning(f"Error extracting key entities: {str(e)}")
        return []
