"""
Teoría del color inspirada en la Bauhaus
"""
class ColorTheory:
    def __init__(self):
        self.primary_colors = ['red', 'blue', 'yellow']
        self.secondary_colors = ['orange', 'green', 'purple']
        self.harmony_types = ['complementary', 'analogous', 'triadic', 'monochromatic']
    
    def analyze_color_psychology(self, color):
        """
        Analiza la psicología del color según la Bauhaus
        
        Args:
            color: Color a analizar
        
        Returns:
            Dict con análisis psicológico
        """
        color_psychology = {
            'red': {'energy': 'high', 'mood': 'passion', 'use': 'accent'},
            'blue': {'energy': 'calm', 'mood': 'serenity', 'use': 'walls'},
            'yellow': {'energy': 'medium', 'mood': 'happiness', 'use': 'highlights'},
            'orange': {'energy': 'medium', 'mood': 'creativity', 'use': 'accent'},
            'green': {'energy': 'calm', 'mood': 'balance', 'use': 'nature_spaces'},
            'purple': {'energy': 'low', 'mood': 'luxury', 'use': 'details'},
            'white': {'energy': 'neutral', 'mood': 'purity', 'use': 'expansion'},
            'black': {'energy': 'neutral', 'mood': 'elegance', 'use': 'contrast'},
            'gray': {'energy': 'neutral', 'mood': 'neutrality', 'use': 'background'}
        }
        
        return color_psychology.get(color.lower(), {'energy': 'variable', 'mood': 'neutral', 'use': 'versatile'})
    
    def create_color_harmony(self, base_color, harmony_type='complementary'):
        """
        Crea una armonía de colores
        
        Args:
            base_color: Color base
            harmony_type: Tipo de armonía
        
        Returns:
            Lista de colores armónicos
        """
        if harmony_type not in self.harmony_types:
            raise ValueError("Tipo de armonía no válido")
        
        color_palettes = {
            'red': {
                'complementary': ['red', 'green'],
                'analogous': ['red', 'red-orange', 'red-purple'],
                'triadic': ['red', 'blue', 'yellow'],
                'monochromatic': ['red', 'maroon', 'pink']
            },
            'blue': {
                'complementary': ['blue', 'orange'],
                'analogous': ['blue', 'blue-green', 'blue-purple'],
                'triadic': ['blue', 'red', 'yellow'],
                'monochromatic': ['blue', 'navy', 'skyblue']
            },
            'yellow': {
                'complementary': ['yellow', 'purple'],
                'analogous': ['yellow', 'yellow-green', 'yellow-orange'],
                'triadic': ['yellow', 'blue', 'red'],
                'monochromatic': ['yellow', 'gold', 'lemon']
            }
        }
        
        return color_palettes.get(base_color, {}).get(harmony_type, [base_color])