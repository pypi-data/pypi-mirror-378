import pytest
from src.bauhaus_design_kit.form_functions import BauhausForms

def test_optimize_living_room():
    """Test para optimización de espacio living"""
    form_tool = BauhausForms()
    result = form_tool.optimize_living_space(20.0, "living")
    
    assert result['total_area'] == 20.0
    assert result['space_type'] == "living"
    assert result['furniture_area'] == 8.0  # 40% de 20
    assert result['circulation_area'] == 6.0  # 30% de 20
    assert result['free_area'] == 6.0  # 30% de 20

def test_invalid_space_type():
    """Test para tipo de espacio inválido"""
    form_tool = BauhausForms()
    with pytest.raises(ValueError):
        form_tool.optimize_living_space(20.0, "invalid_type")

# Tests movidos desde spatial_geometry
def test_primary_forms_cube():
    """Test para formas primarias - cubo"""
    form_tool = BauhausForms()
    cube = form_tool.create_primary_form("cube", {"side": 2.0})
    
    assert cube['form_type'] == "cube"
    assert cube['volume'] == 8.0  # 2^3
    assert cube['surface_area'] == 24.0  # 6 * 4

def test_primary_forms_sphere():
    """Test para formas primarias - esfera"""
    form_tool = BauhausForms()
    sphere = form_tool.create_primary_form("sphere", {"radius": 1.0})
    
    assert sphere['form_type'] == "sphere"
    assert pytest.approx(sphere['volume'], 0.01) == 4.1888  # 4/3 * π * r³
    assert pytest.approx(sphere['surface_area'], 0.01) == 12.5664  # 4 * π * r²

def test_invalid_form_type():
    """Test para tipo de forma inválido"""
    form_tool = BauhausForms()
    with pytest.raises(ValueError):
        form_tool.create_primary_form("invalid_form", {"side": 1.0})