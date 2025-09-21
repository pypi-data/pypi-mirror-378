"""
Módulo de funciones de forma inspiradas en la Bauhaus
"""
class BauhausForms:
    def __init__(self):
        self.primary_forms = ['cube', 'sphere', 'cylinder', 'cone', 'pyramid']
    
    def optimize_living_space(self, area, space_type="living"):
        """
        Optimiza el espacio según principios de la Bauhaus
        
        Args:
            area: Área total del espacio
            space_type: Tipo de espacio (living, kitchen, bedroom)
        
        Returns:
            Dict con la configuración optimizada
        """
        if space_type not in ["living", "kitchen", "bedroom", "bathroom"]:
            raise ValueError("Tipo de espacio no válido")
        
        # Cálculos basados en proporciones de la Bauhaus
        if space_type == "living":
            furniture_area = area * 0.4
            circulation_area = area * 0.3
            free_area = area * 0.3
        elif space_type == "kitchen":
            furniture_area = area * 0.6
            circulation_area = area * 0.25
            free_area = area * 0.15
        else:  # bedroom/bathroom
            furniture_area = area * 0.7
            circulation_area = area * 0.2
            free_area = area * 0.1
        
        return {
            'total_area': area,
            'space_type': space_type,
            'furniture_area': round(furniture_area, 2),
            'circulation_area': round(circulation_area, 2),
            'free_area': round(free_area, 2),
            'efficiency_ratio': round(free_area / area, 2)
        }
    
    def create_primary_form(self, form_type, dimensions):
        """
        Crea una forma primaria básica
        
        Args:
            form_type: Tipo de forma (cube, sphere, cylinder, cone, pyramid)
            dimensions: Dimensiones de la forma
        
        Returns:
            Dict con información de la forma
        """
        if form_type not in self.primary_forms:
            raise ValueError("Tipo de forma no válido")
        
        return {
            'form_type': form_type,
            'dimensions': dimensions,
            'volume': self._calculate_volume(form_type, dimensions),
            'surface_area': self._calculate_surface_area(form_type, dimensions)
        }
    
    def _calculate_volume(self, form_type, dimensions):
        """Calcula el volumen de la forma"""
        if form_type == "cube":
            return dimensions['side'] ** 3
        elif form_type == "sphere":
            return (4/3) * 3.1416 * (dimensions['radius'] ** 3)
        elif form_type == "cylinder":
            return 3.1416 * (dimensions['radius'] ** 2) * dimensions['height']
        elif form_type == "cone":
            return (1/3) * 3.1416 * (dimensions['radius'] ** 2) * dimensions['height']
        elif form_type == "pyramid":
            return (1/3) * dimensions['base_area'] * dimensions['height']
    
    def _calculate_surface_area(self, form_type, dimensions):
        """Calcula el área superficial"""
        if form_type == "cube":
            return 6 * (dimensions['side'] ** 2)
        elif form_type == "sphere":
            return 4 * 3.1416 * (dimensions['radius'] ** 2)
        elif form_type == "cylinder":
            return 2 * 3.1416 * dimensions['radius'] * (dimensions['radius'] + dimensions['height'])
        elif form_type == "cone":
            return 3.1416 * dimensions['radius'] * (dimensions['radius'] + 
                   (dimensions['height']**2 + dimensions['radius']**2)**0.5)
        elif form_type == "pyramid":
            return dimensions['base_area'] + dimensions['perimeter'] * dimensions['slant_height'] / 2