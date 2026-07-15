#!/usr/bin/env python3
"""
Create a test Excel file for testing
"""
import pandas as pd
from pathlib import Path

# Create test data
data = {
    'dusun': ['Kelodan', 'Padang', 'Simpang', 'Tembuku'],
    'population': [516, 835, 420, 680],
    'water_access': ['partial', 'full', 'none', 'partial'],
    'distance': [5.2, 12.3, 8.1, 3.5]
}

df = pd.DataFrame(data)

# Save to Excel
output_file = Path('/home/ahmed/Bureau/stage project/test_data_stage/simple_test.xlsx')
df.to_excel(output_file, index=False, sheet_name='Data')

print(f"✅ Created Excel file: {output_file}")
print(f"\nContent:")
print(df)
print(f"\nDataTypes:")
print(df.dtypes)
