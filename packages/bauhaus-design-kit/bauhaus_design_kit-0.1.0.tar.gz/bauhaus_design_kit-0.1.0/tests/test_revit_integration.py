import pytest
from src.bauhaus_design_kit.revit_integration import RevitIntegration

def test_integration_all_modules():
    """Test para integración de todos los módulos"""
    revit_tool = RevitIntegration()
    design_data = {
        'elements': [
            {'type': 'wall', 'parameters': {'length': 5.0, 'height': 3.0}},
            {'type': 'window', 'parameters': {'width': 1.2, 'height': 1.5}}
        ]
    }
    
    result = revit_tool.export_to_revit(design_data, "2024")
    
    assert result['success'] == True
    assert result['exported_elements'] == 2
    assert result['revit_version'] == "2024"

def test_complete_design_workflow():
    """Test para workflow completo de diseño"""
    revit_tool = RevitIntegration()
    space_data = {'total_area': 25.0, 'elements': []}
    color_scheme = {'colors': ['red', 'blue', 'yellow']}
    furniture_layout = {'total_area': 15.0, 'circulation_area': 5.0}
    
    workflow = revit_tool.create_design_workflow(space_data, color_scheme, furniture_layout)
    
    assert workflow['revit_ready'] == True
    assert 'workflow_id' in workflow
    assert len(workflow['validation_checks']) == 4