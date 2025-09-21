"""
Geometría espacial inspirada en la Bauhaus
"""
class BauhausGeometry:
    def __init__(self):
        self.grid_types = ['modular', 'radial', 'axial']
    
    def create_modular_grid(self, width, height, module_size):
        """
        Crea una retícula modular con puntos de grid
        
        Args:
            width: Ancho total
            height: Alto total
            module_size: Tamaño del módulo
        
        Returns:
            Dict con información del grid y puntos
        """
        columns = int(width / module_size)
        rows = int(height / module_size)
        
        # Generar puntos de la retícula
        grid_points = []
        for x in range(columns + 1):
            for y in range(rows + 1):
                grid_points.append({
                    'x': x * module_size,
                    'y': y * module_size,
                    'z': 0.0
                })
        
        return {
            'columns': columns,
            'rows': rows,
            'module_size': module_size,
            'grid_points': grid_points,
            'total_points': len(grid_points),
            'grid_type': 'modular'
        }
    
    def calculate_proportions(self, dimensions, proportion_type='golden'):
        """
        Calcula proporciones áureas o modulares
        
        Args:
            dimensions: Dimensiones originales
            proportion_type: Tipo de proporción
        
        Returns:
            Dimensiones proporcionales
        """
        if proportion_type == 'golden':
            ratio = 1.618
        elif proportion_type == 'modular':
            ratio = 1.5
        else:
            ratio = 1.0
        
        return {
            'width': dimensions['width'] * ratio,
            'height': dimensions['height'] / ratio,
            'depth': dimensions.get('depth', 0) * ratio,
            'proportion_type': proportion_type
        }