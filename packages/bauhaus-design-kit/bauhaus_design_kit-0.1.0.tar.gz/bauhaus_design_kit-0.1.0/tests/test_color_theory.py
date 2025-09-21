import pytest
from src.bauhaus_design_kit.color_theory import ColorTheory

def test_color_psychology():
    """Test para psicología del color"""
    color_tool = ColorTheory()
    result = color_tool.analyze_color_psychology("red")
    
    assert result['energy'] == 'high'
    assert result['mood'] == 'passion'
    assert result['use'] == 'accent'

def test_color_harmony():
    """Test para armonía de colores"""
    color_tool = ColorTheory()
    harmony = color_tool.create_color_harmony("red", "complementary")
    
    assert len(harmony) == 2
    assert "red" in harmony
    assert "green" in harmony

def test_invalid_harmony_type():
    """Test para tipo de armonía inválido"""
    color_tool = ColorTheory()
    with pytest.raises(ValueError):
        color_tool.create_color_harmony("red", "invalid_harmony")