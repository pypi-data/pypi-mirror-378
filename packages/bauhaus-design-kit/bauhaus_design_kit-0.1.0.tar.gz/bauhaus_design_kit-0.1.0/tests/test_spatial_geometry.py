import pytest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bauhaus_design_kit.spatial_geometry import BauhausGeometry

def test_modular_grid():
    """Test para creación de retícula modular"""
    geometry_tool = BauhausGeometry()
    grid = geometry_tool.create_modular_grid(5.0, 4.0, 1.0)
    
    assert grid['columns'] == 5
    assert grid['rows'] == 4
    assert grid['module_size'] == 1.0
    assert len(grid['grid_points']) == 30  # (5+1) * (4+1)
    assert grid['grid_type'] == 'modular'
    
