"""
Pipeline 2: Helper functions
Utility functions for value detection and unit inference
"""


def detect_value_type(value):
    """
    Detect if a value is continuous (numeric) or categorical (string)
    
    Args:
        value: Any value to analyze
    
    Returns:
        str: 'continuous' if numeric, 'categorical' otherwise
    """
    if value is None:
        return 'categorical'
    
    str_value = str(value).strip()
    
    if not str_value:
        return 'categorical'
    
    # Try to convert to float
    try:
        float(str_value)
        return 'continuous'
    except ValueError:
        return 'categorical'


def guess_unit(column_name):
    """
    Infer unit from column header name using pattern matching
    
    Args:
        column_name: str, the column header name
    
    Returns:
        str or None, the guessed unit or None if no match
    """
    if not column_name:
        return None
    
    column_lower = column_name.lower()
    
    # Population/Count patterns
    if any(word in column_lower for word in ['population', 'count', 'jumlah', 'total']):
        return 'persons'
    
    # Distance/Length patterns
    if any(word in column_lower for word in ['distance', 'length', 'jarak', 'panjang']):
        return 'km'
    
    # Area patterns
    if any(word in column_lower for word in ['area', 'luas']):
        return 'km²'
    
    # Volume/Water patterns
    if any(word in column_lower for word in ['volume', 'water', 'air', 'liquid']):
        return 'L'
    
    # Weight/Mass patterns
    if any(word in column_lower for word in ['weight', 'mass', 'berat']):
        return 'kg'
    
    # Temperature patterns
    if any(word in column_lower for word in ['temperature', 'temp', 'suhu']):
        return '°C'
    
    # Percentage patterns
    if any(word in column_lower for word in ['percentage', 'percent', 'persentase', 'persen', '%']):
        return '%'
    
    # Rainfall patterns
    if any(word in column_lower for word in ['rainfall', 'rain', 'curah', 'hujan']):
        return 'mm'
    
    # Velocity/Speed patterns
    if any(word in column_lower for word in ['velocity', 'speed', 'kecepatan']):
        return 'km/h'
    
    # Density patterns
    if any(word in column_lower for word in ['density', 'densitas']):
        return 'persons/km²'
    
    return None
